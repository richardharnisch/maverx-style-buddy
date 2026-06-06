"""Pluggable deck-build backends.

The conversational pipeline (intake → lesson plan) runs in-process on
OpenRouter; building the actual ``.pptx`` is delegated to a build backend so
the heavy/agentic part can be swapped without touching the rest of the system.

- ``ScriptBuildBackend`` — runs the bundled deterministic ``python-pptx``
  builder. Works out of the box; the default.
- ``CodexBuildBackend`` — shells out to the Codex CLI, which reads the
  presentation-builder skill and builds + visually reviews the deck. Requires
  the ``codex`` CLI on PATH and an OpenAI key.

Select with the ``BUILD_BACKEND`` env var (see ``get_build_backend``).
"""

from .base import BuildBackend, BuildError, BuildResult
from .factory import get_build_backend

__all__ = [
    "BuildBackend",
    "BuildError",
    "BuildResult",
    "get_build_backend",
]
