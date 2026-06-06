"""Certification / multi-level track endpoints.

A REST surface over the same engine as the chat pipeline: collect intake, then
generate + build a multi-session training (Tier 2 module or Tier 3 track). Track
artifacts are written to ``OUTPUT_DIR/<track_id>`` and are downloadable through
the existing files router (``/sessions/<track_id>/files/...``), which simply
serves that directory.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.agent.pipeline import build_training, run_intake
from src.api.routers.session import SessionStatus
from src.constants import DEFAULT_MODEL, INTAKE_FIELDS, OUTPUT_DIR
from ..schemas.track import (
    CreateTrackRequest,
    SessionSummary,
    Track,
    TrackAnswerRequest,
    TrackIntakeResponse,
    TrackStatus,
)

router = APIRouter(prefix="/tracks", tags=["track"])

# In-memory store, mirroring the session router pattern.
_tracks: dict[str, Track] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_track_or_404(track_id: str) -> Track:
    track = _tracks.get(track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Track '{track_id}' not found")
    return track


def _intake_state(track: Track) -> TrackIntakeResponse:
    answered = [f for f in INTAKE_FIELDS if f["key"] in track.intake]
    nxt = next((f for f in INTAKE_FIELDS if f["key"] not in track.intake), None)
    return TrackIntakeResponse(
        question_key=nxt["key"] if nxt else None,
        question=nxt["question"] if nxt else None,
        progress=len(answered),
        total=len(INTAKE_FIELDS),
        complete=nxt is None,
    )


@router.post("", status_code=201, response_model=Track, summary="Create a certification track")
def create_track(body: CreateTrackRequest = CreateTrackRequest()) -> Track:
    now = _now()
    track = Track(
        id=f"track_{uuid.uuid4().hex[:12]}",
        status=TrackStatus.intake,
        language=body.language,
        style_guide=body.style_guide,
        created_at=now,
        updated_at=now,
    )
    _tracks[track.id] = track
    return track


@router.get("/{track_id}", response_model=Track, summary="Get full track state")
def get_track(track_id: str) -> Track:
    return _get_track_or_404(track_id)


@router.get("/{track_id}/intake", response_model=TrackIntakeResponse)
def get_track_intake(track_id: str) -> TrackIntakeResponse:
    return _intake_state(_get_track_or_404(track_id))


@router.post("/{track_id}/intake", response_model=TrackIntakeResponse)
def submit_track_intake(track_id: str, body: TrackAnswerRequest) -> TrackIntakeResponse:
    track = _get_track_or_404(track_id)
    complete, reply, _cost, intake = run_intake(
        track.intake, body.answer, DEFAULT_MODEL
    )
    track.intake = intake
    track.status = TrackStatus.intake_complete if complete else TrackStatus.intake
    track.updated_at = _now()
    state = _intake_state(track)
    state.pushback = None if complete else reply
    return state


@router.get("/{track_id}/sessions", response_model=list[SessionSummary])
def list_track_sessions(track_id: str) -> list[SessionSummary]:
    track = _get_track_or_404(track_id)
    return [
        SessionSummary(
            session_id=sid,
            session_number=index,
            status=SessionStatus.ready
            if track.status == TrackStatus.ready
            else SessionStatus.generating,
        )
        for index, sid in enumerate(track.session_ids, start=1)
    ]


def _run_generation(track_id: str, model: str) -> None:
    track = _tracks.get(track_id)
    if not track:
        return
    try:
        out_dir = OUTPUT_DIR / track.id
        build = build_training(track.intake, track.language, out_dir, model)
        sessions = build.plan.get("sessions", [])
        track.session_ids = [f"{track.id}-s{s['session_n']:02d}" for s in sessions]
        track.backbone = build.plan.get("training", {}).get("scope")
        track.fictional_case = build.plan.get("intake_summary", {}).get("case_sector")
        track.assets = [
            str(p) for p in build.result.deck_paths + build.result.doc_paths
        ]
        track.status = TrackStatus.ready
    except Exception as exc:  # noqa: BLE001 — surface as track error state
        track.status = TrackStatus.error
        track.error = str(exc)
    finally:
        track.updated_at = _now()


@router.post(
    "/{track_id}/generate",
    summary="Generate all sessions in sequence, then the track overview",
)
def generate_track(track_id: str, background_tasks: BackgroundTasks) -> dict[str, str]:
    track = _get_track_or_404(track_id)
    missing = [f["key"] for f in INTAKE_FIELDS if f["key"] not in track.intake]
    if missing:
        raise HTTPException(
            status_code=409,
            detail=f"Intake incomplete; still need: {', '.join(missing)}",
        )
    track.status = TrackStatus.generating
    track.error = None
    track.updated_at = _now()
    background_tasks.add_task(_run_generation, track.id, DEFAULT_MODEL)
    return {"track_id": track.id, "status": track.status.value}


@router.get("/{track_id}/assets", summary="List track-level generated files")
def get_track_assets(track_id: str) -> dict:
    track = _get_track_or_404(track_id)
    base = (OUTPUT_DIR / track.id).resolve()
    files = []
    if base.is_dir():
        for path in sorted(base.iterdir()):
            if path.is_file() and path.suffix.lower() in {".pptx", ".docx", ".json"}:
                files.append(
                    {
                        "filename": path.name,
                        "size_bytes": path.stat().st_size,
                        # Served by the files router, which reads OUTPUT_DIR/<id>.
                        "download_url": f"/sessions/{track.id}/files/{path.name}",
                    }
                )
    return {"track_id": track.id, "status": track.status.value, "files": files}


@router.post(
    "/{track_id}/sessions/{session_id}",
    summary="Attach an existing session id to this track (bookkeeping)",
)
def attach_session(track_id: str, session_id: str) -> dict:
    track = _get_track_or_404(track_id)
    if session_id not in track.session_ids:
        track.session_ids.append(session_id)
        track.updated_at = _now()
    return {"track_id": track.id, "session_ids": track.session_ids}
