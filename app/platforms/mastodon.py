import httpx

from app.platforms.base import SocialPlatform

MASTODON_STATUSES_URL_TEMPLATE = "{base_url}/api/v1/statuses"


class MastodonPlatform(SocialPlatform):
    """Mastodon posting adapter."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        mastodon_base_url: str | None = None,
        mastodon_access_token: str | None = None,
        base_url: str | None = None,
        access_token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(client, timeout)
        self.mastodon_base_url = mastodon_base_url or base_url
        self.mastodon_access_token = mastodon_access_token or access_token

    @property
    def name(self) -> str:
        return "Mastodon"

    @property
    def required_credentials(self) -> list[str]:
        return ["mastodon_base_url", "mastodon_access_token"]

    async def _publish(self, message: str) -> str:
        base_url = str(self.mastodon_base_url).rstrip("/")
        url = MASTODON_STATUSES_URL_TEMPLATE.format(base_url=base_url)
        headers = {"Authorization": f"Bearer {self.mastodon_access_token}"}
        payload = {
            "status": message,
            "visibility": "public",
        }
        response = await self.client.post(url, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["url"]
