import os
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.constants import APP_VERSION, DEFAULT_STYLE_GUIDE

router = APIRouter(tags=["health"])

_START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str = APP_VERSION


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=round(time.time() - _START_TIME, 1),
    )


@router.get(
    "/ready",
    summary="Readiness check — verifies AI client credentials and style guide loader",
)
def ready() -> dict:
    errors: list[str] = []

    if not os.getenv("OPENROUTER_API_KEY"):
        errors.append("OPENROUTER_API_KEY is not set")

    try:
        from src.style_guides.loader import load

        load(DEFAULT_STYLE_GUIDE)
    except FileNotFoundError:
        errors.append(
            f"'{DEFAULT_STYLE_GUIDE}' style guide not found in style_guides/ — upload {DEFAULT_STYLE_GUIDE}.pptx"
        )
    except Exception as exc:
        errors.append(f"Style guide load error: {exc}")

    if errors:
        raise HTTPException(
            status_code=503, detail={"ready": False, "errors": errors}
        )

    return {"ready": True}
