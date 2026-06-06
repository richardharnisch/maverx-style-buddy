"""Skill: apply or re-apply a style guide to an existing presentation."""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "apply_style_guide",
        "description": "Apply a named style guide (fonts, colors, logo) to the presentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "style_guide": {"type": "string", "description": "Name of the style guide file (without .yaml)"},
            },
            "required": ["presentation_id", "style_guide"],
        },
    },
}


def execute(presentation_id: str, style_guide: str) -> dict:
    pass
