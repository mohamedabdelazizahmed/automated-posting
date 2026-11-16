import httpx

from app.platforms.base import SocialPlatform

DEVTO_ARTICLES_URL = "https://dev.to/api/articles"


class DevToPlatform(SocialPlatform):
    """Dev.to posting adapter."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        devto_api_key: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(client, timeout)
        self.devto_api_key = devto_api_key or api_key

    @property
    def name(self) -> str:
        return "Dev.to"

    @property
    def required_credentials(self) -> list[str]:
        return ["devto_api_key"]

    async def _publish(self, message: str) -> str:
        headers = {"api-key": self.devto_api_key}
        title = message[:60]
        payload = {
            "article": {
                "title": title,
                "body_markdown": message,
                "published": True,
            }
        }
        response = await self.client.post(
            DEVTO_ARTICLES_URL, json=payload, headers=headers, timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        return data["url"]
