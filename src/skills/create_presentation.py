"""Skill: create a new blank presentation and return its session ID."""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "create_presentation",
        "description": "Create a new blank PowerPoint presentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Presentation title"},
                "style_guide": {"type": "string", "description": "Name of the style guide to apply"},
            },
            "required": ["title"],
        },
    },
}


def execute(title: str, style_guide: str = "default") -> dict:
    pass
