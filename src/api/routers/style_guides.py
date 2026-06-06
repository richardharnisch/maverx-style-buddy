"""Style guide endpoints.

House style is a configurable input, not a hard-coded assumption: the bundled
``maverx`` guide ships with the master template deck, and additional guides can
be uploaded as PPTX masters into ``STYLE_GUIDES_DIR`` and swapped in without a
rebuild (case requirement: robustness against house-style changes).
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.constants import DEFAULT_STYLE_GUIDE, STYLE_GUIDES_DIR, TEMPLATE_DECK_PATH
from ..schemas.style_guide import StyleGuideInfo, StyleGuideListResponse

router = APIRouter(prefix="/style-guides", tags=["style-guides"])


def _builtin() -> StyleGuideInfo:
    return StyleGuideInfo(
        name=DEFAULT_STYLE_GUIDE,
        has_master_pptx=TEMPLATE_DECK_PATH.exists(),
        description="Bundled Maverx corporate house style (master slide deck).",
    )


def _uploaded() -> list[StyleGuideInfo]:
    if not STYLE_GUIDES_DIR.is_dir():
        return []
    return [
        StyleGuideInfo(
            name=path.stem,
            has_master_pptx=True,
            description="Uploaded house-style master deck.",
        )
        for path in sorted(STYLE_GUIDES_DIR.glob("*.pptx"))
        if path.stem != DEFAULT_STYLE_GUIDE
    ]


@router.get(
    "",
    response_model=StyleGuideListResponse,
    summary="List all available style guides",
)
def list_style_guides() -> StyleGuideListResponse:
    return StyleGuideListResponse(available=[_builtin(), *_uploaded()])


@router.get("/{name}", response_model=StyleGuideInfo, summary="Get a style guide")
def get_style_guide(name: str) -> StyleGuideInfo:
    for guide in [_builtin(), *_uploaded()]:
        if guide.name == name:
            return guide
    raise HTTPException(status_code=404, detail=f"Style guide '{name}' not found")


@router.put(
    "/{name}",
    response_model=StyleGuideInfo,
    summary="Upload or replace a style guide via PPTX master template",
)
async def upload_style_guide(
    name: str, file: UploadFile = File(...)
) -> StyleGuideInfo:
    if name == DEFAULT_STYLE_GUIDE:
        raise HTTPException(
            status_code=400, detail="The bundled 'maverx' guide cannot be overwritten."
        )
    if not (file.filename or "").lower().endswith(".pptx"):
        raise HTTPException(status_code=400, detail="A .pptx master deck is required.")
    STYLE_GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    target = STYLE_GUIDES_DIR / f"{name}.pptx"
    target.write_bytes(await file.read())
    return StyleGuideInfo(
        name=name, has_master_pptx=True, description="Uploaded house-style master deck."
    )
