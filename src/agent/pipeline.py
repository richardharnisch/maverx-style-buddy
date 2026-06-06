"""Hybrid conversational pipeline orchestrator.

Drives one chat turn at a time:

1. **Intake** (OpenRouter) — accumulate the required training context, asking
   precise follow-ups on vague input, until complete.
2. **Lesson plan** (OpenRouter) — generate + schema-validate the normalized
   plan (see :mod:`src.agent.lesson_plan`).
3. **Build** (build backend) — hand the plan off to the configured backend
   (script today, Codex once installed) to produce the editable ``.pptx``.

State lives on the session's ``Session`` object (intake, status, assets, cost),
so the chat router stays a thin transport layer.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache

from src.agent.client import OpenRouterClient
from src.agent.lesson_plan import LessonPlanError, generate_training
from src.api.schemas.session import Session, SessionStatus
from src.build import BuildError, get_build_backend
from src.constants import (
    INTAKE_FIELDS,
    LESSON_PLAN_FILENAME,
    OUTPUT_DIR,
)

log = logging.getLogger(__name__)


@dataclass
class TurnResult:
    reply: str
    deck: dict | None = None  # matches the DeckArtifact schema when present


# Rough USD per 1M tokens (input, output) for cost reporting (criterion 7).
# Approximate — refine from the OpenRouter pricing page as needed.
_PRICING: dict[str, tuple[float, float]] = {
    "anthropic/claude-opus-4-8": (5.0, 25.0),
    "anthropic/claude-sonnet-4-6": (3.0, 15.0),
    "openai/gpt-5.5": (1.25, 10.0),
}
_DEFAULT_PRICING = (3.0, 15.0)


@lru_cache(maxsize=8)
def _client(model: str) -> OpenRouterClient:
    return OpenRouterClient(model=model)


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    in_rate, out_rate = _PRICING.get(model, _DEFAULT_PRICING)
    return (prompt_tokens * in_rate + completion_tokens * out_rate) / 1_000_000


# --- intake -----------------------------------------------------------------

_INTAKE_SYSTEM = """\
You are the Intake Agent for the Maverx Training Builder. Your only job is to \
collect the required context for a training before any content is generated. \
You do not generate slides.

You will be given the required fields, the answers gathered so far, and the \
trainer's latest message. Update the answers from the latest message. If an \
answer is vague (e.g. "a few hours", "some people", "make it good"), do NOT \
accept it — ask ONE precise follow-up and keep that field unfilled.

Return ONLY a JSON object:
{
  "answers": { "<field_key>": "<concise answer>", ... },   // all known answers
  "complete": true|false,                                   // all fields filled & specific
  "reply": "<one short, friendly message to the trainer>"
}
When not complete, `reply` acknowledges what you heard and asks for the single \
most important missing or vague item. When complete, `reply` briefly confirms \
you have what you need and that you're building the deck now.\
"""


def _intake_turn(
    session: Session, user_text: str, model: str
) -> tuple[bool, str, float]:
    complete, reply, cost, intake = run_intake(session.intake, user_text, model)
    session.intake = intake
    return complete, reply, cost


def run_intake(
    intake: dict[str, str], user_text: str, model: str
) -> tuple[bool, str, float, dict[str, str]]:
    """Session-agnostic intake turn. Returns (complete, reply, cost, new_intake).

    Used by both the chat pipeline and the track API so the conversational
    intake behaves identically everywhere.
    """
    fields = "\n".join(f"- {f['key']}: {f['question']}" for f in INTAKE_FIELDS)
    payload = {
        "required_fields": [f["key"] for f in INTAKE_FIELDS],
        "answers_so_far": intake,
        "latest_message": user_text,
    }
    messages = [
        {"role": "system", "content": _INTAKE_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Required fields and their questions:\n{fields}\n\n"
                f"Current state (JSON):\n{json.dumps(payload, ensure_ascii=False)}"
            ),
        },
    ]
    resp = _client(model).chat(messages, response_format={"type": "json_object"})
    cost = _usage_cost(resp, model)
    raw = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(raw[raw.find("{") : raw.rfind("}") + 1])
    except json.JSONDecodeError:
        return False, "Sorry, could you rephrase that?", cost, intake

    new_intake = dict(intake)
    answers = data.get("answers") or {}
    if isinstance(answers, dict):
        keys = {f["key"] for f in INTAKE_FIELDS}
        new_intake = {
            k: str(v).strip()
            for k, v in answers.items()
            if k in keys and str(v).strip()
        }
    have_all = {f["key"] for f in INTAKE_FIELDS} <= set(new_intake)
    complete = bool(data.get("complete")) and have_all
    reply = str(data.get("reply") or "").strip() or "Could you tell me more?"
    return complete, reply, cost, new_intake


def _usage_cost(resp, model: str) -> float:
    usage = getattr(resp, "usage", None)
    if not usage:
        return 0.0
    return _estimate_cost(
        model,
        getattr(usage, "prompt_tokens", 0) or 0,
        getattr(usage, "completion_tokens", 0) or 0,
    )


