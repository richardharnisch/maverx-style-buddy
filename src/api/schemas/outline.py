from pydantic import BaseModel, Field


class SpeakerNotes(BaseModel):
    """Structured facilitation guide for the trainer — Business Case §4 (6 fields)."""

    aim: str = Field(default="", description="Learning aim for this block.")
    time_minutes: int = Field(
        default=0,
        ge=0,
        description="Planned duration in minutes.",
        examples=[10],
    )
    instructions: str = Field(
        default="", description="Step-by-step facilitation instructions."
    )
    key_discussion_points: list[str] = Field(
        default_factory=list,
        description="Talking points the trainer should raise during discussion.",
    )
    link_to_reality: str = Field(
        default="",
        description="Suggested real-world connection or anecdote.",
    )
    debrief_summary: str = Field(
        default="",
        description="Closing summary the trainer delivers at the end of the block.",
    )


class SlideBlock(BaseModel):
    """One block in the didactic arc (kick-off / theory / example / exercise / wrap-up)."""

    block: str = Field(
        min_length=1,
        description="Didactic block identifier.",
        examples=["theory", "exercise"],
    )
    title: str = Field(
        min_length=1,
        description="Slide block title shown as the section header.",
        examples=["Core Concepts"],
    )
    bullets: list[str] = Field(
        default_factory=list,
        description="Bullet-point content for the slide.",
    )
    speaker_notes: SpeakerNotes = Field(
        default_factory=SpeakerNotes,
        description="Structured facilitation guide for the trainer.",
    )
    estimated_minutes: int = Field(
        default=0,
        ge=0,
        description="Estimated time for this block in minutes.",
        examples=[15],
    )
    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="AI reliability score for this block in the range 0.0–1.0; populated during generation.",
        examples=[0.85],
    )


class Outline(BaseModel):
    title: str = Field(
        min_length=1,
        description="Title of the full training outline.",
        examples=["Effective Communication for Managers"],
    )
    total_minutes: int = Field(
        ge=0,
        description="Sum of all block durations in minutes.",
        examples=[90],
    )
    modules: list[SlideBlock] = Field(
        description="Ordered list of didactic blocks that make up the outline.",
    )


class OutlineEditRequest(BaseModel):
    outline: Outline = Field(
        description="The full updated outline to replace the current one."
    )


class OutlinePathRequest(BaseModel):
    """Choose which outline path to take before content is generated."""

    path: str = Field(
        pattern="^(trainer|research)$",
        description="Outline path to follow.",
        examples=["trainer", "research"],
    )
