#!/usr/bin/env python3
"""Orchestrate a full Tier 3 build: intake → track plan → per-session (plan + deck + bites + case) → overview → QA.

Usage:
    python run_tier3.py --intake intake.json --out ./out/<slug>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASSETS = ROOT / "assets"
SCHEMAS = ROOT / "schemas"


def sh(args: list[str]) -> None:
    print(f"$ {' '.join(args)}", flush=True)
    r = subprocess.run(args, cwd=ROOT, check=False)
    if r.returncode not in (0, 1):  # QA returns 1 for issues; that's a soft fail
        raise SystemExit(f"step failed: {' '.join(args)} (exit {r.returncode})")


def validate_intake(intake_path: Path) -> dict:
    schema = json.loads((SCHEMAS / "intake.schema.json").read_text())
    intake = json.loads(intake_path.read_text())
    jsonschema.validate(intake, schema)
    if intake.get("tier") != 3:
        print(f"[warn] tier={intake.get('tier')} — this orchestrator targets Tier 3", file=sys.stderr)
    completeness = intake.get("completeness_score", 0)
    vague = intake.get("vague_fields", [])
    if completeness < 0.8 or vague:
        raise SystemExit(
            f"Intake is not complete enough: completeness_score={completeness}, vague_fields={vague}. "
            "Have the intake agent ask follow-ups before generating."
        )
    return intake


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--planner-model", default=None)
    ap.add_argument("--writer-model", default=None)
    args = ap.parse_args()

    intake_path = Path(args.intake).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    intake = validate_intake(intake_path)
    print(f"[intake] OK — tier={intake.get('tier')}, sessions={intake['duration']['sessions']}")

    # 1) track plan
    track_path = out_dir / "track_plan.json"
    cmd = [sys.executable, "scripts/plan_track.py", "--intake", str(intake_path), "--out", str(track_path)]
    if args.planner_model:
        cmd += ["--model", args.planner_model]
    sh(cmd)
    track = json.loads(track_path.read_text())

    # 2) overview
    overview_path = out_dir / "track_overview.docx"
    sh([sys.executable, "scripts/build_track_overview.py", "--intake", str(intake_path), "--track", str(track_path), "--out", str(overview_path)])

    # 3) per-session
    for s in track["sessions"]:
        n = s["n"]
        sdir = out_dir / "sessions" / str(n)
        sdir.mkdir(parents=True, exist_ok=True)
        plan_path = sdir / "session_plan.json"
        deck_path = sdir / f"session_{n}.pptx"
        case_path = sdir / "case_handout.docx"
        qa_path = sdir / "qa_report.md"

        cmd = [sys.executable, "scripts/plan_session.py", "--intake", str(intake_path), "--track", str(track_path), "--session", str(n), "--out", str(plan_path)]
        if args.planner_model:
            cmd += ["--model", args.planner_model]
        sh(cmd)

        sh([sys.executable, "scripts/build_deck.py", "--session-plan", str(plan_path), "--master", str(ASSETS / "maverx_master.pptx"), "--catalog", str(ASSETS / "template_catalog.json"), "--out", str(deck_path)])
        sh([sys.executable, "scripts/build_bites.py", "--intake", str(intake_path), "--track", str(track_path), "--session", str(n), "--out-dir", str(sdir)])
        sh([sys.executable, "scripts/build_case_handout.py", "--intake", str(intake_path), "--track", str(track_path), "--session", str(n), "--out", str(case_path)])
        sh([sys.executable, "scripts/qa_deck.py", "--session-plan", str(plan_path), "--deck", str(deck_path), "--track", str(track_path), "--out", str(qa_path)])
        print(f"[session {n}] done")

    # 4) trainer README
    trainer_readme = out_dir / "README_for_trainer.md"
    trainer_readme.write_text(_trainer_readme(track))
    print(f"[done] track at {out_dir}")
    return 0


def _trainer_readme(track: dict) -> str:
    lines = [
        f"# {track.get('track_title', 'Certification Track')}",
        "",
        f"Backbone: **{track.get('backbone')}**  |  Sessions: **{len(track.get('sessions', []))}**",
        "",
        "## How to use this bundle",
        "",
        "1. Open `track_overview.docx` for the red thread across all sessions.",
        "2. For each session, open `sessions/N/session_<N>.pptx` in PowerPoint to teach.",
        "3. Send `pre_bite.docx` before each session; send `post_bite.docx` after.",
        "4. Distribute `case_handout.docx` at the start of the exercise block.",
        "5. Speaker notes (5 fields per slide) live in the PowerPoint notes pane.",
        "",
        "## Sessions",
        "",
    ]
    for s in track.get("sessions", []):
        lines.append(f"- **Session {s['n']} — {s['title']}** ({s.get('backbone_phase')})")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
