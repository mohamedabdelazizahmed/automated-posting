import httpx
import pytest
import respx

from app.platforms.pastebin import PASTEBIN_API_URL, PastebinPlatform


@pytest.mark.asyncio
@respx.mock
async def test_pastebin_success():
    async with httpx.AsyncClient() as client:
        platform = PastebinPlatform(client, pastebin_api_dev_key="key")
        respx.post(PASTEBIN_API_URL).mock(
            return_value=httpx.Response(200, text="https://pastebin.com/abc12345")
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "success"
        assert result.posted_url == "https://pastebin.com/abc12345"


@pytest.mark.asyncio
@respx.mock
async def test_pastebin_bad_request_error():
    async with httpx.AsyncClient() as client:
        platform = PastebinPlatform(client, pastebin_api_dev_key="key")
        respx.post(PASTEBIN_API_URL).mock(
            return_value=httpx.Response(200, text="Bad API request, invalid api_dev_key")
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Pastebin error" in (result.error or "")


@pytest.mark.asyncio
async def test_pastebin_missing_credentials():
    async with httpx.AsyncClient() as client:
        platform = PastebinPlatform(client, pastebin_api_dev_key="")
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Missing credentials" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_pastebin_http_error():
    async with httpx.AsyncClient() as client:
        platform = PastebinPlatform(client, pastebin_api_dev_key="key")
        respx.post(PASTEBIN_API_URL).mock(return_value=httpx.Response(403, text="Forbidden"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "HTTP error 403" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_pastebin_timeout():
    async with httpx.AsyncClient() as client:
        platform = PastebinPlatform(client, pastebin_api_dev_key="key")
        respx.post(PASTEBIN_API_URL).mock(side_effect=httpx.TimeoutException("Timeout"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Request timeout" in (result.error or "")
