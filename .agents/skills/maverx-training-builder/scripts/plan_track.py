#!/usr/bin/env python3
"""Plan a Tier 3 track: DMAIC backbone, fictional case, N-to-N+1 handshake.

Usage:
    python plan_track.py --intake intake.json --out out/<slug>/track_plan.json
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


def load_prompt() -> str:
    return (ROOT / "prompts" / "system_track_planner.md").read_text()


def load_schema() -> dict:
    return json.loads((ROOT / "schemas" / "track_plan.schema.json").read_text())


def slugify(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")[:60] or "track"


def validate_handshake(plan: dict) -> list[str]:
    errs: list[str] = []
    sessions = plan.get("sessions", [])
    for i in range(1, len(sessions)):
        prev_artefact = sessions[i - 1].get("post_bite_artefact")
        expected = sessions[i].get("next_session_pre_bite_expects_from_prior")
        if prev_artefact != expected:
            errs.append(
                f"session {sessions[i]['n']} expects {expected!r} "
                f"but prior post_bite is {prev_artefact!r}"
            )
    if sessions and sessions[0].get("next_session_pre_bite_expects_from_prior") not in (
        "none",
        None,
        "",
    ):
        errs.append("session 1 should have next_session_pre_bite_expects_from_prior == 'none'")
    return errs


def plan_track(intake: dict, model: str | None = None) -> dict:
    system = load_prompt()
    schema = load_schema()
    user = f"INTAKE:\n{json.dumps(intake, indent=2)}\n\nReturn one JSON object matching track_plan.schema.json."

    for attempt in range(3):
        plan = call_openrouter(
            system=system, user=user, model=model or DEFAULT_PLANNER_MODEL,
            max_tokens=6000, temperature=0.4,
        )
        # Ensure slug
        if "track_slug" not in plan or not plan["track_slug"]:
            plan["track_slug"] = slugify(plan.get("track_title", intake.get("topic", "track")))
        try:
            jsonschema.validate(plan, schema)
        except jsonschema.ValidationError as e:
            user = f"Your previous output failed validation: {e.message}\n\nFix and re-emit the full JSON.\n\nINTAKE:\n{json.dumps(intake, indent=2)}"
            continue
        errs = validate_handshake(plan)
        if errs:
            user = (
                "Your previous plan broke the N to N+1 handshake. Errors:\n- "
                + "\n- ".join(errs)
                + "\n\nFix every session's post_bite_artefact and next_session_pre_bite_expects_from_prior so they line up. Re-emit the full JSON."
                + f"\n\nINTAKE:\n{json.dumps(intake, indent=2)}"
            )
            continue
        return plan
    raise RuntimeError("Could not produce valid track plan after 3 attempts")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    intake = json.loads(Path(args.intake).read_text())
    plan = plan_track(intake, model=args.model)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2))
    print(f"wrote {out}  ({len(plan['sessions'])} sessions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
