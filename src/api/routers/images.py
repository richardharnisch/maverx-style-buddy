from fastapi import APIRouter

from ..schemas.images import GenerateImageRequest, GenerateImageResponse

router = APIRouter(prefix="/images", tags=["images"])


@router.post(
    "/generate",
    response_model=GenerateImageResponse,
    summary="Generate an image for use in a slide deck",
)
def generate_image(body: GenerateImageRequest) -> GenerateImageResponse:
    # TODO: integrate a real image-generation provider (e.g. OpenAI
    # gpt-image-1) and return base64 or a hosted URL. For now this is a
    # skeleton stub so the deck pipeline has a stable interface to call.
    return GenerateImageResponse(
        prompt=body.prompt,
        image_b64=None,
        image_url=None,
        placeholder=True,
    )
