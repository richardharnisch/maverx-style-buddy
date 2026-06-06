"""Outline generator — the "Human-in-the-Loop" checkpoint.

Generates a structured training outline (kick-off → theory → example
→ exercise → wrap-up) from the completed intake, then waits for the
trainer to review, optionally edit, and approve before heavy generation
begins.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .session import SessionStatus, get_session_or_404, _sessions

router = APIRouter(prefix="/sessions", tags=["outline"])


class SlideBlock(BaseModel):
    block: str  # kick-off | theory | example | exercise | wrap-up
    title: str
    bullets: list[str] = []
    notes: str = ""
    estimated_minutes: int = 0


class Outline(BaseModel):
    title: str
    total_minutes: int
    modules: list[SlideBlock]


class OutlineEditRequest(BaseModel):
    outline: Outline


@router.post(
    "/{session_id}/outline/generate",
    response_model=Outline,
    summary="Generate a training outline from completed intake",
)
def generate_outline(session_id: str) -> Outline:
    session = get_session_or_404(session_id)

    if session.status == SessionStatus.intake:
        raise HTTPException(
            status_code=409,
            detail="Complete all intake questions before generating an outline",
        )
    if session.status not in (
        SessionStatus.intake_complete,
        SessionStatus.outline_pending,
    ):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot generate outline in '{session.status}' state",
        )

    # TODO: call agent loop with intake data to produce the outline
    outline = _stub_outline(session.intake)

    session.outline = outline.model_dump()
    session.status = SessionStatus.outline_pending
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session

    return outline


@router.get(
    "/{session_id}/outline",
    response_model=Outline,
    summary="Get the current outline",
)
def get_outline(session_id: str) -> Outline:
    session = get_session_or_404(session_id)
    if not session.outline:
        raise HTTPException(status_code=404, detail="No outline generated yet")
    return Outline(**session.outline)


@router.put(
    "/{session_id}/outline",
    response_model=Outline,
    summary="Replace the outline with trainer edits",
)
def edit_outline(session_id: str, body: OutlineEditRequest) -> Outline:
    session = get_session_or_404(session_id)
    if session.status != SessionStatus.outline_pending:
        raise HTTPException(
            status_code=409,
            detail="Outline can only be edited while in 'outline_pending' state",
        )
    session.outline = body.outline.model_dump()
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session
    return body.outline


@router.post(
    "/{session_id}/outline/approve",
    summary="Approve the outline and queue asset generation",
)
def approve_outline(session_id: str) -> dict[str, str]:
    session = get_session_or_404(session_id)
    if session.status != SessionStatus.outline_pending:
        raise HTTPException(
            status_code=409,
            detail="Only a pending outline can be approved",
        )
    if not session.outline:
        raise HTTPException(status_code=409, detail="No outline to approve")

    session.status = SessionStatus.outline_approved
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session

    return {
        "message": "Outline approved — call POST /sessions/{id}/assets/generate to build the deck"
    }


# ---------------------------------------------------------------------------
# Stub — replaced by real agent call
# ---------------------------------------------------------------------------


def _stub_outline(intake: dict[str, Any]) -> Outline:
    topic = intake.get("topic", "Training Topic")
    duration_raw = intake.get("duration", "3 hours")
    total_minutes = _parse_duration_minutes(duration_raw)

    blocks = [
        (
            "kick-off",
            "Welcome & Learning Goals",
            ["Agenda", "Why this matters", "Learning objectives"],
            10,
        ),
        (
            "theory",
            f"Core Concepts: {topic}",
            ["Key concept 1", "Key concept 2", "Key concept 3"],
            40,
        ),
        (
            "example",
            "Real-World Example",
            ["Case context", "Step-by-step walkthrough", "Key takeaway"],
            20,
        ),
        (
            "exercise",
            "Hands-On Exercise",
            ["Instructions", "Success criteria", "Debrief prompt"],
            30,
        ),
        (
            "wrap-up",
            "Wrap-Up & Next Steps",
            ["Summary", "Link to practice", "Further reading"],
            10,
        ),
    ]

    modules = [
        SlideBlock(
            block=block,
            title=title,
            bullets=bullets,
            estimated_minutes=minutes,
        )
        for block, title, bullets, minutes in blocks
    ]

    return Outline(title=topic, total_minutes=total_minutes, modules=modules)


def _parse_duration_minutes(raw: str) -> int:
    raw = raw.lower()
    total = 0
    import re

    for match in re.finditer(
        r"(\d+(?:\.\d+)?)\s*(hour|hr|minute|min|h|m)", raw
    ):
        value, unit = float(match.group(1)), match.group(2)
        total += int(value * 60) if unit.startswith("h") else int(value)
    return total or 180
