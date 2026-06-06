"""Skill: list available images from the style guide's image catalog."""

import logging
from pathlib import Path

import yaml

from src.skills import _store
from src.style_guides.loader import PROJECT_ROOT

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "list_images",
        "description": (
            "List all available images extracted from the branded template. "
            "Returns image keys you can pass as 'image_overrides' in add_slide to place "
            "specific photos or icons on slides that have image areas."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
            },
            "required": ["presentation_id"],
        },
    },
}


def execute(presentation_id: str) -> dict:
    _, guide, _ = _store.get(presentation_id)

    if not guide.layouts_dir:
        return {"error": "No layout directory linked to this style guide."}

    catalog_path = PROJECT_ROOT / guide.layouts_dir / "images" / "catalog.yaml"
    if not catalog_path.exists():
        return {"images": [], "hint": "No image catalog found. The template may not contain embedded images."}

    try:
        with catalog_path.open() as f:
            catalog = yaml.safe_load(f) or []
    except Exception as e:
        log.warning("Could not load image catalog: %s", e)
        return {"error": f"Could not read image catalog: {e}"}

    images = [
        {
            "key": entry["key"],
            "description": entry.get("description") or "unlabelled",
            "content_type": entry.get("content_type", ""),
            "usage_count": entry.get("usage_count", 0),
        }
        for entry in catalog
    ]
    log.info("Returning %d image(s) from catalog for guide '%s'", len(images), guide.name)
    return {"images": images, "total": len(images)}
