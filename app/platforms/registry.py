import httpx

from app.config import Settings
from app.platforms.base import SocialPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.github_gist import GitHubGistPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.pastebin import PastebinPlatform
from app.platforms.telegram import TelegramPlatform


def get_platforms(client: httpx.AsyncClient, settings: Settings) -> list[SocialPlatform]:
    """Build and return the list of configured social platforms."""
    timeout = settings.request_timeout
    return [
        TelegramPlatform(
            client,
            telegram_bot_token=settings.telegram_bot_token,
            telegram_channel=settings.telegram_channel,
            timeout=timeout,
        ),
        MastodonPlatform(
            client,
            mastodon_base_url=settings.mastodon_base_url,
            mastodon_access_token=settings.mastodon_access_token,
            timeout=timeout,
        ),
        DevToPlatform(
            client,
            devto_api_key=settings.devto_api_key,
            timeout=timeout,
        ),
        GitHubGistPlatform(
            client,
            github_token=settings.github_token,
            timeout=timeout,
        ),
        PastebinPlatform(
            client,
            api_dev_key=settings.pastebin_api_dev_key,
            timeout=timeout,
        ),
    ]
