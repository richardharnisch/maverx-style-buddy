"""Select a build backend from configuration."""

from __future__ import annotations

from src.constants import BUILD_BACKEND

from .base import BuildBackend
from .codex_backend import CodexBuildBackend
from .script_backend import ScriptBuildBackend

_BACKENDS = {
    "script": ScriptBuildBackend,
    "codex": CodexBuildBackend,
}


def get_build_backend(name: str | None = None) -> BuildBackend:
    """Return the configured build backend (``BUILD_BACKEND`` env by default)."""
    key = (name or BUILD_BACKEND or "script").lower()
    try:
        return _BACKENDS[key]()
    except KeyError:
        raise ValueError(
            f"Unknown BUILD_BACKEND '{key}'. Valid: {', '.join(_BACKENDS)}"
        ) from None
