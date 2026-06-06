from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas.chunks import (
    ChunkAdjustRequest,
    ChunkListResponse,
    ChunkProposal,
    ChunkState,
    ChunkStatus,
)
from src.constants import ORDERED_BLOCKS
from ..schemas.session import SessionStatus
from .session import _sessions, get_session_or_404

router = APIRouter(prefix="/sessions", tags=["chunks"])


def _load_chunks(session_id: str) -> dict[str, ChunkState]:
    session = get_session_or_404(session_id)
    if not session.chunks:
        session.chunks = {
            block: ChunkState(block=block).model_dump()
            for block in ORDERED_BLOCKS
        }
        _sessions[session_id] = session
    return {
        block: ChunkState(**state) for block, state in session.chunks.items()
    }


def _save_chunk(session_id: str, chunk: ChunkState) -> None:
    session = _sessions[session_id]
    session.chunks[chunk.block] = chunk.model_dump()
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session


@router.get(
    "/{session_id}/chunks",
    response_model=ChunkListResponse,
    summary="List all blocks with their chunk confirmation status",
)
def list_chunks(session_id: str) -> ChunkListResponse:
    chunks = _load_chunks(session_id)
    ordered = [chunks[b] for b in ORDERED_BLOCKS if b in chunks]
    all_done = all(c.status == ChunkStatus.done for c in ordered)
    return ChunkListResponse(
        session_id=session_id, chunks=ordered, all_done=all_done
    )


@router.post(
    "/{session_id}/chunks/{block}/propose",
    response_model=ChunkState,
    summary="Generate an AI proposal for a specific block — trainer reviews before approving",
)
def propose_chunk(session_id: str, block: str) -> ChunkState:
    session = get_session_or_404(session_id)

    if session.status != SessionStatus.outline_approved:
        raise HTTPException(
            status_code=409,
            detail="Outline must be approved before proposing chunks",
        )
    if block not in ORDERED_BLOCKS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid block '{block}'. Must be one of: {ORDERED_BLOCKS}",
        )

    chunks = _load_chunks(session_id)
    chunk = chunks[block]

    if chunk.status == ChunkStatus.done:
        raise HTTPException(
            status_code=409, detail=f"Block '{block}' is already done"
        )

    # TODO: call agent loop with session.outline and session.intake to generate proposal
    proposal = ChunkProposal(
        block=block,
        approach=f"[stub] Proposed approach for the '{block}' block",
        slide_titles=[
            f"{block.replace('-', ' ').title()} — slide 1",
            f"{block.replace('-', ' ').title()} — slide 2",
        ],
        estimated_minutes=20,
        exercise_description="[stub] Exercise description"
        if block == "exercise"
        else None,
    )
    chunk.proposal = proposal
    chunk.status = ChunkStatus.proposed
    _save_chunk(session_id, chunk)
    return chunk


@router.put(
    "/{session_id}/chunks/{block}",
    response_model=ChunkState,
    summary="Submit trainer adjustments to a proposed block",
)
def adjust_chunk(
    session_id: str, block: str, body: ChunkAdjustRequest
) -> ChunkState:
    if block not in ORDERED_BLOCKS:
        raise HTTPException(status_code=422, detail=f"Invalid block '{block}'")

    chunks = _load_chunks(session_id)
    chunk = chunks[block]

    if chunk.status not in (ChunkStatus.proposed, ChunkStatus.adjusted):
        raise HTTPException(
            status_code=409,
            detail=f"Block must be in 'proposed' state before adjusting (current: {chunk.status})",
        )

    chunk.trainer_notes = body.trainer_notes
    chunk.status = ChunkStatus.adjusted
    _save_chunk(session_id, chunk)
    return chunk


@router.post(
    "/{session_id}/chunks/{block}/approve",
    response_model=ChunkState,
    status_code=202,
    summary="Approve a block proposal and queue its slide generation",
)
def approve_chunk(
    session_id: str, block: str, background_tasks: BackgroundTasks
) -> ChunkState:
    if block not in ORDERED_BLOCKS:
        raise HTTPException(status_code=422, detail=f"Invalid block '{block}'")

    chunks = _load_chunks(session_id)
    chunk = chunks[block]

    if chunk.status not in (ChunkStatus.proposed, ChunkStatus.adjusted):
        raise HTTPException(
            status_code=409,
            detail=f"Block must be proposed or adjusted before approving (current: {chunk.status})",
        )

    chunk.status = ChunkStatus.approved
    _save_chunk(session_id, chunk)

    background_tasks.add_task(_generate_chunk_slides, session_id, block)
    return chunk


def _generate_chunk_slides(session_id: str, block: str) -> None:
    session = _sessions.get(session_id)
    if not session:
        return

    chunk_data = session.chunks.get(block)
    if not chunk_data:
        return

    chunk = ChunkState(**chunk_data)
    chunk.status = ChunkStatus.generating
    _save_chunk(session_id, chunk)

    try:
        # TODO: call skills pipeline for this block only:
        #   1. For each slide_title in chunk.proposal.slide_titles:
        #        add_slide(presentation_id, layout, block, title, bullets, speaker_notes)
        #   2. Record per-block confidence_score → session.confidence_scores[block]

        chunk.status = ChunkStatus.done
        _save_chunk(session_id, chunk)

        # Flip session to ready once all blocks are done
        all_done = all(
            ChunkState(**s).status == ChunkStatus.done
            for s in _sessions[session_id].chunks.values()
        )
        if all_done:
            _sessions[session_id].status = SessionStatus.ready
            _sessions[session_id].updated_at = datetime.now(timezone.utc)

    except Exception as exc:
        session = _sessions.get(session_id)
        if session:
            session.status = SessionStatus.error
            session.error = str(exc)
            session.updated_at = datetime.now(timezone.utc)
            _sessions[session_id] = session
