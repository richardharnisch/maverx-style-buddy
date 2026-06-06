import os
from pathlib import Path

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