# --- build ------------------------------------------------------------------

@dataclass
class TrainingBuild:
    """Outcome of generating + building a full training (any tier)."""

    plan: dict
    scope: str
    result: object  # BuildResult
    cost_usd: float


def build_training(
    intake: dict[str, str], language: str, out_dir, model: str
) -> TrainingBuild:
    """Generate a tier-appropriate plan and build all its artifacts into out_dir.

    The shared engine behind both the chat pipeline and the track API.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    plan, prompt_tokens, completion_tokens, scope = generate_training(
        _client(model), intake, language
    )
    cost = _estimate_cost(model, prompt_tokens, completion_tokens)
    plan_path = out_dir / LESSON_PLAN_FILENAME
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), "utf-8")
    result = get_build_backend().build(plan_path, out_dir)
    return TrainingBuild(plan=plan, scope=scope, result=result, cost_usd=cost)


def _generate_and_build(session: Session, model: str) -> TurnResult:
    out_dir = OUTPUT_DIR / session.id
    build = build_training(session.intake, session.language, out_dir, model)
    plan, result, scope = build.plan, build.result, build.scope

    session.generation_cost_usd = (session.generation_cost_usd or 0.0) + build.cost_usd
    deck = result.primary_deck
    session.assets = [str(p) for p in result.deck_paths + result.doc_paths]
    session.outline = plan
    session.confidence_scores = _block_confidence(plan)
    session.status = SessionStatus.ready

    deck_artifact = {
        "deck_id": session.id,
        "filename": deck.name if deck else "deck.pptx",
        "slide_count": result.slide_count,
        "download_url": f"/sessions/{session.id}/files/{deck.name}"
        if deck
        else None,
    }

    return TurnResult(
        reply=_build_summary(plan, result, scope, session), deck=deck_artifact
    )


_SCOPE_LABEL = {
    "single_session": "single training",
    "multi_session": "3-level module",
    "certification": "certification track",
}


def _build_summary(plan: dict, result, scope: str, session: Session) -> str:
    training = plan.get("training", {})
    title = training.get("title", "your training")
    n_decks = len(result.deck_paths)

    if n_decks > 1:
        head = (
            f"✅ Built **{title}** — a {_SCOPE_LABEL.get(scope, scope)} of "
            f"{n_decks} decks ({result.slide_count} slides total) in Maverx "
            f"house style ({session.language})."
        )
    else:
        head = (
            f"✅ Built **{title}** — a {result.slide_count}-slide editable deck "
            f"in Maverx house style ({session.language})."
        )
    lines = [head]

    docs = [p.name for p in result.doc_paths]
    if docs:
        shown = ", ".join(docs[:6]) + (" …" if len(docs) > 6 else "")
        lines.append(f"Also generated: {shown}.")

    flagged = sum(
        1
        for s in plan.get("sessions", [])
        for slide in s.get("deck_outline", [])
        if slide.get("reliability", {}).get("review_priority") == "high"
    )
    if flagged:
        lines.append(f"⚠️ {flagged} slide(s) flagged for closer review.")
    if session.generation_cost_usd is not None:
        lines.append(f"Approx. generation cost: ${session.generation_cost_usd:.4f}.")
    lines.extend(result.notes)
    lines.append("Use the download button on the right to open the deck.")
    return "\n\n".join(lines)


def _block_confidence(plan: dict) -> dict[str, float]:
    """Average reliability score per didactic block across all sessions (criterion 6)."""
    scores: dict[str, list[float]] = {}
    for sess in plan.get("sessions", []):
        for slide in sess.get("deck_outline", []):
            block = slide.get("didactic_block")
            score = slide.get("reliability", {}).get("score")
            if block and isinstance(score, (int, float)):
                scores.setdefault(block, []).append(float(score))
    return {b: round(sum(v) / len(v), 3) for b, v in scores.items() if v}


# --- public entry point -----------------------------------------------------

def handle_turn(session: Session, user_text: str, model: str) -> TurnResult:
    """Advance the pipeline by one chat turn and return the assistant reply."""
    try:
        complete, reply, cost = _intake_turn(session, user_text, model)
        session.generation_cost_usd = (session.generation_cost_usd or 0.0) + cost

        if not complete:
            session.status = SessionStatus.intake
            return TurnResult(reply=reply)

        session.status = SessionStatus.generating
        result = _generate_and_build(session, model)
        return TurnResult(
            reply=f"{reply}\n\n{result.reply}", deck=result.deck
        )

    except (LessonPlanError, BuildError) as exc:
        session.status = SessionStatus.error
        session.error = str(exc)
        log.exception("Pipeline failed for session %s", session.id)
        return TurnResult(reply=f"⚠️ Generation failed: {exc}")
    except Exception as exc:  # provider/network/unexpected
        session.status = SessionStatus.error
        session.error = str(exc)
        log.exception("Unexpected pipeline error for session %s", session.id)
        return TurnResult(
            reply=f"⚠️ Something went wrong while building your deck: {exc}"
        )
