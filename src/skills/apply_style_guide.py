"""Skill: apply or re-apply a style guide to an existing presentation.

Full master-swap (merging theme XML trees) is deferred. This skill is a placeholder
that returns a clear status so the agent knows to create a fresh presentation instead.
"""

import logging

from src.skills import _store

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "apply_style_guide",
        "description": "Apply a named style guide to the presentation. Currently style guides are applied at creation time — call create_presentation with the desired style_guide instead.",
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "style_guide": {"type": "string"},
            },
            "required": ["presentation_id", "style_guide"],
        },
    },
}


def execute(presentation_id: str, style_guide: str) -> dict:
    log.warning("apply_style_guide called for prs=%s guide='%s' — not yet implemented", presentation_id, style_guide)
    _store.get(presentation_id)  # validates pid exists
    return {
        "status": "not_implemented",
        "message": (
            "Re-applying a style guide mid-session requires merging PowerPoint master XML, "
            "which is not yet implemented. Create a new presentation with the desired style_guide instead."
        ),
    }
