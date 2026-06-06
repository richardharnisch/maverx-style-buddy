import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.constants import OUTPUT_DIR
from ..schemas.session import (
    CreateSessionRequest,
    Session,
    SessionResponse,
    SessionStatus,
)

router = APIRouter(prefix="/sessions", tags=["session"])

# In-memory store.
_sessions: dict[str, Session] = {}


def get_session_or_404(session_id: str) -> Session:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"Session '{session_id}' not found"
        )
    return session


@router.post(
    "",
    response_model=SessionResponse,
    status_code=201,
    summary="Create a new training session",
)
def create_session(
    body: CreateSessionRequest = CreateSessionRequest(),
) -> SessionResponse:
    now = datetime.now(timezone.utc)
    session = Session(
        id=str(uuid.uuid4()),
        status=SessionStatus.intake,
        language=body.language,
        style_guide=body.style_guide,
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
    import shutil

    session_dir = OUTPUT_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    del _sessions[session_id]
