import httpx
from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.platforms.registry import get_platforms
from app.services.posting_service import PostingService


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Retrieve the shared httpx.AsyncClient from app state."""
    return request.app.state.client


def get_posting_service(
    request: Request,
    settings: Settings = Depends(get_settings),  # noqa: B008
) -> PostingService:
    """Dependency provider for PostingService with injected client and platforms."""
    client = get_http_client(request)
    platforms = get_platforms(client, settings)
    return PostingService(platforms)
