"""Outline endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, HTTPException

from ..schemas.outline import Outline, OutlineEditRequest, OutlinePathRequest

router = APIRouter(prefix="/sessions", tags=["outline"])

_NOT_IMPLEMENTED = "Outline pipeline not implemented yet."


@router.post(
    "/{session_id}/outline/path",
    summary="Choose outline path: 'trainer' or 'research'",
)
def set_outline_path(
    session_id: str, body: OutlinePathRequest
) -> dict[str, str]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{session_id}/outline/generate",
    response_model=Outline,
    summary="Generate a training outline via the research agent",
)
def generate_outline(session_id: str) -> Outline:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{session_id}/outline",
    response_model=Outline,
    summary="Get the current outline",
)
def get_outline(session_id: str) -> Outline:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.put(
    "/{session_id}/outline",
    response_model=Outline,
    summary="Upload a trainer-supplied outline, or edit a generated one",
)
def set_outline(session_id: str, body: OutlineEditRequest) -> Outline:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{session_id}/outline/approve",
    summary="Approve the outline — unlocks asset generation",
)
def approve_outline(session_id: str) -> dict[str, str]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
