from fastapi import APIRouter, Depends, status

from app.dependencies import get_posting_service
from app.schemas import PostRequest, PostResponse
from app.services.posting_service import PostingService

router = APIRouter(tags=["Posting"])


@router.post("/posting", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def create_posting(
    payload: PostRequest,
    service: PostingService = Depends(get_posting_service),  # noqa: B008
) -> PostResponse:
    """Publish a message to all configured social platforms."""
    response = await service.post_to_all(payload.message)
    return response
