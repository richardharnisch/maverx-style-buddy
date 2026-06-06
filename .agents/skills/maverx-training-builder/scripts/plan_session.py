#!/usr/bin/env python3
"""Plan one session: slide-by-slide blueprint with full speaker notes.

Usage:
    python plan_session.py --intake intake.json --track track_plan.json --session 1 --out out/<slug>/sessions/1/session_plan.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

from openrouter_call import call_openrouter, DEFAULT_PLANNER_MODEL

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load_schema() -> dict:
    """Load and pre-resolve the $ref to slide.schema.json into a single doc."""
    session = json.loads((ROOT / "schemas" / "session_plan.schema.json").read_text())
    slide = json.loads((ROOT / "schemas" / "slide.schema.json").read_text())
    session["properties"]["slides"]["items"] = slide
    return session


def validate_timing(plan: dict, target_min: int, tol: int = 5) -> str | None:
    total = sum(s.get("notes", {}).get("time_min", 0) for s in plan.get("slides", []))
    if abs(total - target_min) > tol:
        return f"sum(notes.time_min)={total} but session.duration_min={target_min} (±{tol})"
    return None


def validate_exercise_linkage(plan: dict) -> str | None:
    targets = set()
    for s in plan.get("slides", []):
        if s.get("role", "").startswith("theory_"):
            t = s.get("exercise_target")
            if not t:
                return f"theory slide titled {s.get('title')!r} missing exercise_target"
            targets.add(t.lower())
    if not targets:
        return None
    body_text = " ".join(
        " ".join(s.get("body", []))
        for s in plan.get("slides", [])
        if s.get("role", "").startswith("exercise_")
    ).lower()
    missing = [t for t in targets if t not in body_text]
    if missing:
        return f"exercise slides do not mention exercise_target(s): {missing}"
    return None


def plan_session(
    intake: dict, track: dict, session_n: int, model: str | None = None
) -> dict:
    session_entry = next(s for s in track["sessions"] if s["n"] == session_n)
    duration_min = intake["duration"]["minutes_per_session"]
    system = (ROOT / "prompts" / "system_session_planner.md").read_text()
    schema = load_schema()

    base_user = (
        f"INTAKE:\n{json.dumps(intake, indent=2)}\n\n"
        f"TRACK_PLAN (case + protagonists):\n{json.dumps(track, indent=2)}\n\n"
        f"SESSION (the one you are planning):\n{json.dumps(session_entry, indent=2)}\n\n"
        f"SESSION DURATION (minutes): {duration_min}\n\n"
        "Emit one JSON object matching session_plan.schema.json. "
        "Slides array must follow the structure described in the system prompt."
    )

    user = base_user
    for attempt in range(3):
        plan = call_openrouter(
            system=system, user=user, model=model or DEFAULT_PLANNER_MODEL,
            max_tokens=14000, temperature=0.4,
        )
        plan.setdefault("session_n", session_n)
        plan.setdefault("duration_min", duration_min)
        plan.setdefault("title", session_entry["title"])
        plan.setdefault("backbone_phase", session_entry.get("backbone_phase", ""))
        try:
            jsonschema.validate(plan, schema)
        except jsonschema.ValidationError as e:
            user = base_user + f"\n\nYour last output failed schema validation: {e.message}. Re-emit corrected JSON."
            continue
        errs = []
        if (e := validate_timing(plan, duration_min)):
            errs.append(e)
        if (e := validate_exercise_linkage(plan)):
            errs.append(e)
        if errs:
            user = base_user + "\n\nFix these issues and re-emit JSON:\n- " + "\n- ".join(errs)
            continue
        return plan
    raise RuntimeError(f"Could not produce valid session plan for session {session_n}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", required=True)
    ap.add_argument("--track", required=True)
    ap.add_argument("--session", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    intake = json.loads(Path(args.intake).read_text())
    track = json.loads(Path(args.track).read_text())
    plan = plan_session(intake, track, args.session, model=args.model)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2))
    print(f"wrote {out}  ({len(plan['slides'])} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
