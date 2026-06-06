"""Build backend contract shared by the script and Codex implementations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class BuildError(RuntimeError):
    """Raised when a backend fails to produce a deck."""


@dataclass
class BuildResult:
    """Outcome of a deck build for a single session/lesson plan."""

    deck_paths: list[Path]
    doc_paths: list[Path] = field(default_factory=list)
    manifest_path: Path | None = None
    slide_count: int = 0
    # Free-form notes from the backend (e.g. visual-review findings, template
    # compromises). Surfaced to the trainer in the chat reply.
    notes: list[str] = field(default_factory=list)

    @property
    def primary_deck(self) -> Path | None:
        return self.deck_paths[0] if self.deck_paths else None


def parse_manifest(manifest_path: Path) -> tuple[list[Path], list[Path]]:
    """Read a builder ``manifest.json`` into (deck_paths, doc_paths).

    Both the script builder and the Codex skill write the same manifest shape:
    ``{"outputs": [{"session_n", "pptx", "docx": [...]}, ...]}``.
    """
    if not manifest_path.exists():
        raise BuildError(f"No manifest at {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    deck_paths: list[Path] = []
    doc_paths: list[Path] = []
    for entry in manifest.get("outputs", []):
        if entry.get("pptx"):
            deck_paths.append(Path(entry["pptx"]))
        doc_paths.extend(Path(p) for p in entry.get("docx", []))
    # Track-level artifacts (e.g. the programme overview) for multi-session plans.
    doc_paths.extend(Path(p) for p in manifest.get("track_docs", []))
    return deck_paths, doc_paths


class BuildBackend(Protocol):
    """Turns a validated ``lesson_plan.json`` into delivery artifacts."""

    name: str

    def build(self, lesson_plan_path: Path, out_dir: Path) -> BuildResult:
        """Build artifacts for ``lesson_plan_path`` into ``out_dir``.

        Must raise :class:`BuildError` on failure rather than returning an
        empty result, so callers can surface a clear message.
        """
        ...
