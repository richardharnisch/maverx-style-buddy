"""Refinement endpoint — post-generation slide / section editing.

Lets a trainer say "rewrite the exercise block to be more hands-on"
or "shorten the theory section" without regenerating the whole deck.
Each refinement is a job — trainers can queue several and poll for results.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from .session import SessionStatus, get_session_or_404, _sessions

router = APIRouter(prefix="/sessions", tags=["refine"])

VALID_BLOCKS = {"kick-off", "theory", "example", "exercise", "wrap-up"}

# In-memory job store — keyed by session_id → job_id → job
_jobs: dict[str, dict[str, Any]] = {}


class RefinementJobStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class RefineRequest(BaseModel):
    target_block: str
    instruction: str
    scope: str = "slide"  # "slide" | "speaker_notes" | "both"


class RefineJob(BaseModel):
    job_id: str
    session_id: str
    target_block: str
    instruction: str
    scope: str
    status: RefinementJobStatus
    created_at: datetime
    updated_at: datetime
    result: dict[str, Any] | None = None
    error: str | None = None


@router.post(
    "/{session_id}/refine",
    response_model=RefineJob,
    status_code=202,
    summary="Queue a refinement request for a specific block",
)
def submit_refinement(
    session_id: str, body: RefineRequest, background_tasks: BackgroundTasks
) -> RefineJob:
    session = get_session_or_404(session_id)

    if session.status not in (SessionStatus.ready, SessionStatus.refining):
        raise HTTPException(
            status_code=409,
            detail="Assets must be in 'ready' state before refining",
        )

    if body.target_block not in VALID_BLOCKS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid block '{body.target_block}'. Must be one of: {sorted(VALID_BLOCKS)}",
        )

    now = datetime.now(timezone.utc)
    job = RefineJob(
        job_id=str(uuid.uuid4()),
        session_id=session_id,
        target_block=body.target_block,
        instruction=body.instruction,
        scope=body.scope,
        status=RefinementJobStatus.pending,
        created_at=now,
        updated_at=now,
    )

    _jobs.setdefault(session_id, {})[job.job_id] = job.model_dump()

    session.status = SessionStatus.refining
    session.updated_at = now
    _sessions[session_id] = session

    background_tasks.add_task(_run_refinement, session_id, job.job_id, body)

    return job


@router.get(
    "/{session_id}/refine",
    response_model=list[RefineJob],
    summary="List all refinement jobs for this session",
)
def list_refinements(session_id: str) -> list[RefineJob]:
    get_session_or_404(session_id)
    jobs = _jobs.get(session_id, {})
    return [RefineJob(**j) for j in jobs.values()]


@router.get(
    "/{session_id}/refine/{job_id}",
    response_model=RefineJob,
    summary="Get the status and result of a refinement job",
)
def get_refinement(session_id: str, job_id: str) -> RefineJob:
    get_session_or_404(session_id)
    job_data = _jobs.get(session_id, {}).get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return RefineJob(**job_data)


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------


def _run_refinement(session_id: str, job_id: str, body: RefineRequest) -> None:
    job_data = _jobs.get(session_id, {}).get(job_id)
    if not job_data:
        return

    job_data["status"] = RefinementJobStatus.running
    job_data["updated_at"] = datetime.now(timezone.utc)

    try:
        # TODO: call agent loop with:
        #   - current slide XML for target_block
        #   - body.instruction
        #   - body.scope
        # Then re-export the updated .pptx to disk

        job_data["result"] = {
            "block": body.target_block,
            "message": "Refinement applied (stub)",
        }
        job_data["status"] = RefinementJobStatus.done

        # Flip session back to ready once no more running jobs remain
        session = _sessions.get(session_id)
        if session:
            still_running = any(
                j["status"]
                in (RefinementJobStatus.pending, RefinementJobStatus.running)
                for j in _jobs.get(session_id, {}).values()
                if j["job_id"] != job_id
            )
            if not still_running:
                session.status = SessionStatus.ready
                session.updated_at = datetime.now(timezone.utc)
                _sessions[session_id] = session

    except Exception as exc:  # noqa: BLE001
        job_data["status"] = RefinementJobStatus.failed
        job_data["error"] = str(exc)

    job_data["updated_at"] = datetime.now(timezone.utc)
    _jobs[session_id][job_id] = job_data
