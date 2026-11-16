import httpx

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult


class GitHubGistPlatform(SocialPlatform):
    """GitHub Gist posting adapter."""

    def __init__(self, client: httpx.AsyncClient, token: str | None = None) -> None:
        super().__init__(client)
        self.token = token

    @property
    def name(self) -> str:
        return "GitHub Gist"

    async def post(self, message: str) -> PlatformResult:
        """TODO: Implement GitHub Gist API call."""
        return self.failure("Not implemented yet")
