from pydantic import BaseModel, Field


class GenerateImageRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        description="Description of the image to generate.",
        examples=["A flat illustration of a team reviewing a dashboard."],
    )
    size: str = Field(
        default="1024x1024",
        description="Requested image dimensions, WIDTHxHEIGHT.",
        examples=["1024x1024", "1536x1024"],
    )
    style: str | None = Field(
        default=None,
        description="Optional style hint (e.g. 'maverx', 'flat', 'photo').",
        examples=["maverx"],
    )


class GenerateImageResponse(BaseModel):
    prompt: str = Field(description="Echo of the prompt used.")
    image_b64: str | None = Field(
        default=None,
        description="Base64-encoded PNG of the generated image.",
    )
    image_url: str | None = Field(
        default=None,
        description="URL to the generated image, if hosted.",
    )
    placeholder: bool = Field(
        default=True,
        description="True while the image generator is stubbed.",
    )
