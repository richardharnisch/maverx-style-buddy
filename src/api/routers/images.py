"""Image generation endpoint.

Returns a Maverx-branded placeholder image (a self-contained SVG data URI) sized
to the request, with the prompt rendered on it. This gives the deck pipeline a
stable, dependency-free interface today; swap the body for a real provider
(e.g. OpenAI gpt-image-1) later without changing the contract — set
``placeholder=False`` and populate ``image_b64`` when you do.
"""

import base64
from xml.sax.saxutils import escape

from fastapi import APIRouter

from ..schemas.images import GenerateImageRequest, GenerateImageResponse

router = APIRouter(prefix="/images", tags=["images"])

_PRIMARY = "#0D006A"
_ACCENT = "#6E29E6"


def _parse_size(size: str) -> tuple[int, int]:
    try:
        w, h = (int(part) for part in size.lower().split("x", 1))
        return max(64, min(w, 4096)), max(64, min(h, 4096))
    except (ValueError, TypeError):
        return 1024, 1024


def _placeholder_svg(prompt: str, width: int, height: int) -> str:
    caption = escape(prompt if len(prompt) <= 80 else prompt[:79] + "…")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{_PRIMARY}"/>'
        f'<stop offset="1" stop-color="{_ACCENT}"/></linearGradient></defs>'
        f'<rect width="{width}" height="{height}" fill="url(#g)"/>'
        f'<text x="50%" y="46%" fill="#FFFFFF" font-family="Arial,sans-serif" '
        f'font-size="{max(16, width // 28)}" font-weight="bold" '
        f'text-anchor="middle">maverx</text>'
        f'<text x="50%" y="56%" fill="#F2F2F2" font-family="Arial,sans-serif" '
        f'font-size="{max(12, width // 48)}" text-anchor="middle">{caption}</text>'
        f"</svg>"
    )


@router.post(
    "/generate",
    response_model=GenerateImageResponse,
    summary="Generate an image for use in a slide deck",
)
def generate_image(body: GenerateImageRequest) -> GenerateImageResponse:
    width, height = _parse_size(body.size)
    svg = _placeholder_svg(body.prompt, width, height)
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(
        svg.encode("utf-8")
    ).decode("ascii")
    return GenerateImageResponse(
        prompt=body.prompt,
        image_b64=None,
        image_url=data_uri,
        placeholder=True,
    )
