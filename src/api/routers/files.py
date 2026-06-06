"""File server — the "Deliverable Host".

Serves generated files (pptx, pre-bite, post-bite) for download.
Files are scoped to a session directory so one session can't reach
another's outputs.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .session import SessionStatus, get_session_or_404

router = APIRouter(prefix="/sessions", tags=["files"])

OUTPUT_DIR = Path("outputs")

MIME_TYPES: dict[str, str] = {
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
}


class FileEntry(BaseModel):
    filename: str
    size_bytes: int
    download_url: str


class FileListResponse(BaseModel):
    session_id: str
    files: list[FileEntry]


@router.get(
    "/{session_id}/files",
    response_model=FileListResponse,
    summary="List all downloadable files for this session",
)
def list_files(session_id: str) -> FileListResponse:
    session = get_session_or_404(session_id)

    if session.status not in (SessionStatus.ready, SessionStatus.refining):
        raise HTTPException(status_code=404, detail="No files available yet")

    session_dir = OUTPUT_DIR / session_id
    entries: list[FileEntry] = []

    for filename in session.assets:
        path = session_dir / filename
        if path.exists():
            entries.append(
                FileEntry(
                    filename=filename,
                    size_bytes=path.stat().st_size,
                    download_url=f"/sessions/{session_id}/files/{filename}",
                )
            )

    return FileListResponse(session_id=session_id, files=entries)


@router.get(
    "/{session_id}/files/{filename}",
    summary="Download a generated file",
    response_class=FileResponse,
)
def download_file(session_id: str, filename: str) -> FileResponse:
    session = get_session_or_404(session_id)

    if session.status not in (SessionStatus.ready, SessionStatus.refining):
        raise HTTPException(status_code=404, detail="No files available yet")

    # Prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if filename not in session.assets:
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found in this session",
        )

    path = OUTPUT_DIR / session_id / filename
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="File missing from disk — try regenerating"
        )

    media_type = MIME_TYPES.get(path.suffix, "application/octet-stream")
    return FileResponse(
        path=str(path), media_type=media_type, filename=filename
    )
