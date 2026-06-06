from typing import Any
from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    answer: str = Field(
        min_length=1,
        description="The trainer's answer to the current intake question.",
        examples=["We want to improve cross-team communication."],
    )


class IntakeResponse(BaseModel):
    question_key: str | None = Field(
        default=None,
        description="Machine key for the current question; null when intake is complete.",
        examples=["goal"],
    )
    question: str | None = Field(
        default=None,
        description="Human-readable question text; null when intake is complete.",
        examples=["What is the primary learning goal of this training?"],
    )
    progress: int = Field(
        ge=0,
        description="Number of questions answered so far.",
        examples=[2],
    )
    total: int = Field(
        ge=1,
        description="Total number of intake questions.",
        examples=[5],
    )
    complete: bool = Field(
        description="True when all intake questions have been answered."
    )
    pushback: str | None = Field(
        default=None,
        description="AI follow-up challenge or clarification prompt, if any.",
    )


class IntakeStateResponse(BaseModel):
    answers: dict[str, str] = Field(
        description="All answers collected so far, keyed by question key.",
        examples=[{"goal": "Improve communication", "audience": "Managers"}],
    )
    next_question: dict[str, Any] | None = Field(
        default=None,
        description="Next unanswered question descriptor; null if intake is complete.",
    )
    complete: bool = Field(
        description="True when all intake questions have been answered."
    )
