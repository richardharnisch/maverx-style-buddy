"""In-memory store mapping presentation_id -> (Presentation, StyleGuide, template_path)."""

from pathlib import Path

from pptx import Presentation

from src.style_guides.schema import StyleGuide

_store: dict[str, tuple[Presentation, StyleGuide, Path | None]] = {}


def get(pid: str) -> tuple[Presentation, StyleGuide, Path | None]:
    if pid not in _store:
        raise KeyError(f"No active presentation with id '{pid}'. Create one first.")
    return _store[pid]


def put(pid: str, prs: Presentation, guide: StyleGuide, template_path: Path | None = None) -> None:
    _store[pid] = (prs, guide, template_path)


def remove(pid: str) -> None:
    _store.pop(pid, None)
