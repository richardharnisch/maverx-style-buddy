"""Session management — the backbone of the multi-step flow.

State machine:
  intake → intake_complete → outline_pending → outline_approved
  → generating → ready → (refining → ready)
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["session"])


class SessionStatus(str, Enum):
    intake = "intake"
    intake_complete = "intake_complete"
    outline_pending = "outline_pending"
    outline_approved = "outline_approved"
    generating = "generating"
    ready = "ready"
    refining = "refining"
    error = "error"


class Session(BaseModel):
    id: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    intake: dict[str, Any] = {}
    outline: dict[str, Any] | None = None
    assets: list[str] = []
    error: str | None = None
    # Track context — None when this is a standalone (Tier 1/2) session
    track_id: str | None = None
    session_number: int | None = None


# In-memory store — swap for Redis / DB in production
_sessions: dict[str, Session] = {}


def get_session_or_404(session_id: str) -> Session:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"Session '{session_id}' not found"
        )
    return session


class SessionResponse(BaseModel):
    id: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


@router.post(
    "",
    response_model=SessionResponse,
    status_code=201,
    summary="Create a new training session",
)
def create_session() -> SessionResponse:
    now = datetime.now(timezone.utc)
    session = Session(
        id=str(uuid.uuid4()),
        status=SessionStatus.intake,
        created_at=now,
        updated_at=now,
    )
    _sessions[session.id] = session
    return SessionResponse(**session.model_dump())


@router.get(
    "/{session_id}", response_model=Session, summary="Get full session state"
)
def get_session(session_id: str) -> Session:
    return get_session_or_404(session_id)


@router.delete(
    "/{session_id}", status_code=204, summary="Delete a session and its assets"
)
def delete_session(session_id: str) -> None:
    get_session_or_404(session_id)
    # TODO: also delete generated files from disk
    del _sessions[session_id]
