import httpx
import pytest
import respx

from app.platforms.devto import DEVTO_ARTICLES_URL, DevToPlatform


@pytest.mark.asyncio
@respx.mock
async def test_devto_success():
    async with httpx.AsyncClient() as client:
        platform = DevToPlatform(client, devto_api_key="key")
        respx.post(DEVTO_ARTICLES_URL).mock(
            return_value=httpx.Response(201, json={"url": "https://dev.to/user/post-1"})
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "success"
        assert result.posted_url == "https://dev.to/user/post-1"


@pytest.mark.asyncio
async def test_devto_missing_credentials():
    async with httpx.AsyncClient() as client:
        platform = DevToPlatform(client, devto_api_key="")
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Missing credentials" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_devto_http_error():
    async with httpx.AsyncClient() as client:
        platform = DevToPlatform(client, devto_api_key="key")
        respx.post(DEVTO_ARTICLES_URL).mock(return_value=httpx.Response(401, text="Unauthorized"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "HTTP error 401" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_devto_timeout():
    async with httpx.AsyncClient() as client:
        platform = DevToPlatform(client, devto_api_key="key")
        respx.post(DEVTO_ARTICLES_URL).mock(side_effect=httpx.TimeoutException("Timeout"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Request timeout" in (result.error or "")
