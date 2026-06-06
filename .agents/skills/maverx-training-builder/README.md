# Maverx Training Builder — Skill README

An agentic skill that takes a trainer from a one-sentence idea ("we need a Lean Black Belt") to a full Maverx-house-style training bundle: editable .pptx decks + pre/post-bites + case handouts + a track overview document. Designed to plug into Codex, Claude Code, Lovable, or any agent runtime that loads skills from a directory.

## What you get

For a Tier 3 run, in `out/<track-slug>/`:

```
intake.json                 # validated answers to the 5+ required questions
track_plan.json             # DMAIC backbone + fictional case + 8 sessions + N→N+1 handshake
track_overview.docx         # red thread across all sessions
sessions/
  1/
    session_plan.json       # slide-by-slide blueprint with full speaker notes
    session_1.pptx          # editable deck (cloned from Maverx master)
    pre_bite.docx
    post_bite.docx
    case_handout.docx       # case-so-far + today + working space
    qa_report.md            # auto-QA results
  …
README_for_trainer.md
```

## How it works

1. **Intake** (`prompts/system_intake.md`) — the agent host runs a conversation, asks the 5 required questions plus tier-specific follow-ups, refuses to generate until completeness ≥ 0.8.
2. **Track planning** (`plan_track.py`) — one LLM call writes `track_plan.json` with the DMAIC backbone, a fictional company + protagonists + dataset, per-session objectives, and the post-bite ↔ next pre-bite handshake. Validated by `jsonschema` + a custom handshake check; retried with feedback until valid.
3. **Session planning** (`plan_session.py`) — one LLM call per session writes `session_plan.json`. The session planner enforces the didactic arc, timing budget, theory ↔ exercise linkage, and the 5 speaker-notes fields.
4. **Deck build** (`build_deck.py`) — opens `assets/maverx_master.pptx`, looks up each slide's role in `assets/template_catalog.json`, and **clones the corresponding master slide** rather than redrawing shapes. Text frames are swapped in place, preserving fonts, colours, the footer, and the logo. Tables are real `python-pptx` tables.
5. **Bites + case** (`build_bites.py`, `build_case_handout.py`) — `python-docx` documents with the same Maverx-purple title colour.
6. **Track overview** (`build_track_overview.py`) — a single .docx with the red-thread table and handshake validation list.
7. **QA** (`qa_deck.py`) — checks footer presence, editable text, the 5 notes fields, font/color whitelist (vs `references/house_style.md`), timing sum, didactic-arc completeness, theory↔exercise linkage, and the track-level handshake.

## Setup

```bash
# 1. Install Python deps
python -m pip install python-pptx python-docx requests jsonschema lxml

# 2. Provide the OpenRouter key
export OPENROUTER_API_KEY=sk-or-...

# 3. (One-off, when swapping the master) re-index layouts
python scripts/inspect_master.py assets/maverx_master.pptx assets/
```

LibreOffice + Poppler are only needed for visual QA of the rendered .pptx (the included `qa_deck.py` does *content* QA without them).

## Usage from an agent host

```python
# After running the intake conversation and saving intake.json:
import subprocess, sys
subprocess.run([sys.executable, "scripts/run_tier3.py",
                "--intake", "out/lean-black-belt/intake.json",
                "--out", "out/lean-black-belt"], check=True)
```

Or directly from the shell:

```bash
python scripts/run_tier3.py --intake out/lean-black-belt/intake.json --out out/lean-black-belt
```

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `OPENROUTER_API_KEY` | — (required) | Auth for every LLM call. |
| `MAVERX_PLANNER_MODEL` | `anthropic/claude-sonnet-4.5` | Track + session planning. |
| `MAVERX_WRITER_MODEL` | `openai/gpt-4.1-mini` | Bulk writers (bites, case, slide text). |

## Script reference

| Script | Purpose |
|--------|---------|
| `inspect_master.py` | Enumerate layouts + sample slides of a master `.pptx` into `master_index.json`. |
| `openrouter_call.py` | Thin OpenRouter client with retries + JSON mode. |
| `plan_track.py` | LLM → `track_plan.json` (DMAIC + case + handshake-validated). |
| `plan_session.py` | LLM → `session_plan.json` (slide blueprint + speaker notes). |
| `build_deck.py` | Clone master template slides + swap text → `session_N.pptx`. |
| `build_bites.py` | Generate `pre_bite.docx` + `post_bite.docx`. |
| `build_case_handout.py` | Generate `case_handout.docx` per session. |
| `build_track_overview.py` | Generate `track_overview.docx`. |
| `qa_deck.py` | Run all QA checks; emit `qa_report.md`. |
| `run_tier3.py` | End-to-end orchestrator. |

## Swapping the Maverx master

The skill is master-driven: replace `assets/maverx_master.pptx`, rerun `inspect_master.py`, and update `assets/template_catalog.json` if slide indices shift. `references/house_style.md` is the only other place to update if the palette/fonts change.

## Why this shape (and not a web app)

- **Skill, not app**: any agent host can adopt it without infra. The agent IS the UI.
- **Clone, don't redraw**: matches the Maverx style guide's own advice ("copying elements from another slide is always better") and guarantees house-style compliance without modelling layouts.
- **Schema-validated LLM output**: every planner call is retried with the validator's error message until it produces conforming JSON.
- **Per-session streaming writes**: Tier 3's 8 sessions × ~25 slides each never sit in a single LLM context — each session is planned, written, built, and QA'd independently.
