import httpx
import pytest
import respx

from app.platforms.telegram import TELEGRAM_API_URL_TEMPLATE, TelegramPlatform


@pytest.mark.asyncio
@respx.mock
async def test_telegram_success():
    async with httpx.AsyncClient() as client:
        platform = TelegramPlatform(
            client, telegram_bot_token="test_token", telegram_channel="@test_channel"
        )
        url = TELEGRAM_API_URL_TEMPLATE.format(token="test_token")
        respx.post(url).mock(
            return_value=httpx.Response(
                200, json={"ok": True, "result": {"message_id": 42}}
            )
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "success"
        assert result.posted_url == "https://t.me/test_channel/42"
        assert result.public_access is True


@pytest.mark.asyncio
async def test_telegram_missing_credentials():
    async with httpx.AsyncClient() as client:
        platform = TelegramPlatform(client, telegram_bot_token="", telegram_channel="")
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Missing credentials" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_telegram_http_error():
    async with httpx.AsyncClient() as client:
        platform = TelegramPlatform(
            client, telegram_bot_token="test_token", telegram_channel="@test_channel"
        )
        url = TELEGRAM_API_URL_TEMPLATE.format(token="test_token")
        respx.post(url).mock(return_value=httpx.Response(401, text="Unauthorized"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "HTTP error 401" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_telegram_timeout():
    async with httpx.AsyncClient() as client:
        platform = TelegramPlatform(
            client, telegram_bot_token="test_token", telegram_channel="@test_channel"
        )
        url = TELEGRAM_API_URL_TEMPLATE.format(token="test_token")
        respx.post(url).mock(side_effect=httpx.TimeoutException("Timeout"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Request timeout" in (result.error or "")
