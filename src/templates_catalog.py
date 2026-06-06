"""Read-only access to the bundled Maverx slide template catalog.

The catalog lives in the maverx-presentation-builder skill assets and is the
source of truth for the template preview page. This module resolves those paths
and parses ``template_yaml/index.yaml`` so the API layer never hard-codes them.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
SLIDES_DIR = (
    _REPO_ROOT
    / ".agents"
    / "skills"
    / "maverx-presentation-builder"
    / "assets"
    / "slides"
)
INDEX_PATH = SLIDES_DIR / "template_yaml" / "index.yaml"


@lru_cache(maxsize=1)
def _load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        return []
    data = yaml.safe_load(INDEX_PATH.read_text()) or {}
    return data.get("slides", [])


def list_templates() -> list[dict]:
    """Return template metadata: ``template_id`` and ``title`` for each slide."""
    return [
        {"template_id": s["template_id"], "title": s["title"]}
        for s in _load_index()
    ]


def preview_path(template_id: str) -> Path | None:
    """Resolve the absolute preview PNG path for a template, or None."""
    for s in _load_index():
        if s["template_id"] == template_id:
            path = SLIDES_DIR / s["preview_image"]
            return path if path.exists() else None
    return None
