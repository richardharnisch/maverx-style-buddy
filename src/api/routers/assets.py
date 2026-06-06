"""Asset compiler — the "Heavy Lifter".

Kicks off background generation of the full asset bundle:
  - .pptx deck in Maverx house style
  - pre-bite preparation document
  - post-bite follow-up document

Generation runs as a background task so the HTTP response is immediate;
clients poll GET /assets for status.
"""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from .session import SessionStatus, get_session_or_404, _sessions

router = APIRouter(prefix="/sessions", tags=["assets"])

OUTPUT_DIR = Path("outputs")


class AssetStatus(BaseModel):
    status: str
    assets: list[str]
    message: str | None = None


@router.post(
    "/{session_id}/assets/generate",
    response_model=AssetStatus,
    summary="Trigger full asset generation (pptx + pre-bite + post-bite)",
)
def generate_assets(
    session_id: str, background_tasks: BackgroundTasks
) -> AssetStatus:
    session = get_session_or_404(session_id)

    if session.status != SessionStatus.outline_approved:
        raise HTTPException(
            status_code=409,
            detail="Approve the outline before generating assets",
        )

    session.status = SessionStatus.generating
    session.updated_at = datetime.now(timezone.utc)
    _sessions[session_id] = session

    background_tasks.add_task(run_generation, session_id)

    return AssetStatus(
        status="generating",
        assets=[],
        message="Generation started — poll GET /sessions/{id}/assets for progress",
    )


@router.get(
    "/{session_id}/assets",
    response_model=AssetStatus,
    summary="Get generation status and list of ready assets",
)
def get_assets(session_id: str) -> AssetStatus:
    session = get_session_or_404(session_id)

    if session.status == SessionStatus.generating:
        return AssetStatus(
            status="generating", assets=[], message="Still generating…"
        )

    if session.status == SessionStatus.error:
        return AssetStatus(status="error", assets=[], message=session.error)

    if session.status not in (SessionStatus.ready, SessionStatus.refining):
        return AssetStatus(
            status=session.status,
            assets=[],
            message="Assets not yet generated",
        )

    return AssetStatus(status="ready", assets=session.assets)


# ---------------------------------------------------------------------------
# Generation worker — public so track.py can call it directly in sequence
# ---------------------------------------------------------------------------


def run_generation(
    session_id: str,
    previous_post_bite_path: Path | None = None,
) -> None:
    """Generate all assets for one session.

    Args:
        session_id: Target session.
        previous_post_bite_path: When called from a Track, the post-bite
            document of the preceding session is passed here so the LLM
            can open it with a forward reference in this session's pre-bite.
    """
    session = _sessions.get(session_id)
    if not session:
        return

    try:
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # When part of a track, surface the previous post-bite path so the
        # pre-bite generator can write a bridging intro referencing it.
        if previous_post_bite_path:
            session.intake["_previous_post_bite"] = str(previous_post_bite_path)

        # TODO: call skills pipeline
        #   1. create_presentation(title, style_guide="maverx")
        #   2. for each slide block in outline: add_slide(...)
        #   3. apply_style_guide(...)
        #   4. export_pptx(path=session_dir / "deck.pptx")
        #   5. generate pre-bite — read session.intake["_previous_post_bite"]
        #      if present and pass its content to the LLM as bridging context
        #   6. generate post-bite

        pptx_path = session_dir / "deck.pptx"
        prebite_path = session_dir / "pre-bite.docx"
        postbite_path = session_dir / "post-bite.docx"

        # Stubs — replaced by real skill calls
        pptx_path.touch()
        prebite_path.touch()
        postbite_path.touch()

        session.assets = [pptx_path.name, prebite_path.name, postbite_path.name]
        session.status = SessionStatus.ready
        session.updated_at = datetime.now(timezone.utc)

    except Exception as exc:  # noqa: BLE001
        session.status = SessionStatus.error
        session.error = str(exc)
        session.updated_at = datetime.now(timezone.utc)

    _sessions[session_id] = session
