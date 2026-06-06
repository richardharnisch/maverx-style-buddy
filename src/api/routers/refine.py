"""Refinement endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas.refine import RefineJob, RefineRequest

router = APIRouter(prefix="/sessions", tags=["refine"])

_NOT_IMPLEMENTED = "Refinement pipeline not implemented yet."


@router.post(
    "/{session_id}/refine",
    response_model=RefineJob,
    status_code=202,
    summary="Queue a refinement request for a specific block",
)
def submit_refinement(
    session_id: str, body: RefineRequest, background_tasks: BackgroundTasks
) -> RefineJob:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{session_id}/refine",
    response_model=list[RefineJob],
    summary="List all refinement jobs for this session",
)
def list_refinements(session_id: str) -> list[RefineJob]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{session_id}/refine/{job_id}",
    response_model=RefineJob,
    summary="Get the status and result of a refinement job",
)
def get_refinement(session_id: str, job_id: str) -> RefineJob:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
