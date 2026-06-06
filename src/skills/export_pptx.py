"""Skill: finalise and write the presentation to disk as a .pptx file."""

import logging
from pathlib import Path

from src.skills import _store

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "export_pptx",
        "description": "Save the completed presentation to a .pptx file and return the file path.",
        "parameters": {
            "type": "object",
            "properties": {
                "presentation_id": {"type": "string"},
                "filename": {"type": "string", "description": "Output filename without extension (default: 'output')"},
            },
            "required": ["presentation_id"],
        },
    },
}


def _unique_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem, suffix, parent = base.stem, base.suffix, base.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def execute(presentation_id: str, filename: str = "output") -> dict:
    log.debug("Exporting presentation %s as '%s'", presentation_id, filename)
    prs, _, _ = _store.get(presentation_id)

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    path = _unique_path(out_dir / f"{filename}.pptx")
    log.debug("Output path: %s", path)

    prs.save(str(path))
    slide_count = len(prs.slides)
    _store.remove(presentation_id)

    log.info("Exported %d slides → %s", slide_count, path)
    return {"path": str(path), "slides": slide_count}
