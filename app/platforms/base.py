from abc import ABC, abstractmethod
from datetime import datetime

import httpx

from app.schemas import PlatformResult


class SocialPlatform(ABC):
    """Abstract base class for social media and posting platforms."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialize platform with an async HTTP client."""
        self.client = client

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the platform."""

    @abstractmethod
    async def post(self, message: str) -> PlatformResult:
        """Publish a message to the platform."""

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
