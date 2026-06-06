import os
from pathlib import Path

APP_TITLE = "Maverx Style Buddy"
APP_DESCRIPTION = "AI-powered training builder: intake → outline → .pptx in Maverx house style"
APP_VERSION = "0.1.0"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))

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
