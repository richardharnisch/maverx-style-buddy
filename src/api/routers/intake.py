"""Intake endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, HTTPException

from ..schemas.intake import AnswerRequest, IntakeResponse, IntakeStateResponse

router = APIRouter(prefix="/sessions", tags=["intake"])

_NOT_IMPLEMENTED = "Intake pipeline not implemented yet."


@router.get(
    "/{session_id}/intake",
    response_model=IntakeStateResponse,
    summary="Get current intake state",
)
def get_intake(session_id: str) -> IntakeStateResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{session_id}/intake",
    response_model=IntakeResponse,
    summary="Submit an intake answer",
)
def submit_intake_answer(
    session_id: str, body: AnswerRequest
) -> IntakeResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
