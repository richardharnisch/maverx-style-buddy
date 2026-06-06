from pydantic import BaseModel, Field


class Template(BaseModel):
    template_id: str = Field(
        description="Stable template identifier.",
        examples=["01-deck-title"],
    )
    title: str = Field(
        description="Human-readable template name.",
        examples=["Deck Title"],
    )
    preview_url: str = Field(
        description="API path to the template's preview image.",
        examples=["/templates/01-deck-title/preview"],
    )


class TemplatesResponse(BaseModel):
    templates: list[Template]


class UploadTemplateResponse(BaseModel):
    template_id: str = Field(description="Identifier assigned to the upload.")
    filename: str = Field(description="Original filename of the upload.")
    accepted: bool = Field(
        default=True, description="Whether the upload was accepted."
    )
    detail: str = Field(
        default="Upload received (stub — not yet persisted).",
        description="Human-readable status note.",
    )
