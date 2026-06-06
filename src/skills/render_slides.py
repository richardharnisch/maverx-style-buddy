"""Skill: render an in-progress presentation to PNG images via LibreOffice headless."""

import base64
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from src.skills import _store

log = logging.getLogger(__name__)

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "render_slides",
        "description": (
            "Render all slides of an in-progress presentation as PNG images so you can visually "
            "inspect them. Returns each slide as a base64-encoded image. "
            "Does NOT export or remove the presentation — call export_pptx when you are done."
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
    if not shutil.which("libreoffice"):
        return {
            "error": "LibreOffice is not installed or not in PATH.",
            "hint": "Install it with: sudo apt install libreoffice",
        }

    prs, _, _ = _store.get(presentation_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "preview.pptx"
        prs.save(str(tmp_path))
        log.debug("Saved temp pptx for rendering: %s", tmp_path)

        result = subprocess.run(
            [
                "libreoffice", "--headless",
                "--convert-to", "png",
                "--outdir", tmpdir,
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            log.warning("LibreOffice conversion failed: %s", result.stderr)
            return {"error": "LibreOffice conversion failed", "details": result.stderr}

        # LibreOffice names output files preview1.png, preview2.png, … (1-indexed)
        # Also handles single-slide case: preview.png
        pngs = sorted(Path(tmpdir).glob("preview*.png"))
        log.debug("Found %d PNG(s): %s", len(pngs), [p.name for p in pngs])

        if not pngs:
            return {"error": "No PNG files produced by LibreOffice", "stdout": result.stdout}

        slides = []
        for i, png in enumerate(pngs):
            image_b64 = base64.b64encode(png.read_bytes()).decode()
            slides.append({"index": i, "image_b64": image_b64})

    log.info("Rendered %d slide(s) for presentation %s", len(slides), presentation_id)
    return {"count": len(slides), "slides": slides}
