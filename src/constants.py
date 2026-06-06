import os
from pathlib import Path

# Repo root — used to locate the bundled skill assets (template deck, schema,
# build/validate scripts) regardless of the current working directory.
REPO_ROOT = Path(__file__).resolve().parents[1]

APP_TITLE = "Decker"
APP_DESCRIPTION = "Decker — AI-powered slide deck builder in Maverx house style"
APP_VERSION = "0.1.0"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))

# Hardcoded model list surfaced in the Settings page (GET /models).
# TODO: source this from the provider once routing is wired up.
AVAILABLE_MODELS: list[str] = [
    "anthropic/claude-opus-4-8",
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-5.5",
]
DEFAULT_MODEL = os.getenv("MODEL", AVAILABLE_MODELS[0])

ORDERED_BLOCKS: list[str] = [
    "kick-off",
    "theory",
    "example",
    "exercise",
    "wrap-up",
]
VALID_BLOCKS: frozenset[str] = frozenset(ORDERED_BLOCKS)

DECK_FILENAME = "deck.pptx"
PRE_BITE_FILENAME = "pre-bite.docx"
POST_BITE_FILENAME = "post-bite.docx"
OVERVIEW_FILENAME = "overview.docx"

AGENT_MAX_ITERATIONS = 20


SESSION_MIN_ANSWER_WORDS = 2
TRACK_MIN_ANSWER_WORDS = 3

DEFAULT_LANGUAGE = "en"
DEFAULT_STYLE_GUIDE = "maverx"

# --- Pipeline / build wiring -------------------------------------------------

# The conversational pipeline (intake → lesson plan) runs in-process on
# OpenRouter; the heavy deck build is delegated to a build backend. "script"
# uses the bundled deterministic python-pptx builder and works today; "codex"
# shells out to the Codex CLI once it is installed and an OpenAI key is set.
BUILD_BACKEND = os.getenv("BUILD_BACKEND", "script")

# Bundled skill assets that the build backend consumes.
_PRESENTATION_SKILL = (
    REPO_ROOT / ".agents" / "skills" / "maverx-presentation-builder"
)
_TRAINING_SKILL = REPO_ROOT / ".agents" / "skills" / "maverx-training-builder"

TEMPLATE_DECK_PATH = _PRESENTATION_SKILL / "assets" / "slides" / "templates.pptx"
BUILD_SCRIPT_PATH = _PRESENTATION_SKILL / "scripts" / "build_maverx_artifacts.py"
LESSON_PLAN_SCHEMA_PATH = _TRAINING_SKILL / "schemas" / "lesson_plan.schema.json"
VALIDATE_SCRIPT_PATH = _TRAINING_SKILL / "scripts" / "validate_lesson_plan.py"

LESSON_PLAN_FILENAME = "lesson_plan.json"

# Where uploaded house-style master decks live. Style is a configurable input
# (not hard-coded), so new brand assets can be swapped in without a rebuild.
STYLE_GUIDES_DIR = Path(os.getenv("STYLE_GUIDES_DIR", "style_guides"))

# Whether the build backend should render decks to PNG for visual review
# (requires LibreOffice + pdftoppm). Off by default to keep generation fast.
RENDER_DECKS = os.getenv("RENDER_DECKS", "0") == "1"

# Max attempts to repair a schema-invalid lesson plan before giving up.
LESSON_PLAN_MAX_REPAIRS = int(os.getenv("LESSON_PLAN_MAX_REPAIRS", "2"))

# Intake context the doc requires before any content is generated. Keys match
# the lesson_plan intake_summary fields the generator consumes.
INTAKE_FIELDS: list[dict[str, str]] = [
    {"key": "topic", "question": "What is the topic or skill to be trained?"},
    {"key": "audience", "question": "Who is the target audience?"},
    {
        "key": "knowledge_level",
        "question": "What is the knowledge level of participants "
        "(beginner / intermediate / advanced / mixed)?",
    },
    {
        "key": "duration",
        "question": "How long is the training (e.g. '3 hours', '2x2 hours')?",
    },
    {
        "key": "primary_objective",
        "question": "What is the primary learning objective?",
    },
]
