from pydantic import BaseModel, Field


class AssetStatus(BaseModel):
    status: str = Field(
        description="Generation pipeline status.",
        examples=["ready", "generating", "error"],
    )
    assets: list[str] = Field(
        description="Paths or URLs of generated asset files.",
        examples=[["output/session_1.pptx"]],
    )
    message: str | None = Field(
        default=None,
        description="Optional human-readable status detail or error message.",
    )
    generation_cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Measured end-to-end API cost in USD.",
        examples=[0.042],
    )
    confidence_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-block reliability scores in the range 0.0–1.0.",
    )
