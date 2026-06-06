"""File download endpoints — skeleton.

Logic removed pending the deck-generation pipeline rewrite. Signatures and
schemas are kept so the teammate can reimplement against a stable contract.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/sessions", tags=["files"])

_NOT_IMPLEMENTED = "File pipeline not implemented yet."


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
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get(
    "/{session_id}/files/{filename}",
    summary="Download a generated file",
    response_class=FileResponse,
)
def download_file(session_id: str, filename: str) -> FileResponse:
    # TODO: reimplement once the deck-generation pipeline lands.
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
