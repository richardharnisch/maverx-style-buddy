from typing import Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from ..schemas.style_guide import StyleGuideInfo, StyleGuideListResponse

router = APIRouter(prefix="/style-guides", tags=["style-guides"])


def _loader():
    """Lazy import — raises 501 until style_guides/loader.py is implemented."""
    try:
        from src.style_guides import loader

        return loader
    except (ImportError, AttributeError):
        raise HTTPException(
            status_code=501, detail="style_guides/loader.py not yet implemented"
        )


@router.get(
    "",
    response_model=StyleGuideListResponse,
    summary="List all available style guides",
)
def list_style_guides() -> StyleGuideListResponse:
    loader = _loader()
    available: list[StyleGuideInfo] = []
    for name in loader.list_available():
        try:
            guide = loader.load(name)
            available.append(
                StyleGuideInfo(
                    name=name,
                    has_master_pptx=getattr(guide, "master_pptx", None)
                    is not None,
                    description=getattr(guide, "description", ""),
                )
            )
        except Exception:
            available.append(StyleGuideInfo(name=name, has_master_pptx=False))
    return StyleGuideListResponse(available=available)


@router.get(
    "/{name}",
    summary="Get a style guide definition",
)
def get_style_guide(name: str) -> Any:
    loader = _loader()
    try:
        return loader.load(name)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Style guide '{name}' not found"
        )


@router.put(
    "/{name}",
    summary="Upload or replace a style guide via PPTX master template",
    description=(
        "Accepts a .pptx file. The style and branding are extracted from the master template. "
        "All active sessions that reference this style guide will use the new definition "
        "on their next generation run."
    ),
)
async def upload_style_guide(name: str, file: UploadFile = File(...)) -> Any:
    if not (file.filename or "").lower().endswith(".pptx"):
        raise HTTPException(status_code=422, detail="Only .pptx files are accepted")
    loader = _loader()
    raw = await file.read()
    try:
        guide = loader.ingest_pptx(name, raw)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid PPTX: {exc}")
    return guide
