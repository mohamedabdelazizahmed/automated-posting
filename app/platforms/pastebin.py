import httpx

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult


class PastebinPlatform(SocialPlatform):
    """Pastebin posting adapter."""

    def __init__(self, client: httpx.AsyncClient, api_dev_key: str | None = None) -> None:
        super().__init__(client)
        self.api_dev_key = api_dev_key

    @property
    def name(self) -> str:
        return "Pastebin"

    async def post(self, message: str) -> PlatformResult:
        """TODO: Implement Pastebin API call."""
        return self.failure("Not implemented yet")
