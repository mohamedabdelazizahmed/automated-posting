import httpx

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult


class MastodonPlatform(SocialPlatform):
    """Mastodon posting adapter."""

    def __init__(self, client: httpx.AsyncClient, base_url: str | None = None, access_token: str | None = None) -> None:
        super().__init__(client)
        self.base_url = base_url
        self.access_token = access_token

    @property
    def name(self) -> str:
        return "Mastodon"

    async def post(self, message: str) -> PlatformResult:
        """TODO: Implement Mastodon API call."""
        return self.failure("Not implemented yet")
