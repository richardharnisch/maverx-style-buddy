import uvicorn
from fastapi import FastAPI

from src.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION, HOST, PORT
from .routers import (
    assets,
    chunks,
    files,
    health,
    intake,
    outline,
    refine,
    session,
    style_guides,
    track,
)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.include_router(health.router)
app.include_router(session.router)
app.include_router(intake.router)
app.include_router(outline.router)
app.include_router(chunks.router)
app.include_router(assets.router)
app.include_router(files.router)
app.include_router(refine.router)
app.include_router(track.router)
app.include_router(style_guides.router)


def main() -> None:
    uvicorn.run("src.api.router:app", host=HOST, port=PORT)


def dev() -> None:
    uvicorn.run("src.api.router:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()
