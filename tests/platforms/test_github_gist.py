import httpx
import pytest
import respx

from app.platforms.github_gist import GITHUB_GISTS_URL, GitHubGistPlatform


@pytest.mark.asyncio
@respx.mock
async def test_github_gist_success():
    async with httpx.AsyncClient() as client:
        platform = GitHubGistPlatform(client, github_token="token")
        respx.post(GITHUB_GISTS_URL).mock(
            return_value=httpx.Response(
                201, json={"html_url": "https://gist.github.com/user/123"}
            )
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "success"
        assert result.posted_url == "https://gist.github.com/user/123"


@pytest.mark.asyncio
async def test_github_gist_missing_credentials():
    async with httpx.AsyncClient() as client:
        platform = GitHubGistPlatform(client, github_token="")
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Missing credentials" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_github_gist_http_error():
    async with httpx.AsyncClient() as client:
        platform = GitHubGistPlatform(client, github_token="token")
        respx.post(GITHUB_GISTS_URL).mock(
            return_value=httpx.Response(403, text="Forbidden")
        )
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "HTTP error 403" in (result.error or "")


@pytest.mark.asyncio
@respx.mock
async def test_github_gist_timeout():
    async with httpx.AsyncClient() as client:
        platform = GitHubGistPlatform(client, github_token="token")
        respx.post(GITHUB_GISTS_URL).mock(side_effect=httpx.TimeoutException("Timeout"))
        result = await platform.post("Test message https://example.com")
        assert result.status == "failure"
        assert "Request timeout" in (result.error or "")
