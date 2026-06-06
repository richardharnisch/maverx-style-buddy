# Decker

AI-powered slide deck builder in the Maverx house style.

Decker is two processes:

- **Backend** — a FastAPI app (`src/api/`). Currently a skeleton: chat, templates,
  images, and sessions endpoints exist; the deck-generation pipeline is stubbed
  with `# TODO` markers pending the routing work.
- **Frontend** — a Streamlit app (`app/`) with three pages:
  - **Chat** (`Home.py`) — each session is one slide deck (ChatGPT-style).
  - **Templates** — browse the bundled Maverx slide templates and upload new ones.
  - **Settings** — pick the model used for generation (hardcoded list).

The slide template assets live in
`.agents/skills/maverx-presentation-builder/assets/slides/`.

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
