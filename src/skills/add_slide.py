"""Skill: append a slide to an in-progress presentation."""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "add_slide",
        "description": "Add a slide to the presentation with a layout, title, and body content.",
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "layout": {"type": "string", "enum": ["title", "content", "two_column", "blank"]},
                "title": {"type": "string"},
                "body": {"type": "string"},
                "speaker_notes": {"type": "string"},
            },
            "required": ["presentation_id", "layout"],
        },
    },
}


def execute(presentation_id: str, layout: str, title: str = "", body: str = "", speaker_notes: str = "") -> dict:
    pass
