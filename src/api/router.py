"""Top-level API router and application entry point."""

import uvicorn
from fastapi import FastAPI

from .routers import (
    assets,
    files,
    health,
    intake,
    outline,
    refine,
    session,
    track,
)

app = FastAPI(
    title="Maverx Style Buddy",
    description="AI-powered training builder: intake → outline → .pptx in Maverx house style",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(session.router)
app.include_router(intake.router)
app.include_router(outline.router)
app.include_router(assets.router)
app.include_router(files.router)
app.include_router(refine.router)
app.include_router(track.router)


def main() -> None:
    uvicorn.run("src.api.router:app", host="0.0.0.0", port=8000)


def dev() -> None:
    uvicorn.run("src.api.router:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
