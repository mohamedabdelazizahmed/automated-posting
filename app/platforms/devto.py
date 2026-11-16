import httpx

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult


class DevToPlatform(SocialPlatform):
    """Dev.to posting adapter."""

    def __init__(self, client: httpx.AsyncClient, api_key: str | None = None) -> None:
        super().__init__(client)
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "Dev.to"

    async def post(self, message: str) -> PlatformResult:
        """TODO: Implement Dev.to API call."""
        return self.failure("Not implemented yet")
