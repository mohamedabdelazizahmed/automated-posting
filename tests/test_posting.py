import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.platforms.base import SocialPlatform
from app.schemas import PostRequest
from app.services.posting_service import PostingService

client = TestClient(app)


def test_post_request_validation_valid():
    """Valid message with exactly one URL passes validation."""
    req = PostRequest(message="Check out this cool site https://example.com")
    assert req.message is not None


def test_post_request_validation_too_long():
    """Message over 200 characters fails validation."""
    long_msg = "A" * 190 + " https://example.com"  # Total length > 200
    with pytest.raises(ValidationError) as exc_info:
        PostRequest(message=long_msg)
    assert "at most 200 characters" in str(exc_info.value)


def test_post_request_validation_no_url():
    """Message without any URL fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        PostRequest(message="Hello world without any link here")
    assert "Message must contain a URL" in str(exc_info.value)


def test_post_request_validation_multiple_urls():
    """Message with multiple URLs fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        PostRequest(message="Visit https://example.com and https://test.com")
    assert "exactly one URL, found multiple" in str(exc_info.value)


def test_post_request_validation_bad_url():
    """Message with invalid URL format fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        PostRequest(message="Check this out not-a-url")
    assert "Message must contain a URL" in str(exc_info.value)


class FakeSuccessPlatform(SocialPlatform):
    @property
    def name(self) -> str:
        return "FakeSuccess"

    @property
    def required_credentials(self) -> list[str]:
        return []

    async def _publish(self, message: str) -> str:
        return "https://fakesuccess.com/post/1"


class FakeFailurePlatform(SocialPlatform):
    @property
    def name(self) -> str:
        return "FakeFailure"

    @property
    def required_credentials(self) -> list[str]:
        return []

    async def _publish(self, message: str) -> str:
        request = httpx.Request("POST", "https://example.com")
        response = httpx.Response(400, text="API error", request=request)
        raise httpx.HTTPStatusError("API error", request=request, response=response)


class FakeExceptionPlatform(SocialPlatform):
    @property
    def name(self) -> str:
        return "FakeException"

    @property
    def required_credentials(self) -> list[str]:
        return []

    async def _publish(self, message: str) -> str:
        raise RuntimeError("Network timeout")


@pytest.mark.asyncio
async def test_posting_service_resilience():
    """Ensure service handles success, failure, and exceptions without stopping others."""
    platforms = [
        FakeSuccessPlatform(None),  # type: ignore
        FakeFailurePlatform(None),  # type: ignore
        FakeExceptionPlatform(None),  # type: ignore
    ]
    service = PostingService(platforms)
    response = await service.post_to_all("Test message https://example.com")

    assert response.success is True
    assert len(response.results) == 3

    success_res = next(r for r in response.results if r.platform == "FakeSuccess")
    assert success_res.status == "success"
    assert success_res.posted_url == "https://fakesuccess.com/post/1"

    fail_res = next(r for r in response.results if r.platform == "FakeFailure")
    assert fail_res.status == "failure"
    assert "HTTP error 400" in (fail_res.error or "")

    exc_res = next(r for r in response.results if r.platform == "FakeException")
    assert exc_res.status == "failure"
    assert "Network timeout" in (exc_res.error or "")


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
