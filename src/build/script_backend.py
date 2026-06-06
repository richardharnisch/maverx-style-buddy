"""Deterministic build backend — runs the bundled python-pptx builder.

This is the default, dependency-light path: it shells out to
``build_maverx_artifacts.py`` (which ships with the presentation-builder
skill), parses the manifest it writes, and optionally renders each deck to PNG
for visual review using LibreOffice + pdftoppm when ``RENDER_DECKS`` is on.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

from pptx import Presentation

from src.constants import (
    BUILD_SCRIPT_PATH,
    RENDER_DECKS,
    TEMPLATE_DECK_PATH,
)

from .base import BuildError, BuildResult, parse_manifest

log = logging.getLogger(__name__)

# Generous because the builder opens/saves a multi-MB template per session.
_BUILD_TIMEOUT_S = 180
_RENDER_TIMEOUT_S = 120


class ScriptBuildBackend:
    name = "script"

    def build(self, lesson_plan_path: Path, out_dir: Path) -> BuildResult:
        if not TEMPLATE_DECK_PATH.exists():
            raise BuildError(f"Template deck not found at {TEMPLATE_DECK_PATH}")
        if not BUILD_SCRIPT_PATH.exists():
            raise BuildError(f"Build script not found at {BUILD_SCRIPT_PATH}")

        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(BUILD_SCRIPT_PATH),
            str(lesson_plan_path),
            "--template",
            str(TEMPLATE_DECK_PATH),
            "--out-dir",
            str(out_dir),
            "--clean",
        ]
        log.info("Running build script: %s", " ".join(cmd))
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=_BUILD_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as exc:
            raise BuildError(f"Build script timed out after {_BUILD_TIMEOUT_S}s") from exc

        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            raise BuildError(f"Build script failed: {detail}")

        manifest_path = out_dir / "manifest.json"
        deck_paths, doc_paths = parse_manifest(manifest_path)
        if not deck_paths:
            raise BuildError("Build produced no .pptx decks")

        slide_count = sum(len(Presentation(str(p)).slides) for p in deck_paths)

        notes: list[str] = []
        if RENDER_DECKS:
            notes.extend(self._render(deck_paths, out_dir))

        return BuildResult(
            deck_paths=deck_paths,
            doc_paths=doc_paths,
            manifest_path=manifest_path,
            slide_count=slide_count,
            notes=notes,
        )

    def _render(self, deck_paths: list[Path], out_dir: Path) -> list[str]:
        """Render decks to PNG for visual review. Best-effort: never fatal."""
        soffice = shutil.which("libreoffice") or shutil.which("soffice")
        pdftoppm = shutil.which("pdftoppm")
        if not soffice or not pdftoppm:
            return ["Render skipped: LibreOffice/pdftoppm not available."]

        render_dir = out_dir / "render"
        render_dir.mkdir(parents=True, exist_ok=True)
        notes: list[str] = []
        for deck in deck_paths:
            try:
                subprocess.run(
                    [soffice, "--headless", "--convert-to", "pdf",
                     "--outdir", str(render_dir), str(deck)],
                    capture_output=True, timeout=_RENDER_TIMEOUT_S, check=True,
                )
                pdf = render_dir / (deck.stem + ".pdf")
                subprocess.run(
                    [pdftoppm, "-png", "-r", "110", str(pdf),
                     str(render_dir / deck.stem)],
                    capture_output=True, timeout=_RENDER_TIMEOUT_S, check=True,
                )
                pngs = sorted(render_dir.glob(f"{deck.stem}*.png"))
                notes.append(f"Rendered {deck.name}: {len(pngs)} slide PNG(s).")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                notes.append(f"Render failed for {deck.name}: {exc}")
        return notes
