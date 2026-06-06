from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.constants import DEFAULT_MODEL


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class SendMessageRequest(BaseModel):
    content: str = Field(
        min_length=1,
        description="The user's chat message.",
        examples=["Build a 6-slide deck introducing Lean for managers."],
    )
    model: str = Field(
        default=DEFAULT_MODEL,
        description="Model id to generate with (see GET /models).",
        examples=[DEFAULT_MODEL],
    )


class DeckArtifact(BaseModel):
    """Reference to a generated deck. Stubbed until the pipeline lands."""

    deck_id: str = Field(description="Identifier for the generated deck.")
    filename: str = Field(description="Suggested download filename.")
    slide_count: int = Field(ge=0, description="Number of slides in the deck.")
    download_url: str | None = Field(
        default=None, description="URL to download the .pptx once available."
    )


class Message(BaseModel):
    id: str = Field(description="Unique message identifier.")
    role: MessageRole = Field(description="Who authored the message.")
    content: str = Field(description="Message text.")
    created_at: datetime = Field(description="ISO-8601 creation timestamp.")
    deck: DeckArtifact | None = Field(
        default=None,
        description="Deck produced by this assistant turn, if any.",
    )


class MessagesResponse(BaseModel):
    session_id: str
    messages: list[Message]
