"""Intake endpoint — the "Pushback" agent.

Walks the trainer through the 5 mandatory questions in order.
Refuses to advance until each answer is specific enough; asks
follow-up questions when input is vague.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .session import SessionStatus, get_session_or_404, _sessions

router = APIRouter(prefix="/sessions", tags=["intake"])

INTAKE_QUESTIONS: list[dict[str, Any]] = [
    {
        "key": "topic",
        "question": "What is the topic or skill to be trained?",
        "why": "Sets the domain",
        "vague_signals": ["something", "stuff", "things", "general", "various"],
    },
    {
        "key": "audience",
        "question": "Who is the target audience?",
        "why": "Sets tone and depth",
        "vague_signals": ["everyone", "anyone", "people", "employees"],
    },
    {
        "key": "knowledge_level",
        "question": "What is the knowledge level of participants?",
        "why": "Beginner / intermediate / advanced",
        "valid_levels": ["beginner", "intermediate", "advanced"],
        "vague_signals": ["mixed", "varies", "unknown", "unsure"],
    },
    {
        "key": "duration",
        "question": "How long is the training?",
        "why": "Determines module count and slide count",
        "vague_signals": ["short", "long", "a while", "some time"],
    },
    {
        "key": "learning_objective",
        "question": "What is the primary learning objective?",
        "why": "Anchors the entire structure",
        "vague_signals": ["learn", "understand", "know about", "get better"],
    },
]


class AnswerRequest(BaseModel):
    answer: str


class IntakeResponse(BaseModel):
    question_key: str | None
    question: str | None
    progress: int
    total: int
    complete: bool
    pushback: str | None = None


class IntakeStateResponse(BaseModel):
    answers: dict[str, str]
    next_question: dict[str, Any] | None
    complete: bool


def _is_vague(answer: str, question_def: dict[str, Any]) -> bool:
    answer_lower = answer.lower().strip()
    if len(answer_lower.split()) < 2:
        return True
    for signal in question_def.get("vague_signals", []):
        if signal in answer_lower:
            return True
    if "valid_levels" in question_def:
        return not any(
            level in answer_lower for level in question_def["valid_levels"]
        )
    return False


def _next_unanswered(intake: dict[str, str]) -> dict[str, Any] | None:
    for q in INTAKE_QUESTIONS:
        if q["key"] not in intake:
            return q
    return None


@router.get(
    "/{session_id}/intake",
    response_model=IntakeStateResponse,
    summary="Get current intake state",
)
def get_intake(session_id: str) -> IntakeStateResponse:
    session = get_session_or_404(session_id)
    next_q = _next_unanswered(session.intake)
    return IntakeStateResponse(
        answers=session.intake,
        next_question=next_q,
        complete=next_q is None,
    )


@router.post(
    "/{session_id}/intake",
    response_model=IntakeResponse,
    summary="Submit an intake answer",
)
def submit_intake_answer(
    session_id: str, body: AnswerRequest
) -> IntakeResponse:
    session = get_session_or_404(session_id)

    if session.status not in (
        SessionStatus.intake,
        SessionStatus.intake_complete,
    ):
        raise HTTPException(
            status_code=409,
            detail=f"Intake already locked — session is in '{session.status}' state",
        )

    next_q = _next_unanswered(session.intake)
    if next_q is None:
        raise HTTPException(
            status_code=409, detail="All intake questions already answered"
        )

    answer = body.answer.strip()
    if not answer:
        raise HTTPException(status_code=422, detail="Answer cannot be empty")

    pushback: str | None = None
    if _is_vague(answer, next_q):
        pushback = (
            f"That answer is a bit vague. Could you be more specific? "
            f"This matters because: {next_q['why']}."
        )
        answered_count = len(session.intake)
        return IntakeResponse(
            question_key=next_q["key"],
            question=next_q["question"],
            progress=answered_count,
            total=len(INTAKE_QUESTIONS),
            complete=False,
            pushback=pushback,
        )

    session.intake[next_q["key"]] = answer
    session.updated_at = datetime.now(timezone.utc)

    next_q_after = _next_unanswered(session.intake)
    complete = next_q_after is None

    if complete:
        session.status = SessionStatus.intake_complete

    _sessions[session_id] = session

    return IntakeResponse(
        question_key=next_q_after["key"] if next_q_after else None,
        question=next_q_after["question"] if next_q_after else None,
        progress=len(session.intake),
        total=len(INTAKE_QUESTIONS),
        complete=complete,
    )
