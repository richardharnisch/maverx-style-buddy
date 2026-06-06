import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from ..schemas.outline import (
    Outline,
    OutlineEditRequest,
    OutlinePathRequest,
    SlideBlock,
    SpeakerNotes,
)
from ..schemas.session import SessionStatus
from .session import _sessions, get_session_or_404

router = APIRouter(prefix="/sessions", tags=["outline"])


@router.post(
    "/{session_id}/outline/path",
    summary="Choose outline path: 'trainer' (Option A) or 'research' (Option B)",
)
def set_outline_path(
    session_id: str, body: OutlinePathRequest
) -> dict[str, str]:
    session = get_session_or_404(session_id)

    if session.status == SessionStatus.intake:
        raise HTTPException(
            status_code=409,
            detail="Complete intake before choosing an outline path",
        )

    if body.path not in ("trainer", "research"):
        raise HTTPException(
            status_code=422, detail="path must be 'trainer' or 'research'"
        )

    session.outline_path = body.path
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session

    if body.path == "trainer":
        next_step = "PUT /sessions/{id}/outline to upload your outline, then POST /sessions/{id}/outline/approve"
    else:
        next_step = "POST /sessions/{id}/outline/generate to let the research agent propose an outline"

    return {"outline_path": body.path, "next": next_step}


@router.post(
    "/{session_id}/outline/generate",
    response_model=Outline,
    summary="Option B — generate a training outline via the research agent",
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

    # TODO: call agent loop with intake data to produce outline
    #   The agent should propose the structure chunk by chunk and confirm with the trainer.
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
    summary="Option A — upload trainer-supplied outline, or edit a generated one",
)
def set_outline(session_id: str, body: OutlineEditRequest) -> Outline:
    session = get_session_or_404(session_id)

    if session.status not in (
        SessionStatus.intake_complete,
        SessionStatus.outline_pending,
    ):
        raise HTTPException(
            status_code=409,
            detail="Outline can only be set while in 'intake_complete' or 'outline_pending' state",
        )

    session.outline = body.outline.model_dump()
    session.status = SessionStatus.outline_pending
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session
    return body.outline


@router.post(
    "/{session_id}/outline/approve",
    summary="Approve the outline — unlocks asset generation and chunk proposal",
)
def approve_outline(session_id: str) -> dict[str, str]:
    session = get_session_or_404(session_id)

    if session.status != SessionStatus.outline_pending:
        raise HTTPException(
            status_code=409, detail="Only a pending outline can be approved"
        )
    if not session.outline:
        raise HTTPException(status_code=409, detail="No outline to approve")

    session.status = SessionStatus.outline_approved
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session

    return {
        "message": (
            "Outline approved. "
            "Option 1 (iterative): POST /sessions/{id}/chunks/{block}/propose per block. "
            "Option 2 (bulk): POST /sessions/{id}/assets/generate"
        )
    }

def _stub_outline(intake: dict[str, Any]) -> Outline:
    topic = intake.get("topic", "Training Topic")
    total_minutes = _parse_duration_minutes(intake.get("duration", "3 hours"))
    notes = SpeakerNotes()

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
            speaker_notes=notes,
        )
        for block, title, bullets, minutes in blocks
    ]
    return Outline(title=topic, total_minutes=total_minutes, modules=modules)


def _parse_duration_minutes(raw: str) -> int:
    raw = raw.lower()
    total = 0
    for match in re.finditer(
        r"(\d+(?:\.\d+)?)\s*(hour|hr|minute|min|h|m)", raw
    ):
        value, unit = float(match.group(1)), match.group(2)
        total += int(value * 60) if unit.startswith("h") else int(value)
    return total or 180
