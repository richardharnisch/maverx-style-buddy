from enum import Enum
from pydantic import BaseModel, Field


class ChunkStatus(str, Enum):
    pending = "pending"
    proposed = "proposed"
    adjusted = "adjusted"
    approved = "approved"
    generating = "generating"
    done = "done"


class ChunkProposal(BaseModel):
    """AI's proposed approach for a single didactic block, shown to trainer before building."""

    block: str = Field(
        min_length=1,
        description="Didactic block identifier.",
        examples=["theory", "exercise"],
    )
    approach: str = Field(
        min_length=1,
        description="Short description of the proposed pedagogical approach.",
        examples=[
            "Use a case-study to introduce the concept, then discuss in pairs."
        ],
    )
    slide_titles: list[str] = Field(
        description="Proposed slide titles for this block.",
        examples=[["Introduction", "Key Concepts", "Discussion"]],
    )
    estimated_minutes: int = Field(
        ge=0,
        description="Estimated time for this block in minutes.",
        examples=[15],
    )
    exercise_description: str | None = Field(
        default=None,
        description="Exercise prompt or instructions; only populated for the exercise block.",
    )


class ChunkState(BaseModel):
    block: str = Field(
        min_length=1,
        description="Didactic block identifier.",
        examples=["theory"],
    )
    status: ChunkStatus = Field(
        default=ChunkStatus.pending,
        description="Current processing status of this chunk.",
    )
    proposal: ChunkProposal | None = Field(
        default=None,
        description="AI proposal for this chunk, available after the propose step.",
    )
    trainer_notes: str | None = Field(
        default=None,
        description="Free-text feedback from the trainer used to adjust the proposal.",
    )


class ChunkAdjustRequest(BaseModel):
    trainer_notes: str = Field(
        min_length=1,
        description="Free-text instructions for adjusting the chunk proposal.",
        examples=[
            "Make the exercise more interactive and add a reflection step."
        ],
    )


class ChunkListResponse(BaseModel):
    session_id: str = Field(
        description="Session this chunk list belongs to.",
        examples=["sess_abc123"],
    )
    chunks: list[ChunkState] = Field(
        description="All chunks for the session, in didactic order.",
    )
    all_done: bool = Field(
        description="True when every chunk has reached the 'done' status.",
    )
