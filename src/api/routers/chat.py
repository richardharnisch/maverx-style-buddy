import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from src.agent.pipeline import handle_turn
from ..schemas.chat import (
    DeckArtifact,
    Message,
    MessageRole,
    MessagesResponse,
    SendMessageRequest,
)
from .session import get_session_or_404

router = APIRouter(prefix="/sessions", tags=["chat"])

# In-memory message store, keyed by session id. Mirrors the _sessions pattern
# in session.py. TODO: replace with real persistence once the pipeline lands.
_messages: dict[str, list[Message]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_message(role: MessageRole, content: str, **extra) -> Message:
    return Message(
        id=str(uuid.uuid4()),
        role=role,
        content=content,
        created_at=_now(),
        **extra,
    )


@router.get(
    "/{session_id}/messages",
    response_model=MessagesResponse,
    summary="List all messages in a session",
)
def list_messages(session_id: str) -> MessagesResponse:
    get_session_or_404(session_id)
    return MessagesResponse(
        session_id=session_id, messages=_messages.get(session_id, [])
    )


@router.post(
    "/{session_id}/messages",
    response_model=MessagesResponse,
    summary="Send a chat message and get the assistant reply",
)
def send_message(
    session_id: str, body: SendMessageRequest
) -> MessagesResponse:
    session = get_session_or_404(session_id)
    history = _messages.setdefault(session_id, [])
    history.append(_new_message(MessageRole.user, body.content))

    # Drive the hybrid pipeline: conversational intake on OpenRouter, then
    # lesson-plan generation + deck build once intake is complete.
    result = handle_turn(session, body.content, body.model)
    deck = DeckArtifact(**result.deck) if result.deck else None
    history.append(
        _new_message(MessageRole.assistant, result.reply, deck=deck)
    )
    return MessagesResponse(session_id=session_id, messages=history)
