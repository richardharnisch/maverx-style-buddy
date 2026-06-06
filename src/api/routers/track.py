"""Certification track endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..schemas.track import (
    CreateTrackRequest,
    SessionSummary,
    Track,
    TrackAnswerRequest,
    TrackIntakeResponse,
)

router = APIRouter(prefix="/tracks", tags=["track"])

_NOT_IMPLEMENTED = "Track pipeline not implemented yet."


@router.post(
    "",
    status_code=201,
    response_model=Track,
    summary="Create a certification track",
)
def create_track(body: CreateTrackRequest = CreateTrackRequest()) -> Track:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{track_id}", response_model=Track, summary="Get full track state")
def get_track(track_id: str) -> Track:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{track_id}/intake", response_model=TrackIntakeResponse)
def get_track_intake(track_id: str) -> TrackIntakeResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post("/{track_id}/intake", response_model=TrackIntakeResponse)
def submit_track_intake(
    track_id: str, body: TrackAnswerRequest
) -> TrackIntakeResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{track_id}/sessions", response_model=list[SessionSummary])
def list_track_sessions(track_id: str) -> list[SessionSummary]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{track_id}/sessions/{session_id}",
    summary="Attach an existing session to this track",
)
def attach_session(track_id: str, session_id: str) -> dict[str, Any]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post(
    "/{track_id}/generate",
    summary="Generate all sessions in sequence, then the track overview",
)
def generate_track(
    track_id: str, background_tasks: BackgroundTasks
) -> dict[str, str]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{track_id}/assets", summary="List track-level assets (overview document)"
)
def get_track_assets(track_id: str) -> dict[str, Any]:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
