"""File download endpoints — serves artifacts from the session output dir."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.constants import OUTPUT_DIR

router = APIRouter(prefix="/sessions", tags=["files"])

# Only generated delivery artifacts are downloadable.
_ALLOWED_SUFFIXES = {".pptx", ".docx", ".pdf", ".png", ".json"}


class FileEntry(BaseModel):
    filename: str
    size_bytes: int
    download_url: str


class FileListResponse(BaseModel):
    session_id: str
    files: list[FileEntry]


def _session_dir(session_id: str) -> Path:
    return (OUTPUT_DIR / session_id).resolve()


@router.get(
    "/{session_id}/files",
    response_model=FileListResponse,
    summary="List all downloadable files for this session",
)
def list_files(session_id: str) -> FileListResponse:
    base = _session_dir(session_id)
    files: list[FileEntry] = []
    if base.is_dir():
        for path in sorted(base.iterdir()):
            if path.is_file() and path.suffix.lower() in _ALLOWED_SUFFIXES:
                files.append(
                    FileEntry(
                        filename=path.name,
                        size_bytes=path.stat().st_size,
                        download_url=f"/sessions/{session_id}/files/{path.name}",
                    )
                )
    return FileListResponse(session_id=session_id, files=files)


@router.get(
    "/{session_id}/files/{filename}",
    summary="Download a generated file",
    response_class=FileResponse,
)
def download_file(session_id: str, filename: str) -> FileResponse:
    base = _session_dir(session_id)
    target = (base / filename).resolve()
    # Guard against path traversal: the resolved path must stay inside base.
    if base not in target.parents or target.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=target, filename=filename)
