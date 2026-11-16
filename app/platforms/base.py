from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.schemas import PlatformResult


class SocialPlatform(ABC):
    """Abstract base class for social media and posting platforms."""

    def __init__(self, client: httpx.AsyncClient, timeout: float = 10.0) -> None:
        """Initialize platform with an async HTTP client and timeout."""
        self.client = client
        self.timeout = timeout

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the platform."""

    @property
    @abstractmethod
    def required_credentials(self) -> list[str]:
        """Return list of required credential attribute/setting names."""

    @abstractmethod
    async def _publish(self, message: str) -> str:
        """Publish message to platform API and return the posted URL."""

    async def post(self, message: str) -> PlatformResult:
        """Publish a message using the template method pattern with unified error handling."""
        missing = [attr for attr in self.required_credentials if not getattr(self, attr, None)]
        if missing:
            return self.failure(f"Missing credentials: {', '.join(missing)}")

        try:
            url = await self._publish(message)
            return self.success(posted_url=url, public_access=True)
        except httpx.TimeoutException as e:
            return self.failure(f"Request timeout: {e}")
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            body = e.response.text[:200] if e.response is not None else ""
            return self.failure(f"HTTP error {status}: {body}")
        except Exception as e:  # noqa: BLE001
            return self.failure(f"Publishing failed: {e}")

    def success(self, posted_url: str | None = None, public_access: bool | None = None) -> PlatformResult:
        """Helper to construct a successful PlatformResult."""
        now = datetime.now()
        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            error=None,
        )

    def failure(self, error: str) -> PlatformResult:
        """Helper to construct a failed PlatformResult."""
        now = datetime.now()
        return PlatformResult(
            platform=self.name,
            status="failure",
            posted_url=None,
            public_access=None,
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            error=error,
        )
