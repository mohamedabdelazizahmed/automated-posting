
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
    return [
        TelegramPlatform(client, bot_token=settings.telegram_bot_token, channel=settings.telegram_channel),
        MastodonPlatform(client, base_url=settings.mastodon_base_url, access_token=settings.mastodon_access_token),
        DevToPlatform(client, api_key=settings.devto_api_key),
        GitHubGistPlatform(client, token=settings.github_token),
        PastebinPlatform(client, api_dev_key=settings.pastebin_api_dev_key),
    ]
