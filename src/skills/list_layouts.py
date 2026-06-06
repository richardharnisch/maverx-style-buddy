"""Skill: list available slide layout keys and descriptions for a presentation."""

import logging

from src.skills import _store
from src.style_guides.loader import load_slide_templates

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "list_layouts",
        "description": (
            "List all available slide layout keys for a presentation, with descriptions "
            "of when to use each. Call this after create_presentation and before add_slide."
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
    templates = load_slide_templates(guide)

    if not templates:
        log.warning("No layout templates found for guide '%s'", guide.name)
        return {
            "error": "No layout templates available.",
            "hint": "Ensure the style guide has a .pptx template in the style_guides/ directory.",
        }

    layouts = [
        {
            "key": t.key,
            "description": t.description,
            "text_areas": [ta.role for ta in t.text_areas],
            "layout_name": t.layout_name,
        }
        for t in templates.values()
    ]
    log.info("Returning %d layout(s) for guide '%s'", len(layouts), guide.name)
    return {"layouts": layouts}
