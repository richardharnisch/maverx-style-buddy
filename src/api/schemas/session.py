from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from src.constants import DEFAULT_LANGUAGE, DEFAULT_STYLE_GUIDE


class SessionStatus(str, Enum):
    intake = "intake"
    intake_complete = "intake_complete"
    outline_pending = "outline_pending"
    outline_approved = "outline_approved"
    generating = "generating"
    ready = "ready"
    refining = "refining"
    error = "error"


class CreateSessionRequest(BaseModel):
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        min_length=2,
        max_length=10,
        description="BCP-47 language code; all output is generated in this language.",
        examples=["en", "nl"],
    )
    style_guide: str = Field(
        default=DEFAULT_STYLE_GUIDE,
        min_length=1,
        description="Name of the style guide YAML to apply.",
        examples=["default", "acme-corp"],
    )


class Session(BaseModel):
    id: str = Field(
        description="Unique session identifier.", examples=["sess_abc123"]
    )
    status: SessionStatus = Field(
        description="Current lifecycle status of the session."
    )
    language: str = Field(
        default=DEFAULT_LANGUAGE,
        min_length=2,
        max_length=10,
        description="BCP-47 language code for all generated output.",
        examples=["en", "nl"],
    )
    style_guide: str = Field(
        default=DEFAULT_STYLE_GUIDE,
        min_length=1,
        description="Name of the applied style guide.",
        examples=["default"],
    )
    outline_path: str | None = Field(
        default=None,
        pattern="^(trainer|research)$",
        description="Chosen outline path; set via POST /outline/path.",
        examples=["trainer", "research"],
    )
    created_at: datetime = Field(
        description="ISO-8601 timestamp when the session was created."
    )
    updated_at: datetime = Field(
        description="ISO-8601 timestamp of the last update."
    )
    intake: dict[str, Any] = Field(
        default_factory=dict,
        description="Accumulated intake answers keyed by question key.",
    )
    outline: dict[str, Any] | None = Field(
        default=None,
        description="Full outline payload once generated.",
    )
    chunks: dict[str, Any] = Field(
        default_factory=dict,
        description="Block-keyed ChunkState dicts managed by the chunks router.",
    )
    assets: list[str] = Field(
        default_factory=list,
        description="Paths or URLs of generated asset files.",
    )
    confidence_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-block reliability scores in the range 0.0–1.0.",
    )
    generation_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Measured end-to-end API cost in USD.",
        examples=[0.042],
    )
    error: str | None = Field(
        default=None,
        description="Human-readable error message if status is 'error'.",
    )
    track_id: str | None = Field(
        default=None,
        description="Parent track ID, if this session belongs to a track.",
    )
    session_number: int | None = Field(
        default=None,
        ge=1,
        description="1-based position of this session within its track.",
        examples=[1, 2],
    )


class SessionResponse(BaseModel):
    id: str = Field(
        description="Unique session identifier.", examples=["sess_abc123"]
    )
    status: SessionStatus = Field(description="Current lifecycle status.")
    language: str = Field(
        description="BCP-47 language code.", examples=["en", "nl"]
    )
    style_guide: str = Field(
        description="Name of the applied style guide.", examples=["default"]
    )
    created_at: datetime = Field(description="ISO-8601 creation timestamp.")
    updated_at: datetime = Field(description="ISO-8601 last-updated timestamp.")
