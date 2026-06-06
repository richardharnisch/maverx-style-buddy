from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.templates_catalog import list_templates, preview_path
from ..schemas.templates import (
    Template,
    TemplatesResponse,
    UploadTemplateResponse,
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get(
    "",
    response_model=TemplatesResponse,
    summary="List available slide templates",
)
def get_templates() -> TemplatesResponse:
    templates = [
        Template(
            template_id=t["template_id"],
            title=t["title"],
            preview_url=f"/templates/{t['template_id']}/preview",
        )
        for t in list_templates()
    ]
    return TemplatesResponse(templates=templates)


@router.get(
    "/{template_id}/preview",
    summary="Get the preview image for a template",
    response_class=FileResponse,
)
def get_template_preview(template_id: str) -> FileResponse:
    path = preview_path(template_id)
    if path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_id}' not found",
        )
    return FileResponse(path, media_type="image/png")


@router.post(
    "",
    response_model=UploadTemplateResponse,
    status_code=201,
    summary="Upload a new slide template",
)
async def upload_template(file: UploadFile) -> UploadTemplateResponse:
    # TODO: persist the uploaded template (PPTX/PNG), extract geometry, and
    # register it in the catalog so it appears in GET /templates.
    filename = file.filename or "upload"
    return UploadTemplateResponse(
        template_id=filename.rsplit(".", 1)[0],
        filename=filename,
        accepted=True,
    )
