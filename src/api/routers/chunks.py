"""Chunk endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas.chunks import ChunkAdjustRequest, ChunkListResponse, ChunkState

router = APIRouter(prefix="/sessions", tags=["chunks"])

_NOT_IMPLEMENTED = "Chunk pipeline not implemented yet."


@router.get(
    "/{session_id}/chunks",
    response_model=ChunkListResponse,
    summary="List all blocks with their chunk confirmation status",
)
def list_chunks(session_id: str) -> ChunkListResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{session_id}/chunks/{block}/propose",
    response_model=ChunkState,
    summary="Generate an AI proposal for a specific block",
)
def propose_chunk(session_id: str, block: str) -> ChunkState:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.put(
    "/{session_id}/chunks/{block}",
    response_model=ChunkState,
    summary="Submit trainer adjustments to a proposed block",
)
def adjust_chunk(
    session_id: str, block: str, body: ChunkAdjustRequest
) -> ChunkState:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{session_id}/chunks/{block}/approve",
    response_model=ChunkState,
    status_code=202,
    summary="Approve a block proposal and queue its slide generation",
)
def approve_chunk(
    session_id: str, block: str, background_tasks: BackgroundTasks
) -> ChunkState:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
