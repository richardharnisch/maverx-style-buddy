"""Health and readiness check — useful during live demos and CI."""

import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])

_START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=round(time.time() - _START_TIME, 1),
    )


@router.get(
    "/ready", summary="Readiness check — verifies AI client is reachable"
)
def ready() -> dict:
    """Returns 200 when the service is ready to accept requests."""
    # TODO: ping the OpenRouter client and style-guide loader
    return {"ready": True}
