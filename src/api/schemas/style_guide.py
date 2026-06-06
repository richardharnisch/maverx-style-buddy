from pydantic import BaseModel, Field


class StyleGuideInfo(BaseModel):
    name: str = Field(
        min_length=1,
        description="Unique identifier / filename stem for this style guide.",
        examples=["default", "acme-corp"],
    )
    has_master_pptx: bool = Field(
        description="True when a branded master PPTX template is available for this guide.",
    )
    description: str = Field(
        default="",
        description="Human-readable summary of the style guide's purpose or audience.",
        examples=["Default Maverx corporate style"],
    )


class StyleGuideListResponse(BaseModel):
    available: list[StyleGuideInfo] = Field(
        description="All style guides currently available on the server.",
    )
