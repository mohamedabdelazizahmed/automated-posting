import httpx

from app.platforms.base import SocialPlatform

TELEGRAM_API_URL_TEMPLATE = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramPlatform(SocialPlatform):
    """Telegram posting adapter."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        telegram_bot_token: str | None = None,
        telegram_channel: str | None = None,
        bot_token: str | None = None,
        channel: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(client, timeout)
        self.telegram_bot_token = telegram_bot_token or bot_token
        self.telegram_channel = telegram_channel or channel

    @property
    def name(self) -> str:
        return "Telegram"

    @property
    def required_credentials(self) -> list[str]:
        return ["telegram_bot_token", "telegram_channel"]

    async def _publish(self, message: str) -> str:
        url = TELEGRAM_API_URL_TEMPLATE.format(token=self.telegram_bot_token)
        payload = {
            "chat_id": self.telegram_channel,
            "text": message,
        }
        response = await self.client.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        message_id = data["result"]["message_id"]
        channel_clean = str(self.telegram_channel).lstrip("@")
        return f"https://t.me/{channel_clean}/{message_id}"
