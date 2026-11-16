import httpx
import pytest
import respx

from app.platforms.mastodon import MASTODON_STATUSES_URL_TEMPLATE, MastodonPlatform


@pytest.mark.asyncio
@respx.mock
async def test_mastodon_success():
    async with httpx.AsyncClient() as client:
        platform = MastodonPlatform(client, mastodon_base_url="https://mastodon.social", mastodon_access_token="token")
        url = MASTODON_STATUSES_URL_TEMPLATE.format(base_url="https://mastodon.social")
        respx.post(url).mock(
            return_value=httpx.Response(200, json={"url": "https://mastodon.social/@user/123"})
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "success"
        assert result.posted_url == "https://mastodon.social/@user/123"


@pytest.mark.asyncio
async def test_mastodon_missing_credentials():
    async with httpx.AsyncClient() as client:
        platform = MastodonPlatform(client, mastodon_base_url="", mastodon_access_token="")
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Missing credentials" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_mastodon_http_error():
    async with httpx.AsyncClient() as client:
        platform = MastodonPlatform(client, mastodon_base_url="https://mastodon.social", mastodon_access_token="token")
        url = MASTODON_STATUSES_URL_TEMPLATE.format(base_url="https://mastodon.social")
        respx.post(url).mock(return_value=httpx.Response(403, text="Forbidden"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "HTTP error 403" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_mastodon_timeout():
    async with httpx.AsyncClient() as client:
        platform = MastodonPlatform(client, mastodon_base_url="https://mastodon.social", mastodon_access_token="token")
        url = MASTODON_STATUSES_URL_TEMPLATE.format(base_url="https://mastodon.social")
        respx.post(url).mock(side_effect=httpx.TimeoutException("Timeout"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Request timeout" in (result.error or "")
