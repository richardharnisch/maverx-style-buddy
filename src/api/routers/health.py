import os
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.constants import APP_VERSION

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
    summary="Readiness check — verifies AI client credentials",
)
def ready() -> dict:
    errors: list[str] = []

    if not os.getenv("OPENROUTER_API_KEY"):
        errors.append("OPENROUTER_API_KEY is not set")

    # TODO: add a style guide / template catalog readiness check once the
    # deck-generation pipeline lands.

    if errors:
        raise HTTPException(
            status_code=503, detail={"ready": False, "errors": errors}
        )

    return {"ready": True}
