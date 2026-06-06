from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class RefinementJobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class RefineRequest(BaseModel):
    target_block: str = Field(
        min_length=1,
        description="Didactic block to refine.",
        examples=["theory"],
    )
    instruction: str = Field(
        min_length=1,
        description="Natural-language instruction describing the desired change.",
        examples=["Shorten the bullet points to three words each."],
    )
    scope: str = Field(
        default="both",
        pattern="^(slide|speaker_notes|both)$",
        description="Which parts of the block to refine.",
        examples=["both", "slide", "speaker_notes"],
    )


class RefineJob(BaseModel):
    job_id: str = Field(
        description="Unique refinement job identifier.", examples=["job_xyz789"]
    )
    session_id: str = Field(
        description="Session this job belongs to.", examples=["sess_abc123"]
    )
    target_block: str = Field(
        description="Block being refined.", examples=["theory"]
    )
    instruction: str = Field(description="Refinement instruction as submitted.")
    scope: str = Field(
        description="Scope of the refinement.",
        examples=["both", "slide", "speaker_notes"],
    )
    status: RefinementJobStatus = Field(description="Current job status.")
    created_at: datetime = Field(
        description="ISO-8601 timestamp when the job was created."
    )
    updated_at: datetime = Field(
        description="ISO-8601 timestamp of the last status update."
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="Refined block payload; available when status is 'done'.",
    )
    error: str | None = Field(
        default=None,
        description="Error detail; populated when status is 'failed'.",
    )
