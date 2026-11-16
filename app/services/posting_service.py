import asyncio
from datetime import datetime

from app.platforms.base import SocialPlatform
from app.schemas import PlatformResult, PostResponse


class PostingService:
    """Service orchestrating concurrent posting across multiple social platforms."""

    def __init__(self, platforms: list[SocialPlatform]) -> None:
        self.platforms = platforms

    async def post_to_all(self, message: str) -> PostResponse:
        """Post message to all configured platforms concurrently."""
        if not self.platforms:
            return PostResponse(success=False, results=[])

        tasks = [platform.post(message) for platform in self.platforms]
        # return_exceptions=True ensures one failing platform or exception doesn't drop others
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[PlatformResult] = []
        for platform, res in zip(self.platforms, raw_results):
            if isinstance(res, Exception):
                now = datetime.now()
                results.append(
                    PlatformResult(
                        platform=platform.name,
                        status="failure",
                        posted_url=None,
                        public_access=None,
                        date=now.strftime("%Y-%m-%d"),
                        time=now.strftime("%H:%M:%S"),
                        error=str(res),
                    )
                )
            elif isinstance(res, PlatformResult):
                results.append(res)
            else:
                now = datetime.now()
                results.append(
                    PlatformResult(
                        platform=platform.name,
                        status="failure",
                        posted_url=None,
                        public_access=None,
                        date=now.strftime("%Y-%m-%d"),
                        time=now.strftime("%H:%M:%S"),
                        error=f"Unexpected return type: {type(res)}",
                    )
                )

        success_any = any(r.status == "success" for r in results)
        return PostResponse(success=success_any, results=results)
