"""Skill: finalise and write the presentation to disk as a .pptx file."""

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "export_pptx",
        "description": "Save the completed presentation to a .pptx file and return the file path.",
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "filename": {"type": "string", "description": "Output filename (without extension)"},
            },
            "required": ["presentation_id"],
        },
    },
}


def execute(presentation_id: str, filename: str = "output") -> dict:
    pass
