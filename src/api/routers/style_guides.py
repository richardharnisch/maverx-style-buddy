"""Style guide endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas.style_guide import StyleGuideListResponse

router = APIRouter(prefix="/style-guides", tags=["style-guides"])

_NOT_IMPLEMENTED = "Style guide loader not implemented yet."


@router.get(
    "",
    response_model=StyleGuideListResponse,
    summary="List all available style guides",
)
def list_style_guides() -> StyleGuideListResponse:
    # TODO: reimplement once the style guide loader lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{name}", summary="Get a style guide definition")
def get_style_guide(name: str) -> Any:
    # TODO: reimplement once the style guide loader lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.put(
    "/{name}",
    summary="Upload or replace a style guide via PPTX master template",
)
async def upload_style_guide(name: str, file: UploadFile = File(...)) -> Any:
    # TODO: reimplement once the style guide loader lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
