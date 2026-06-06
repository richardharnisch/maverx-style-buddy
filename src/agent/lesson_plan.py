"""Generate and validate a Maverx ``lesson_plan.json`` via OpenRouter.

This is the "Normalized Lesson Plan" step from the design sketch: it turns the
collected intake into one schema-valid lesson plan that the build backend can
consume. Generation is a single structured (JSON) OpenRouter call against the
real ``lesson_plan.schema.json``, followed by a deterministic reconcile pass
(timing, slide numbering, capacity) and a schema-validation repair loop.

Tier 1 (single session) is the baseline. Breaks/handouts are off by default and
the deck is capped to the bundled template deck's capacity so the deterministic
builder always succeeds; see ``MAX_CONTENT_SLIDES``.
"""

from __future__ import annotations

import json
import logging
import math
import re
from functools import lru_cache
from typing import Any

import jsonschema

from src.agent.client import OpenRouterClient
from src.constants import (
    LESSON_PLAN_MAX_REPAIRS,
    LESSON_PLAN_SCHEMA_PATH,
    ORDERED_BLOCKS,
)

log = logging.getLogger(__name__)

# The builder now clones slides, so a deck can reuse templates without limit.
# Cap only to keep one-shot generation reliable and within the doc's 30-50 range.
MAX_CONTENT_SLIDES = 45
MIN_CONTENT_SLIDES = 10  # lesson_plan.schema.json deck_outline minItems

# Output budget for a full lesson-plan JSON (≈150 tokens/slide + arc + bites).
GENERATION_MAX_TOKENS = 16000


class LessonPlanError(RuntimeError):
    """Raised when a valid lesson plan cannot be produced."""


@lru_cache(maxsize=1)
def _schema() -> dict[str, Any]:
    return json.loads(LESSON_PLAN_SCHEMA_PATH.read_text(encoding="utf-8"))


def _schema_errors(plan: dict[str, Any]) -> list[str]:
    validator = jsonschema.Draft7Validator(_schema())
    errors = []
    for err in sorted(validator.iter_errors(plan), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    return errors


_SYSTEM_PROMPT = f"""\
You are the Maverx Didactic Lesson Planner. Produce ONE JSON object that \
conforms to the provided JSON Schema for a Maverx training lesson plan. Output \
ONLY the JSON object, no prose, no markdown fences.

Non-negotiable didactic structure — every session's `didactic_arc` must contain \
exactly these five blocks, in this order: {", ".join(ORDERED_BLOCKS)}. Each block \
needs a learning_purpose, trainer_actions, participant_actions, content_outline, \
learning_check, and a time_min. The five `time_min` values MUST sum to the \
session's `duration_min`.

Deck outline rules:
- Aim for roughly ceil(session_minutes / 3) content slides, clamped to between \
{MIN_CONTENT_SLIDES} and {MAX_CONTENT_SLIDES}. Distribute them across the five \
blocks in proportion to each block's time; theory and exercise get the most.
- Slide 1 is the deck title slide. Number slides sequentially from 1.
- CONTENT DEPTH (important): every content slide must be substantive, not a \
placeholder. `key_message` is one full, specific sentence stating the single \
idea of the slide. `suggested_content` is 3-5 concrete bullets a trainer could \
present as-is — real examples, steps, numbers, do/don't contrasts, or a worked \
mini-case relevant to the audience. Avoid vague filler like "discuss the topic" \
or "key points". Each bullet ≤ 18 words.
- Vary slides: openers pose a question, theory slides explain one concept each, \
example slides show a concrete recognizable case, exercise slides give clear \
participant instructions and a deliverable.
- Every slide needs a `reliability` object: score (0-1), rationale, \
review_priority (low/medium/high). Score well-grounded content high (>=0.85) \
and audience-dependent or uncertain content lower (<0.75) with higher review \
priority — be honest so the trainer knows what to check.
- Do NOT include break or handout slides unless explicitly required.

Pre-bite and post-bite must be genuinely useful: a concrete participant_task \
(something to read, install, watch, or reflect on with a clear prompt) and at \
least one real, specific resource with a plausible URL or reference and a reason \
it's included. No generic "read about the topic".

Other requirements:
- `training.scope` = "single_session", `training.total_sessions` = 1.
- `intake_summary.include_breaks` = false and `include_handouts` = false.
- `research_evidence`: at least 2 real, citable sources with URLs relevant to \
the topic; set evidence_strength honestly.
- Fill `validation` with your honest self-assessment booleans and any issues.
- Generate ALL human-readable text (titles, content, briefs, bites, speaker \
guidance) in the target language specified by the user.
"""


def _user_prompt(intake: dict[str, str], language: str) -> str:
    intake_lines = "\n".join(f"- {k}: {v}" for k, v in intake.items())
    return (
        f"Target output language: {language}\n\n"
        f"Intake context:\n{intake_lines}\n\n"
        "Build a single-session Maverx training lesson plan from this intake. "
        "Here is the exact JSON Schema your output must satisfy:\n\n"
        f"{json.dumps(_schema())}"
    )


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
        text = text.lstrip()
        if text[:4].lower() == "json":
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise LessonPlanError("Model response contained no JSON object.")
    candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Tolerate the most common LLM slip: trailing commas before } or ].
        repaired = re.sub(r",(\s*[}\]])", r"\1", candidate)
        return json.loads(repaired)  # may still raise; callers handle it


