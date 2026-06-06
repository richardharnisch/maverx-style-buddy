import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from ..schemas.chat import (
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
    get_session_or_404(session_id)
    history = _messages.setdefault(session_id, [])
    history.append(_new_message(MessageRole.user, body.content))

    # TODO: wire the real presentation-builder pipeline here. For now we return
    # a canned assistant reply so the chat UI is fully exercisable end-to-end.
    reply = _new_message(
        MessageRole.assistant,
        (
            "🛠️ Decker is not wired to the deck-generation pipeline yet "
            f"(requested model: `{body.model}`). Once routing lands, this turn "
            "will produce a Maverx-branded deck from your prompt."
        ),
    )
    history.append(reply)
    return MessagesResponse(session_id=session_id, messages=history)
