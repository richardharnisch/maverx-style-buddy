"""HTTP client for the Decker FastAPI backend.

The Streamlit UI is a pure frontend; all state lives behind the API. This is a
thin httpx wrapper so pages never build URLs or parse JSON inline.
"""

from __future__ import annotations

import os

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

_client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)


class APIError(RuntimeError):
    """Raised when the backend returns a non-success status."""


def _request(method: str, path: str, **kwargs) -> httpx.Response:
    try:
        resp = _client.request(method, path, **kwargs)
    except httpx.HTTPError as exc:  # connection refused, timeout, etc.
        raise APIError(
            f"Could not reach the Decker API at {API_BASE_URL}. "
            f"Is it running? ({exc})"
        ) from exc
    if resp.status_code >= 400:
        detail = resp.text
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        raise APIError(f"{resp.status_code}: {detail}")
    return resp


# --- meta ---------------------------------------------------------------

def health() -> dict:
    return _request("GET", "/health").json()


def get_models() -> dict:
    """Return {'models': [...], 'default': '...'}."""
    return _request("GET", "/models").json()


# --- sessions (decks) ---------------------------------------------------

def create_session() -> dict:
    return _request("POST", "/sessions", json={}).json()


def list_messages(session_id: str) -> list[dict]:
    data = _request("GET", f"/sessions/{session_id}/messages").json()
    return data.get("messages", [])


def send_message(session_id: str, content: str, model: str) -> list[dict]:
    data = _request(
        "POST",
        f"/sessions/{session_id}/messages",
        json={"content": content, "model": model},
    ).json()
    return data.get("messages", [])


# --- templates ----------------------------------------------------------

def list_templates() -> list[dict]:
    data = _request("GET", "/templates").json()
    return data.get("templates", [])


def template_preview_url(template_id: str) -> str:
    return f"{API_BASE_URL}/templates/{template_id}/preview"


def upload_template(filename: str, data: bytes, content_type: str) -> dict:
    return _request(
        "POST",
        "/templates",
        files={"file": (filename, data, content_type)},
    ).json()


# --- files --------------------------------------------------------------

def download_file(session_id: str, filename: str) -> bytes:
    """Fetch a generated artifact's raw bytes for a Streamlit download button."""
    return _request(
        "GET", f"/sessions/{session_id}/files/{filename}"
    ).content


# --- images -------------------------------------------------------------

def generate_image(prompt: str, size: str = "1024x1024") -> dict:
    return _request(
        "POST",
        "/images/generate",
        json={"prompt": prompt, "size": size},
    ).json()