def _reconcile(plan: dict[str, Any]) -> dict[str, Any]:
    """Deterministically fix the things LLMs reliably get slightly wrong:
    Tier-1 invariants, slide numbering, deck capacity, and arc timing sums."""
    training = plan.setdefault("training", {})
    training["scope"] = "single_session"
    training["total_sessions"] = 1

    sessions = plan.get("sessions") or []
    if not sessions:
        raise LessonPlanError("Plan has no sessions.")
    plan["sessions"] = sessions[:1]  # Tier 1 = single session
    session = sessions[0]
    session["session_n"] = 1

    duration = session.get("duration_min") or training.get("total_minutes") or 60
    session["duration_min"] = duration
    training["total_minutes"] = duration

    _reconcile_arc_timing(session, duration)
    _reconcile_deck(session)
    _reconcile_validation(plan)
    return plan


def _reconcile_arc_timing(session: dict[str, Any], duration: int) -> None:
    arc = session.get("didactic_arc") or []
    if len(arc) != len(ORDERED_BLOCKS):
        return  # structural problem; let schema validation surface it
    for block, name in zip(arc, ORDERED_BLOCKS):
        block["block"] = name
        if not isinstance(block.get("time_min"), int) or block["time_min"] < 1:
            block["time_min"] = 1
    total = sum(b["time_min"] for b in arc)
    diff = duration - total
    if diff != 0:
        # Adjust the theory block (index 1) to make the sum exact.
        idx = 1
        arc[idx]["time_min"] = max(1, arc[idx]["time_min"] + diff)
        # If that still doesn't balance (e.g. clamped at 1), spread onto others.
        total = sum(b["time_min"] for b in arc)
        if total != duration:
            arc[-1]["time_min"] = max(1, arc[-1]["time_min"] + (duration - total))


def _reconcile_deck(session: dict[str, Any]) -> None:
    deck = session.get("deck_outline") or []
    # Drop breaks/handouts for the Tier-1 baseline so the builder stays simple.
    content = [s for s in deck if s.get("slide_type", "content") == "content"]
    content = content[:MAX_CONTENT_SLIDES]
    content = _fit_deck_to_templates(content)
    for n, slide in enumerate(content, start=1):
        slide["slide_n"] = n
        slide.setdefault("slide_type", "content")
    session["deck_outline"] = content
    session.pop("handout", None)


