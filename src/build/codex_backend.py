"""Codex CLI build backend — the agentic build pass from the design sketch.

Shells out to the Codex CLI in non-interactive (``exec``) mode, pointing it at
the bundled ``maverx-presentation-builder`` skill and the validated lesson
plan. Codex reads the skill, runs the builder, renders the decks, visually
inspects them, and fixes issues before returning.

This backend is only selected when ``BUILD_BACKEND=codex``. It requires the
``codex`` CLI on PATH and an OpenAI key in the environment; if either is
missing it raises a clear :class:`BuildError` so the operator can fall back to
the script backend.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path

from pptx import Presentation

from src.constants import REPO_ROOT, TEMPLATE_DECK_PATH

from .base import BuildError, BuildResult, parse_manifest

log = logging.getLogger(__name__)

# Agentic build + visual review is slow; give Codex real headroom.
_CODEX_TIMEOUT_S = int(os.getenv("CODEX_TIMEOUT_S", "1200"))

_PROMPT = """\
Use the maverx-presentation-builder skill to turn this validated lesson plan \
into Maverx-branded delivery artifacts.

Lesson plan: {plan}
Template deck: {template}
Output directory: {out_dir}

Follow the skill's workflow: run the builder script, open the resulting PPTX to \
verify it, render each deck to PNG, visually inspect the slides, and fix any \
overflow or layout issues. Write a manifest.json to the output directory listing \
every output. Return only paths and review notes — do not paste file contents.\
"""


class CodexBuildBackend:
    name = "codex"

    def _ensure_available(self) -> str:
        codex = shutil.which("codex")
        if not codex:
            raise BuildError(
                "BUILD_BACKEND=codex but the `codex` CLI is not on PATH. "
                "Install it, or set BUILD_BACKEND=script to use the bundled builder."
            )
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("CODEX_API_KEY")):
            raise BuildError(
                "BUILD_BACKEND=codex but no OPENAI_API_KEY is set for the Codex CLI."
            )
        return codex

    def build(self, lesson_plan_path: Path, out_dir: Path) -> BuildResult:
        codex = self._ensure_available()
        out_dir.mkdir(parents=True, exist_ok=True)
        prompt = _PROMPT.format(
            plan=lesson_plan_path,
            template=TEMPLATE_DECK_PATH,
            out_dir=out_dir,
        )
        # `exec` is Codex's non-interactive mode; run from the repo root so the
        # skill under .agents/skills is discoverable.
        cmd = [codex, "exec", "--skip-git-repo-check", prompt]
        log.info("Running Codex build in %s", REPO_ROOT)
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=_CODEX_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as exc:
            raise BuildError(f"Codex timed out after {_CODEX_TIMEOUT_S}s") from exc

        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()[-2000:]
            raise BuildError(f"Codex build failed: {detail}")

        manifest_path = out_dir / "manifest.json"
        deck_paths, doc_paths = parse_manifest(manifest_path)
        if not deck_paths:
            raise BuildError("Codex build produced no .pptx decks")

        slide_count = sum(len(Presentation(str(p)).slides) for p in deck_paths)
        # Surface a trimmed tail of Codex's own summary as review notes.
        tail = (proc.stdout or "").strip().splitlines()[-5:]
        notes = [line for line in tail if line.strip()]
        return BuildResult(
            deck_paths=deck_paths,
            doc_paths=doc_paths,
            manifest_path=manifest_path,
            slide_count=slide_count,
            notes=notes,
        )
