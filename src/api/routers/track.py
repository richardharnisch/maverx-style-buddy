"""Track router — Tier 3 Certification Track.

A Track owns an ordered sequence of Sessions sharing a backbone
(e.g. DMAIC), a fictional business case, and cross-session continuity:
post-bite of session N feeds into the pre-bite of session N+1.

State machine:
  intake → intake_complete → planning → sessions_ready
  → generating → ready → error
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from .assets import run_generation
from .session import Session, SessionStatus, _sessions, get_session_or_404

router = APIRouter(prefix="/tracks", tags=["track"])

OUTPUT_DIR = Path("outputs")

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_tracks: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TrackStatus(str, Enum):
    intake = "intake"
    intake_complete = "intake_complete"
    planning = "planning"  # sessions being set up and approved
    sessions_ready = "sessions_ready"  # all sessions outline-approved
    generating = "generating"
    ready = "ready"
    error = "error"


class Track(BaseModel):
    id: str
    status: TrackStatus
    intake: dict[str, str] = {}
    backbone: str | None = None  # e.g. DMAIC, ADDIE
    fictional_case: str | None = None
    session_ids: list[str] = []  # ordered
    assets: list[str] = []  # track-level files (overview.docx)
    error: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Track-level intake (5 questions mirroring the per-session intake)
# ---------------------------------------------------------------------------

TRACK_INTAKE_QUESTIONS: list[dict[str, Any]] = [
    {
        "key": "programme_topic",
        "question": "What is the certification programme topic or skill domain?",
        "why": "Defines the scope of the entire track",
        "vague_signals": ["something", "stuff", "general"],
    },
    {
        "key": "backbone",
        "question": (
            "What structural backbone should the programme follow? "
            "(e.g. DMAIC, ADDIE, Lean, Agile, custom — or describe your own)"
        ),
        "why": "Determines how sessions connect and build on each other",
        "vague_signals": ["any", "whatever", "something", "unsure"],
    },
    {
        "key": "structure",
        "question": "How many sessions, and how long is each? (e.g. '8 sessions of 2 hours')",
        "why": "Sets the total scope and pacing of the certification track",
        "vague_signals": ["some", "a few", "many"],
    },
    {
        "key": "fictional_case",
        "question": (
            "Describe the fictional business case that will run through all sessions. "
            "Include company name, industry, and the central problem participants will solve."
        ),
        "why": "Creates the narrative thread — participants build on this case each session",
        "vague_signals": ["a company", "some business", "any case"],
    },
    {
        "key": "certification_objective",
        "question": (
            "What is the overarching certification objective — "
            "what will participants be able to do upon completion?"
        ),
        "why": "Anchors all session-level learning objectives",
        "vague_signals": ["learn", "understand", "know about"],
    },
]


class TrackAnswerRequest(BaseModel):
    answer: str


class TrackIntakeResponse(BaseModel):
    question_key: str | None
    question: str | None
    progress: int
    total: int
    complete: bool
    pushback: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_track_or_404(track_id: str) -> dict[str, Any]:
    track = _tracks.get(track_id)
    if not track:
        raise HTTPException(
            status_code=404, detail=f"Track '{track_id}' not found"
        )
    return track


def _next_unanswered(intake: dict[str, str]) -> dict[str, Any] | None:
    for q in TRACK_INTAKE_QUESTIONS:
        if q["key"] not in intake:
            return q
    return None


def _is_vague(answer: str, question_def: dict[str, Any]) -> bool:
    answer_lower = answer.lower().strip()
    if len(answer_lower.split()) < 3:
        return True
    return any(
        signal in answer_lower
        for signal in question_def.get("vague_signals", [])
    )


def _parse_session_count(structure: str) -> int:
    import re

    match = re.search(r"(\d+)\s*session", structure.lower())
    return int(match.group(1)) if match else 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "",
    status_code=201,
    response_model=Track,
    summary="Create a certification track",
)
def create_track() -> Track:
    now = datetime.now(timezone.utc)
    track: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "status": TrackStatus.intake,
        "intake": {},
        "backbone": None,
        "fictional_case": None,
        "session_ids": [],
        "assets": [],
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
    _tracks[track["id"]] = track
    return Track(**track)


@router.get("/{track_id}", response_model=Track, summary="Get full track state")
def get_track(track_id: str) -> Track:
    return Track(**_get_track_or_404(track_id))


# ---------------------------------------------------------------------------
# Track intake
# ---------------------------------------------------------------------------


@router.get(
    "/{track_id}/intake",
    response_model=TrackIntakeResponse,
    summary="Get current track intake state",
)
def get_track_intake(track_id: str) -> TrackIntakeResponse:
    track = _get_track_or_404(track_id)
    next_q = _next_unanswered(track["intake"])
    return TrackIntakeResponse(
        question_key=next_q["key"] if next_q else None,
        question=next_q["question"] if next_q else None,
        progress=len(track["intake"]),
        total=len(TRACK_INTAKE_QUESTIONS),
        complete=next_q is None,
    )


@router.post(
    "/{track_id}/intake",
    response_model=TrackIntakeResponse,
    summary="Submit a track-level intake answer",
)
def submit_track_intake(
    track_id: str, body: TrackAnswerRequest
) -> TrackIntakeResponse:
    track = _get_track_or_404(track_id)

    if track["status"] not in (TrackStatus.intake, TrackStatus.intake_complete):
        raise HTTPException(
            status_code=409, detail="Track intake is already locked"
        )

    next_q = _next_unanswered(track["intake"])
    if next_q is None:
        raise HTTPException(
            status_code=409,
            detail="All track intake questions already answered",
        )

    answer = body.answer.strip()
    if not answer:
        raise HTTPException(status_code=422, detail="Answer cannot be empty")

    if _is_vague(answer, next_q):
        return TrackIntakeResponse(
            question_key=next_q["key"],
            question=next_q["question"],
            progress=len(track["intake"]),
            total=len(TRACK_INTAKE_QUESTIONS),
            complete=False,
            pushback=(
                f"That's a bit vague for a certification track. "
                f"Could you be more specific? This matters because: {next_q['why']}."
            ),
        )

    track["intake"][next_q["key"]] = answer

    # Promote shortcut fields for easy access
    if next_q["key"] == "backbone":
        track["backbone"] = answer
    if next_q["key"] == "fictional_case":
        track["fictional_case"] = answer

    next_q_after = _next_unanswered(track["intake"])
    complete = next_q_after is None

    if complete:
        track["status"] = TrackStatus.intake_complete
        # Auto-create session stubs based on declared structure
        _scaffold_sessions(track)

    track["updated_at"] = datetime.now(timezone.utc)
    _tracks[track_id] = track

    return TrackIntakeResponse(
        question_key=next_q_after["key"] if next_q_after else None,
        question=next_q_after["question"] if next_q_after else None,
        progress=len(track["intake"]),
        total=len(TRACK_INTAKE_QUESTIONS),
        complete=complete,
    )


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


class SessionSummary(BaseModel):
    session_id: str
    session_number: int
    status: SessionStatus
    backbone_phase: str | None


@router.get(
    "/{track_id}/sessions",
    response_model=list[SessionSummary],
    summary="List all sessions in this track with their status",
)
def list_track_sessions(track_id: str) -> list[SessionSummary]:
    track = _get_track_or_404(track_id)
    summaries = []
    for i, sid in enumerate(track["session_ids"], start=1):
        session = _sessions.get(sid)
        if session:
            summaries.append(
                SessionSummary(
                    session_id=sid,
                    session_number=i,
                    status=session.status,
                    backbone_phase=session.intake.get("backbone_phase"),
                )
            )
    return summaries


@router.post(
    "/{track_id}/sessions/{session_id}",
    summary="Attach an existing session to this track at the next position",
)
def attach_session(track_id: str, session_id: str) -> dict[str, Any]:
    track = _get_track_or_404(track_id)
    session = get_session_or_404(session_id)

    if session_id in track["session_ids"]:
        raise HTTPException(
            status_code=409, detail="Session already attached to this track"
        )

    position = len(track["session_ids"]) + 1
    track["session_ids"].append(session_id)
    track["updated_at"] = datetime.now(timezone.utc)

    # Stamp the session with its track context
    session.track_id = track_id
    session.session_number = position
    _sessions[session_id] = session

    return {
        "track_id": track_id,
        "session_id": session_id,
        "session_number": position,
    }


# ---------------------------------------------------------------------------
# Track-level generation
# ---------------------------------------------------------------------------


@router.post(
    "/{track_id}/generate",
    summary="Generate all sessions in sequence, then the track overview",
)
def generate_track(
    track_id: str, background_tasks: BackgroundTasks
) -> dict[str, str]:
    track = _get_track_or_404(track_id)

    if track["status"] not in (
        TrackStatus.intake_complete,
        TrackStatus.planning,
    ):
        raise HTTPException(
            status_code=409,
            detail="Complete track intake before generating",
        )

    session_ids = track["session_ids"]
    if not session_ids:
        raise HTTPException(
            status_code=409, detail="No sessions attached to this track"
        )

    unapproved = [
        sid
        for sid in session_ids
        if _sessions.get(sid)
        and _sessions[sid].status != SessionStatus.outline_approved
    ]
    if unapproved:
        raise HTTPException(
            status_code=409,
            detail=(
                f"{len(unapproved)} session(s) still need outline approval: "
                + ", ".join(unapproved)
            ),
        )

    track["status"] = TrackStatus.generating
    track["updated_at"] = datetime.now(timezone.utc)
    _tracks[track_id] = track

    background_tasks.add_task(_run_track_generation, track_id)

    return {
        "message": (
            f"Generating {len(session_ids)} sessions in sequence — "
            "poll GET /tracks/{id} for status"
        )
    }


@router.get(
    "/{track_id}/assets",
    summary="List track-level assets (overview document)",
)
def get_track_assets(track_id: str) -> dict[str, Any]:
    track = _get_track_or_404(track_id)
    return {"status": track["status"], "assets": track["assets"]}


# ---------------------------------------------------------------------------
# Background workers
# ---------------------------------------------------------------------------


def _scaffold_sessions(track: dict[str, Any]) -> None:
    """Create empty session stubs based on the declared structure."""
    structure = track["intake"].get("structure", "1 session of 2 hours")
    backbone = track["backbone"] or ""
    session_count = _parse_session_count(structure)

    # Derive per-session backbone phases from the backbone string
    phases = _backbone_phases(backbone, session_count)

    now = datetime.now(timezone.utc)
    for i in range(session_count):
        session = Session(
            id=str(uuid.uuid4()),
            status=SessionStatus.intake,
            created_at=now,
            updated_at=now,
        )
        # Pre-fill context from track so per-session intake is shorter
        session.intake["backbone_phase"] = phases[i]
        session.intake["fictional_case"] = track["fictional_case"] or ""
        session.intake["programme_topic"] = track["intake"].get(
            "programme_topic", ""
        )
        session.track_id = track["id"]
        session.session_number = i + 1

        _sessions[session.id] = session
        track["session_ids"].append(session.id)

    track["status"] = TrackStatus.planning


def _backbone_phases(backbone: str, n: int) -> list[str]:
    """Map a backbone name to per-session phase labels."""
    known: dict[str, list[str]] = {
        "dmaic": ["Define", "Measure", "Analyze", "Improve", "Control"],
        "addie": [
            "Analysis",
            "Design",
            "Development",
            "Implementation",
            "Evaluation",
        ],
        "lean": ["Value", "Value Stream", "Flow", "Pull", "Perfection"],
        "agile": [
            "Vision",
            "Roadmap",
            "Sprint Planning",
            "Execution",
            "Retrospective",
        ],
    }
    key = backbone.lower().split()[0] if backbone else ""
    phases = known.get(key, [])

    if phases:
        # Cycle if n > len(phases), truncate if n < len(phases)
        return [phases[i % len(phases)] for i in range(n)]
    # Generic fallback
    return [f"Session {i + 1}" for i in range(n)]


def _run_track_generation(track_id: str) -> None:
    track = _tracks.get(track_id)
    if not track:
        return

    try:
        track_dir = OUTPUT_DIR / track_id
        track_dir.mkdir(parents=True, exist_ok=True)

        prev_post_bite_path: Path | None = None

        for session_id in track["session_ids"]:
            run_generation(
                session_id, previous_post_bite_path=prev_post_bite_path
            )

            # Pass this session's post-bite into the next session's pre-bite
            candidate = OUTPUT_DIR / session_id / "post-bite.docx"
            prev_post_bite_path = candidate if candidate.exists() else None

        # Generate track-level overview document
        overview_path = track_dir / "overview.docx"
        _generate_overview(track, overview_path)

        track["assets"] = ["overview.docx"]
        track["status"] = TrackStatus.ready
        track["updated_at"] = datetime.now(timezone.utc)

    except Exception as exc:  # noqa: BLE001
        track["status"] = TrackStatus.error
        track["error"] = str(exc)
        track["updated_at"] = datetime.now(timezone.utc)

    _tracks[track_id] = track


def _generate_overview(track: dict[str, Any], path: Path) -> None:
    """Generate the session overview document (red thread, timing, objectives).

    TODO: replace stub with a real docx generated via python-docx + agent call.
    """
    path.touch()
