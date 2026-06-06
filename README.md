# Decker

AI-powered slide deck builder in the Maverx house style.

Decker is two processes:

- **Backend** — a FastAPI app (`src/api/`). A chat turn drives a **hybrid
  pipeline**: conversational intake → lesson-plan generation (both on OpenRouter,
  in `src/agent/`) → deck build (a pluggable backend in `src/build/`).
- **Frontend** — a Streamlit app (`app/`) with three pages:
  - **Chat** (`Home.py`) — each session is one slide deck (ChatGPT-style); the
    finished `.pptx` is downloadable from the preview pane.
  - **Templates** — browse the bundled Maverx slide templates and upload new ones.
  - **Settings** — pick the model used for generation.

## How a deck gets built

1. **Intake** (`src/agent/pipeline.py`) — the chat asks for the required training
   context, pushing back on vague answers, until it has enough.
2. **Lesson plan** (`src/agent/lesson_plan.py`) — generates a normalized plan,
   validates it against `lesson_plan.schema.json`, reconciles timing/numbering,
   and trims the deck to the template deck's capacity. Repairs on schema errors.
3. **Build** (`src/build/`) — a pluggable backend turns the plan into the deck:
   - `script` (default) — the bundled deterministic `python-pptx` builder. Works
     out of the box.
   - `codex` — shells out to the Codex CLI (the agentic build + visual-review
     pass). Requires the `codex` CLI on PATH and an OpenAI key.

   Select with `BUILD_BACKEND` in `.env`.

The slide template assets live in
`.agents/skills/maverx-presentation-builder/assets/slides/`.

> **Known limit:** the bundled builder assigns a unique template per slide
> (~14 usable layouts), so decks are capped accordingly. Larger decks need the
> builder taught to clone slides.

## Setup

```bash
uv sync
cp .env.example .env   # fill in OPENROUTER_API_KEY
```

## Run

Start the backend (port 8000):

```bash
uv run uvicorn src.api.router:app --reload
# or: uv run python main.py
```

In a second terminal, start the UI (port 8501):

```bash
uv run streamlit run app/Home.py
```

The Streamlit app reaches the backend via `API_BASE_URL` (default
`http://localhost:8000`). API docs are at `http://localhost:8000/docs`.
