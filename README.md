# Maverx Style Buddy: 1st Place at 2026 Digilize AI Hackathon!
![digilize](https://digilize.agency/static/Hackthon_poster-c16685.png)

Winning submission for the 2026 Digilize AI Hackathon, made by Teun Boersma, Marcus Persson, and Richard Harnisch. Thanks to everyone who helped make the day possible!

AI-powered CLI for building Maverx-branded training programmes and presentation artifacts. Runs an agent loop against any OpenRouter-compatible model to guide you through intake, generate schema-validated lesson plans, and produce ready-to-deliver PPTX decks and DOCX documents.

## Usage in Codex
To use in Codex, install [Codex](github.com/openai/codex) (free) and get a ChatGPT account (free). Then you can call $maverx-training-builder and $maverx-presentation-builder through the Codex-native skill selector. If you don't want to use Codex or want the FastAPI-Streamlit GUI, you can try the more involved setup below:

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- An [OpenRouter](https://openrouter.ai) API key

## Installation

```bash
git clone <repo-url>
cd maverx-style-buddy
uv sync
```

## Configuration

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
OPENROUTER_API_KEY=sk-or-...
```

Optional overrides:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | API base URL |
| `MODEL` | `qwen/qwen3.6-35b-a3b` | Model to use |
| `OUTPUT_DIR` | `outputs` | Root folder for generated files |

## Usage

### One-shot

```bash
uv run python -m src.main "Build a 2-session Lean Six Sigma intro for operations teams"
```

### Interactive mode

Omit the prompt to start a REPL-style session:

```bash
uv run python -m src.main
```

Type `reset` or `/reset` to clear the conversation and start over. Type `quit` or `exit` to stop.

### Flags

| Flag | Options | Default | Description |
|---|---|---|---|
| `--skill` | `combined`, `training-builder`, `presentation-builder` | `combined` | Which agent skill to run |
| `--model` | any OpenRouter model ID | env `MODEL` | Override the model for this run |
| `--log-level` | `DEBUG`, `INFO`, `WARNING` | `INFO` | Log verbosity |

## Available skills

### `combined` (default)

Auto-detects whether the request is about building a lesson plan or generating presentation artifacts and routes accordingly. Use this when you are not sure which skill applies.

### `training-builder`

Runs a structured intake conversation, researches the topic, and writes a schema-validated `lesson_plan.json` to `outputs/<slug>/`. The JSON is the handoff contract for the presentation builder.

```bash
uv run python -m src.main --skill training-builder "Design a Power BI certification track"
```

### `presentation-builder`

Takes a completed `lesson_plan.json` and produces one branded PPTX deck per session, plus DOCX pre-bites, post-bites, and optional handout documents.

```bash
uv run python -m src.main --skill presentation-builder "Build the deck from outputs/power-bi-cert/lesson_plan.json"
```

## Outputs

All generated files land under `outputs/<slug>/`:

```
outputs/
└── lean-six-sigma-intro/
    ├── lesson_plan.json
    └── presentation_artifacts/
        ├── session_1.pptx
        ├── session_1_pre_bite.docx
        ├── session_1_post_bite.docx
        └── manifest.json
```

## Architecture

```
src/
├── main.py              # Entry point — parses CLI args, delegates to interface
├── interface/cli.py     # One-shot and interactive REPL loop
├── agent/
│   ├── loop.py          # Core agent loop: sends messages, handles tool calls
│   └── client.py        # OpenRouter API client wrapper
└── skills/
    └── registry.py      # Tool definitions (OpenAI function-calling format) and dispatch
.agents/skills/
└── maverx-presentation-builder/
    ├── scripts/build_maverx_artifacts.py   # Renders lesson_plan.json → PPTX + DOCX
    └── assets/slides/templates.pptx        # Maverx branded slide master
```

**Request flow:**

1. CLI (`interface/cli.py`) receives a prompt and resolves the `--skill` flag.
2. `SkillRegistry` selects the tool set to expose — training tools, presentation tools, or both.
3. The agent loop (`agent/loop.py`) sends the conversation to OpenRouter; the model issues tool calls.
4. Tool calls are dispatched back through `SkillRegistry`:
   - **training-builder** tools write and validate `lesson_plan.json`.
   - **presentation-builder** tools invoke `build_maverx_artifacts.py` as a subprocess, which renders the branded PPTX/DOCX files from the lesson plan.
5. Results are fed back to the model until it produces a final text response.

The `lesson_plan.json` is the handoff contract between the two skills: training-builder produces it, presentation-builder consumes it.

## Optional API server

A FastAPI server is included for programmatic access:

```bash
uv run uvicorn src.api.router:app --host 0.0.0.0 --port 8000
```
