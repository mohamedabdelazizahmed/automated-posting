import httpx

from app.platforms.base import SocialPlatform

PASTEBIN_API_URL = "https://pastebin.com/api/api_post.php"


class PastebinPlatform(SocialPlatform):
    """Pastebin posting adapter."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        pastebin_api_dev_key: str | None = None,
        api_dev_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(client, timeout)
        self.pastebin_api_dev_key = pastebin_api_dev_key or api_dev_key

    @property
    def name(self) -> str:
        return "Pastebin"

    @property
    def required_credentials(self) -> list[str]:
        return ["pastebin_api_dev_key"]

    async def _publish(self, message: str) -> str:
        payload = {
            "api_dev_key": self.pastebin_api_dev_key,
            "api_option": "paste",
            "api_paste_code": message,
            "api_paste_private": "0",
            "api_paste_name": "Public post",
        }
        response = await self.client.post(
            PASTEBIN_API_URL, data=payload, timeout=self.timeout
        )
        response.raise_for_status()
        text = response.text.strip()
        if text.startswith("https://"):
            return text
        raise ValueError(f"Pastebin error: {text}")
