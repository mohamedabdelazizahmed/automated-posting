
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    telegram_bot_token: str | None = None
    telegram_channel: str | None = None
    mastodon_base_url: str | None = None
    mastodon_access_token: str | None = None
    devto_api_key: str | None = None
    github_token: str | None = None
    pastebin_api_dev_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Return a cached or fresh Settings instance."""
    return Settings()
