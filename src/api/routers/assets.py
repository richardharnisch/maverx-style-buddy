from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.constants import (
    DECK_FILENAME,
    OUTPUT_DIR,
    POST_BITE_FILENAME,
    PRE_BITE_FILENAME,
)
from ..schemas.assets import AssetStatus
from ..schemas.session import SessionStatus
from .session import _sessions, get_session_or_404

router = APIRouter(prefix="/sessions", tags=["assets"])


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
    summary="Get generation status, file list, cost, and confidence scores",
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
            status=session.status, assets=[], message="Assets not yet generated"
        )

    return AssetStatus(
        status="ready",
        assets=session.assets,
        generation_cost_usd=session.generation_cost_usd,
        confidence_scores=session.confidence_scores,
    )


def run_generation(
    session_id: str,
    previous_post_bite_path: Path | None = None,
) -> None:
    """Generate all assets for one session.

    Args:
        session_id: Target session.
        previous_post_bite_path: Post-bite of the preceding session (Tier 3 tracks).
            Passed to the pre-bite generator so it can write a bridging intro.
    """
    session = _sessions.get(session_id)
    if not session:
        return

    try:
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        if previous_post_bite_path:
            session.intake["_previous_post_bite"] = str(previous_post_bite_path)

        # TODO: implement full pipeline:
        #   1. create_presentation(title, style_guide=session.style_guide, language=session.language)
        #   2. for each block in approved outline:
        #        for each slide: add_slide(presentation_id, layout, block, title, bullets, speaker_notes)
        #        session.confidence_scores[block] = mean(slide confidence_scores for this block)
        #   3. apply_style_guide(presentation_id, session.style_guide)
        #   4. export_pptx(presentation_id, output_path=session_dir/"deck.pptx")
        #   5. generate_document("pre-bite",  ..., previous_post_bite_summary if track session)
        #   6. generate_document("post-bite", ...)
        #   7. record total token cost → session.generation_cost_usd

        pptx_path = session_dir / DECK_FILENAME
        prebite_path = session_dir / PRE_BITE_FILENAME
        postbite_path = session_dir / POST_BITE_FILENAME

        pptx_path.touch()
        prebite_path.touch()
        postbite_path.touch()

        session.assets = [pptx_path.name, prebite_path.name, postbite_path.name]
        session.generation_cost_usd = 0.0  # TODO: sum token costs
        session.status = SessionStatus.ready
        session.updated_at = datetime.now(timezone.utc)

    except Exception as exc:  # noqa: BLE001
        session.status = SessionStatus.error
        session.error = str(exc)
        session.updated_at = datetime.now(timezone.utc)

    _sessions[session_id] = session
