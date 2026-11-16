import httpx

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult


class TelegramPlatform(SocialPlatform):
    """Telegram posting adapter."""

    def __init__(self, client: httpx.AsyncClient, bot_token: str | None = None, channel: str | None = None) -> None:
        super().__init__(client)
        self.bot_token = bot_token
        self.channel = channel

    @property
    def name(self) -> str:
        return "Telegram"

    async def post(self, message: str) -> PlatformResult:
        """TODO: Implement Telegram API call."""
        return self.failure("Not implemented yet")