def _fit_deck_to_templates(deck: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Trim the deck so the deterministic builder can assign a unique template
    to every slide. Drops slides from the most-represented block first to keep
    the didactic arc balanced. Falls back to the input deck if the builder can't
    be loaded (e.g. Codex backend), letting schema/build validation surface it.
    """
    try:
        from src.build.builder_module import load_builder

        choose_templates = load_builder().choose_templates
    except Exception:  # builder unavailable — don't block generation
        return deck

    work = list(deck)
    while len(work) > MIN_CONTENT_SLIDES:
        try:
            choose_templates(work)
            return work
        except ValueError:
            work = _drop_largest_block_slide(work)
    return work  # at the schema minimum; build will validate the rest


def _drop_largest_block_slide(deck: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for slide in deck:
        counts[slide.get("didactic_block", "")] = (
            counts.get(slide.get("didactic_block", ""), 0) + 1
        )
    target_block = max(counts, key=counts.get)
    # Remove the last slide of that block, but never slide 1 (the title slide).
    for i in range(len(deck) - 1, 0, -1):
        if deck[i].get("didactic_block") == target_block:
            return deck[:i] + deck[i + 1 :]
    return deck[:-1]


def _reconcile_validation(plan: dict[str, Any]) -> None:
    session = plan["sessions"][0]
    deck = session.get("deck_outline", [])
    non_break = sum(1 for s in deck if s.get("slide_type") != "break")
    density_ok = non_break >= math.ceil(session.get("duration_min", 0) / 3)
    plan["validation"] = {
        "schema_validated": True,
        "didactic_arc_verified": len(session.get("didactic_arc", [])) == 5,
        "timing_verified": True,
        "slide_density_verified": density_ok,
        "research_used": bool(plan.get("research_evidence")),
        "issues": []
        if density_ok
        else [
            "Deck capped to template-deck capacity; below the ceil(duration/3) "
            "density guideline for this duration."
        ],
    }


def generate_lesson_plan(
    client: OpenRouterClient,
    intake: dict[str, str],
    language: str,
) -> tuple[dict[str, Any], int, int]:
    """Generate, reconcile, and schema-validate a lesson plan. Repairs on error.

    Returns ``(plan, prompt_tokens, completion_tokens)`` so the caller can
    account for generation cost.
    """
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": _user_prompt(intake, language)},
    ]

    plan: dict[str, Any] | None = None
    prompt_tokens = completion_tokens = 0
    for attempt in range(LESSON_PLAN_MAX_REPAIRS + 1):
        try:
            resp = client.chat(
                messages,
                response_format={"type": "json_object"},
                max_tokens=GENERATION_MAX_TOKENS,
            )
        except Exception as exc:  # network / provider error
            raise LessonPlanError(f"Lesson plan generation failed: {exc}") from exc

        usage = getattr(resp, "usage", None)
        if usage:
            prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            completion_tokens += getattr(usage, "completion_tokens", 0) or 0
        content = resp.choices[0].message.content or ""
        try:
            plan = _reconcile(_extract_json(content))
        except (json.JSONDecodeError, LessonPlanError) as exc:
            errors = [str(exc)]
        else:
            errors = _schema_errors(plan)
            if not errors:
                log.info("Lesson plan valid after %d attempt(s)", attempt + 1)
                return plan, prompt_tokens, completion_tokens

        if attempt < LESSON_PLAN_MAX_REPAIRS:
            log.warning(
                "Lesson plan invalid (attempt %d): %s", attempt + 1, errors[:5]
            )
            messages.append({"role": "assistant", "content": content})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "That JSON did not validate. Fix ONLY these schema "
                        "errors and return the full corrected JSON object:\n"
                        + "\n".join(f"- {e}" for e in errors[:20])
                    ),
                }
            )

    raise LessonPlanError(
        "Could not produce a schema-valid lesson plan after "
        f"{LESSON_PLAN_MAX_REPAIRS + 1} attempts. Last errors: {errors[:5]}"
    )


# --- multi-session: Tier 2 (module) & Tier 3 (certification track) ----------

# Cap how many full decks one request will generate (cost/time guard).
MAX_TRACK_SESSIONS = 8

_STRUCTURE_SYSTEM = """\
You analyze a training intake and decide its structure. Choose one scope:
- "single_session": a single standalone training.
- "multi_session": a 3-level module (Essentials / Advanced / Expert) where each \
level builds on the previous one.
- "certification": a multi-session certification track with a coherent running \
case and a framework backbone (e.g. DMAIC), where sessions build on each other.

Return ONLY this JSON:
{
  "scope": "single_session" | "multi_session" | "certification",
  "training_title": "<short title>",
  "certification_name": "<only for certification, else empty>",
  "running_case": "<only for certification: a consistent fictional company/problem>",
  "framework": "<optional backbone, e.g. DMAIC>",
  "sessions": [
    {"session_n": 1, "title": "...", "focus": "<what this session covers>",
     "minutes": <int>, "level_or_phase": "<Essentials/Advanced/Expert or phase>",
     "builds_on": "<what prior knowledge it assumes>"}
  ]
}
Infer session count and durations from the intake. Use 3 sessions for \
multi_session; use the stated count for certification (max 8). Keep minutes \
realistic (e.g. 90-180). For single_session, return exactly one session.\
"""


def _single_session_structure(intake: dict[str, str]) -> dict[str, Any]:
    """Safe default: treat the request as one standalone training."""
    title = intake.get("topic") or "Training"
    return {
        "scope": "single_session",
        "training_title": title,
        "sessions": [
            {
                "session_n": 1,
                "title": title,
                "focus": intake.get("primary_objective", ""),
                "minutes": 120,
            }
        ],
    }


def _normalize_structure(data: dict[str, Any], intake: dict[str, str]) -> dict[str, Any]:
    scope = data.get("scope", "single_session")
    if scope not in {"single_session", "multi_session", "certification"}:
        scope = "single_session"
    data["scope"] = scope
    sessions = data.get("sessions") or []
    if not sessions:
        sessions = _single_session_structure(intake)["sessions"]
    data["sessions"] = sessions[:MAX_TRACK_SESSIONS]
    return data


def _structure(
    client: OpenRouterClient, intake: dict[str, str], language: str
) -> tuple[dict[str, Any], int, int]:
    """Detect the training tier. Resilient: retries once on a bad JSON response
    and falls back to single_session rather than failing the whole pipeline."""
    intake_lines = "\n".join(f"- {k}: {v}" for k, v in intake.items())
    messages = [
        {"role": "system", "content": _STRUCTURE_SYSTEM},
        {"role": "user", "content": f"Target language: {language}\n\nIntake:\n{intake_lines}"},
    ]
    prompt_tokens = completion_tokens = 0
    for attempt in range(2):
        try:
            resp = client.chat(
                messages, response_format={"type": "json_object"}, max_tokens=1500
            )
        except Exception as exc:  # network/provider — fall back to single session
            log.warning("Structure call failed: %s", exc)
            break
        usage = getattr(resp, "usage", None)
        if usage:
            prompt_tokens += getattr(usage, "prompt_tokens", 0) or 0
            completion_tokens += getattr(usage, "completion_tokens", 0) or 0
        content = resp.choices[0].message.content or "{}"
        try:
            data = _normalize_structure(_extract_json(content), intake)
            return data, prompt_tokens, completion_tokens
        except (json.JSONDecodeError, LessonPlanError) as exc:
            log.warning("Structure JSON invalid (attempt %d): %s", attempt + 1, exc)
            messages.append({"role": "assistant", "content": content})
            messages.append(
                {
                    "role": "user",
                    "content": "That was not valid JSON. Return ONLY a single, "
                    "valid, minified JSON object — no prose, no code fences, no "
                    "trailing commas.",
                }
            )
    log.warning("Structure detection falling back to single_session.")
    return _single_session_structure(intake), prompt_tokens, completion_tokens


def _session_intake(
    intake: dict[str, str], structure: dict[str, Any], spec: dict[str, Any], total: int
) -> dict[str, str]:
    """Augment the base intake with this session's place in the programme so the
    reused single-session generator produces coherent, progressive content."""
    parts = [
        f"{intake.get('primary_objective', '')}",
        f"This is session {spec.get('session_n')} of {total}: \"{spec.get('title')}\" "
        f"— focus on {spec.get('focus', '')}.",
    ]
    if spec.get("level_or_phase"):
        parts.append(f"Level/phase: {spec['level_or_phase']}.")
    if spec.get("builds_on"):
        parts.append(f"Assumes prior knowledge: {spec['builds_on']}.")
    if structure.get("running_case"):
        parts.append(f"Use this consistent running case throughout: {structure['running_case']}.")
    if structure.get("framework"):
        parts.append(f"Framework backbone: {structure['framework']}.")
    sub = dict(intake)
    sub["primary_objective"] = " ".join(p for p in parts if p.strip())
    if spec.get("minutes"):
        sub["duration"] = f"{int(spec['minutes'])} minutes"
    return sub


def generate_track(
    client: OpenRouterClient,
    intake: dict[str, str],
    language: str,
    structure: dict[str, Any],
) -> tuple[dict[str, Any], int, int]:
    """Generate a multi-session plan by producing each session with the proven
    single-session generator, then stitching them into one track plan."""
    specs = structure["sessions"]
    total = len(specs)
    prompt_tokens = completion_tokens = 0
    sub_plans: list[dict[str, Any]] = []

    for index, spec in enumerate(specs, start=1):
        sub_intake = _session_intake(intake, structure, spec, total)
        plan, p_tok, c_tok = generate_lesson_plan(client, sub_intake, language)
        prompt_tokens += p_tok
        completion_tokens += c_tok
        session = plan["sessions"][0]
        session["session_n"] = index
        if spec.get("title"):
            session["title"] = spec["title"][:120]
        sub_plans.append(plan)
        log.info("Track session %d/%d generated: %s", index, total, session["title"])

    plan = _assemble_track(sub_plans, structure)
    errors = _schema_errors(plan)
    if errors:
        raise LessonPlanError(f"Assembled track failed schema validation: {errors[:5]}")
    return plan, prompt_tokens, completion_tokens


def _assemble_track(sub_plans: list[dict[str, Any]], structure: dict[str, Any]) -> dict[str, Any]:
    base = sub_plans[0]
    sessions = [p["sessions"][0] for p in sub_plans]
    base["sessions"] = sessions

    scope = structure["scope"]
    base["training"]["scope"] = scope
    base["training"]["title"] = structure.get("training_title") or base["training"]["title"]
    base["training"]["total_sessions"] = len(sessions)
    base["training"]["total_minutes"] = sum(s["duration_min"] for s in sessions)

    # Reflect the track shape in intake_summary.
    summary = base["intake_summary"]
    summary["duration"] = {
        "sessions": len(sessions),
        "minutes_per_session": sessions[0]["duration_min"],
    }
    if scope == "certification" and structure.get("certification_name"):
        summary["certification_name"] = structure["certification_name"]

    # Merge research evidence (dedup by URL) and programme outcomes across sessions.
    seen: set[str] = set()
    research: list[dict[str, Any]] = []
    outcomes: list[str] = []
    for plan in sub_plans:
        for evidence in plan.get("research_evidence", []):
            key = evidence.get("source_url", "")
            if key and key not in seen:
                seen.add(key)
                research.append(evidence)
        outcomes.extend(plan.get("programme_learning_outcomes", []))
    if research:
        base["research_evidence"] = research
    base["programme_learning_outcomes"] = list(dict.fromkeys(outcomes))[:10] or base[
        "programme_learning_outcomes"
    ]

    base["validation"] = {
        "schema_validated": True,
        "didactic_arc_verified": all(len(s.get("didactic_arc", [])) == 5 for s in sessions),
        "timing_verified": True,
        "slide_density_verified": all(
            len(s.get("deck_outline", [])) >= MIN_CONTENT_SLIDES for s in sessions
        ),
        "research_used": bool(base.get("research_evidence")),
        "issues": [],
    }
    return base


def generate_training(
    client: OpenRouterClient, intake: dict[str, str], language: str
) -> tuple[dict[str, Any], int, int, str]:
    """Unified entry point. Detects the tier (single / module / certification),
    generates the appropriate plan, and returns it with token usage and scope."""
    structure, s_pt, s_ct = _structure(client, intake, language)
    scope = structure["scope"]
    if scope == "single_session":
        plan, pt, ct = generate_lesson_plan(client, intake, language)
        return plan, s_pt + pt, s_ct + ct, "single_session"
    plan, pt, ct = generate_track(client, intake, language, structure)
    return plan, s_pt + pt, s_ct + ct, scope
