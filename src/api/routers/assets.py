"""Asset generation endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas.assets import AssetStatus

router = APIRouter(prefix="/sessions", tags=["assets"])

_NOT_IMPLEMENTED = "Asset generation pipeline not implemented yet."


@router.post(
    "/{session_id}/assets/generate",
    response_model=AssetStatus,
    summary="Trigger full asset generation (pptx + pre-bite + post-bite)",
)
def generate_assets(
    session_id: str, background_tasks: BackgroundTasks
) -> AssetStatus:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{session_id}/assets",
    response_model=AssetStatus,
    summary="Get generation status, file list, cost, and confidence scores",
)
def get_assets(session_id: str) -> AssetStatus:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
