import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.constants import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    HOST,
    PORT,
)
from .routers import (
    chat,
    files,
    health,
    images,
    session,
    style_guides,
    templates,
    track,
)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.include_router(health.router)
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(templates.router)
app.include_router(images.router)
app.include_router(files.router)
app.include_router(track.router)
app.include_router(style_guides.router)


class ModelsResponse(BaseModel):
    models: list[str]
    default: str


@app.get("/models", response_model=ModelsResponse, tags=["meta"])
def list_models() -> ModelsResponse:
    """Hardcoded model list surfaced in the Settings page."""
    return ModelsResponse(models=AVAILABLE_MODELS, default=DEFAULT_MODEL)


def main() -> None:
    uvicorn.run("src.api.router:app", host=HOST, port=PORT)


def dev() -> None:
    uvicorn.run("src.api.router:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()
