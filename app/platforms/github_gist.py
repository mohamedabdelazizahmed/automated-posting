import httpx

from app.platforms.base import SocialPlatform

GITHUB_GISTS_URL = "https://api.github.com/gists"


class GitHubGistPlatform(SocialPlatform):
    """GitHub Gist posting adapter."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        github_token: str | None = None,
        token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(client, timeout)
        self.github_token = github_token or token

    @property
    def name(self) -> str:
        return "GitHub Gist"

    @property
    def required_credentials(self) -> list[str]:
        return ["github_token"]

    async def _publish(self, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json",
        }
        payload = {
            "description": "Public post",
            "public": True,
            "files": {
                "post.md": {
                    "content": message
                }
            }
        }
        response = await self.client.post(GITHUB_GISTS_URL, json=payload, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        return data["html_url"]
