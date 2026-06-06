from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from src.constants import DEFAULT_LANGUAGE, DEFAULT_STYLE_GUIDE
from .session import SessionStatus


class TrackStatus(str, Enum):
    intake = "intake"
    intake_complete = "intake_complete"

    # sessions being set up and approved
    planning = "planning"  

    # all sessions outline-approved
    sessions_ready = "sessions_ready"  
    generating = "generating"
    ready = "ready"
    error = "error"


class CreateTrackRequest(BaseModel):
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
        examples=["default"],
    )


class Track(BaseModel):
    id: str = Field(
        description="Unique track identifier.", examples=["track_abc123"]
    )
    status: TrackStatus = Field(
        description="Current lifecycle status of the track."
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
    intake: dict[str, str] = Field(
        default_factory=dict,
        description="Accumulated track-level intake answers keyed by question key.",
    )
    backbone: str | None = Field(
        default=None,
        description="Narrative backbone shared across all sessions in this track.",
    )
    fictional_case: str | None = Field(
        default=None,
        description="Fictional case study or scenario used throughout the track.",
    )
    session_ids: list[str] = Field(
        default_factory=list,
        description="Ordered list of session IDs belonging to this track.",
    )
    assets: list[str] = Field(
        default_factory=list,
        description="Paths or URLs of generated track-level asset files.",
    )
    error: str | None = Field(
        default=None,
        description="Human-readable error message if status is 'error'.",
    )
    created_at: datetime = Field(
        description="ISO-8601 timestamp when the track was created."
    )
    updated_at: datetime = Field(
        description="ISO-8601 timestamp of the last update."
    )


class TrackAnswerRequest(BaseModel):
    answer: str = Field(
        min_length=1,
        description="The trainer's answer to the current track-level intake question.",
        examples=["We want a 3-day leadership programme for senior managers."],
    )


class TrackIntakeResponse(BaseModel):
    question_key: str | None = Field(
        default=None,
        description="Machine key for the current question; null when intake is complete.",
        examples=["track_goal"],
    )
    question: str | None = Field(
        default=None,
        description="Human-readable question text; null when intake is complete.",
    )
    progress: int = Field(
        ge=0,
        description="Number of questions answered so far.",
        examples=[1],
    )
    total: int = Field(
        ge=1,
        description="Total number of track intake questions.",
        examples=[4],
    )
    complete: bool = Field(
        description="True when all track intake questions have been answered."
    )
    pushback: str | None = Field(
        default=None,
        description="AI follow-up challenge or clarification prompt, if any.",
    )


class SessionSummary(BaseModel):
    session_id: str = Field(
        description="Session identifier.", examples=["sess_abc123"]
    )
    session_number: int = Field(
        ge=1,
        description="1-based position of this session within the track.",
        examples=[1],
    )
    status: SessionStatus = Field(
        description="Current lifecycle status of the session."
    )
    backbone_phase: str | None = Field(
        default=None,
        description="Narrative backbone phase assigned to this session.",
    )
