# Automated Posting Service

A robust, asynchronous FastAPI microservice that publishes a message simultaneously to five major social and content platforms (Telegram, Mastodon, Dev.to, GitHub Gist, and Pastebin) with strict input validation, fault-tolerant concurrent execution, and unified error handling.

## Features

- **Concurrent Multi-Platform Publishing:** Publishes messages to all configured platforms in parallel using asynchronous HTTPX clients.
- **Per-Platform Failure Isolation:** Leverages asynchronous gathering with exception isolation so that downtime, rate limits, or errors on one platform never prevent others from publishing successfully.
- **Strict Input Validation:** Enforces message length limits (maximum 200 characters) and strict URL integrity (requires exactly one valid HTTP/HTTPS URL).
- **Template Method Pattern:** Unifies credential pre-checks, successful result generation, and centralized error handling (timeouts, HTTP status errors, and exceptions) in the abstract base class.

## Supported Platforms

| Platform | API Used | Auth Variable | Public URL Source |
| :--- | :--- | :--- | :--- |
| **Telegram** | `https://api.telegram.org/bot{token}/sendMessage` | `TELEGRAM_BOT_TOKEN` (plus `TELEGRAM_CHANNEL`) | `https://t.me/{channel}/{message_id}` |
| **Mastodon** | `{base_url}/api/v1/statuses` | `MASTODON_ACCESS_TOKEN` (plus `MASTODON_BASE_URL`) | Response JSON field `url` |
| **Dev.to** | `https://dev.to/api/articles` | `DEVTO_API_KEY` | Response JSON field `url` |
| **GitHub Gist** | `https://api.github.com/gists` | `GITHUB_TOKEN` | Response JSON field `html_url` |
| **Pastebin** | `https://pastebin.com/api/api_post.php` | `PASTEBIN_API_DEV_KEY` | Plain text response body starting with `https://` |

## Architecture

### Folder Structure
```text
automated-posting/
├── app/
│   ├── api/
│   │   └── routes.py         # API route handlers
│   ├── platforms/
│   │   ├── base.py           # Abstract base class (Template Method pattern)
│   │   ├── devto.py          # Dev.to platform adapter
│   │   ├── github_gist.py    # GitHub Gist platform adapter
│   │   ├── mastodon.py       # Mastodon platform adapter
│   │   ├── pastebin.py       # Pastebin platform adapter
│   │   ├── registry.py       # Platform registry factory
│   │   └── telegram.py       # Telegram platform adapter
│   ├── services/
│   │   └── posting_service.py # Orchestrates concurrent posting
│   ├── config.py             # Pydantic settings configuration
│   ├── dependencies.py       # FastAPI dependency providers
│   ├── main.py               # FastAPI app and lifespan management
│   └── schemas.py            # Pydantic request/response models & validation
├── tests/
│   ├── platforms/            # Unit tests for each platform adapter (using respx)
│   └── test_posting.py       # Request validation and end-to-end service tests
├── Dockerfile                # Container definition
├── docker-compose.yml        # Docker compose configuration
├── requirements.txt          # Production dependencies
└── requirements-dev.txt      # Development & testing dependencies
```

### SOLID Principles Mapping
- **Single Responsibility Principle (S):** Request validation and routing live in `app/api/routes.py`, concurrency orchestration in `app/services/posting_service.py`, and each adapter in `app/platforms/` interacts with exactly one platform API.
- **Open/Closed Principle (O):** Adding a new platform requires implementing a new subclass of `SocialPlatform` (`app/platforms/base.py`) and registering it in `get_platforms` (`app/platforms/registry.py`) without modifying existing code.
- **Liskov Substitution Principle (L):** All platform adapters inherit from `SocialPlatform`, adhere to the expected interface, and return standardized `PlatformResult` objects without raising unhandled exceptions out of `post()`.
- **Interface Segregation Principle (I):** The abstract base class defines a lean, cohesive interface (`name`, `required_credentials`, `_publish`).
- **Dependency Inversion Principle (D):** `PostingService` depends on the abstract `SocialPlatform` interface, and dependencies (`AsyncClient`, `Settings`, platforms) are injected via FastAPI dependency injection (`app/dependencies.py`).

## Setup

### Local Setup
1. Clone the repository and navigate to the project directory.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
5. Run the application locally:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
   ```

### Docker Setup
1. Copy `.env.example` to `.env` and configure your credentials.
2. Build and run using Docker Compose:
   ```bash
   docker compose up --build
   ```

### How to Get Each Credential
- **Telegram Bot Token (`TELEGRAM_BOT_TOKEN`):** Talk to [@BotFather](https://t.me/BotFather) on Telegram to create a bot and obtain its token.
- **Telegram Channel (`TELEGRAM_CHANNEL`):** Create a public channel and add your bot as an administrator (e.g., `@mychannel`).
- **Mastodon Access Token (`MASTODON_ACCESS_TOKEN`):** Go to your instance Settings > Development > New Application to generate an access token.
- **Mastodon Base URL (`MASTODON_BASE_URL`):** Your instance URL (e.g., `https://mastodon.social`).
- **Dev.to API Key (`DEVTO_API_KEY`):** Go to Dev.to Settings > Account > API Keys to generate a new API key.
- **GitHub Token (`GITHUB_TOKEN`):** Generate a Personal Access Token (Classic or Fine-grained) with `gist` scope under GitHub Developer Settings.
- **Pastebin API Dev Key (`PASTEBIN_API_DEV_KEY`):** Log into Pastebin, go to the API page, and copy your Developer API Key.

## Usage

### cURL Example
```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world from FastAPI! Check this out https://example.com"}'
```

### Validation Rules
- **Message Content:** Must not be empty or whitespace-only.
- **Length:** Maximum 200 characters.
- **URL Count:** Must contain **exactly one** valid HTTP/HTTPS URL.

## Sample Requests and Responses

### Valid Request
```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{"message": "Announcing our new release! https://example.com"}'
```

#### Success Response (`docs/sample_response.json`)
```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/mychannel/123",
      "public_access": true,
      "date": "2026-11-16",
      "time": "12:00:00",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@user/456",
      "public_access": true,
      "date": "2026-11-16",
      "time": "12:00:00",
      "error": null
    },
    {
      "platform": "Dev.to",
      "status": "success",
      "posted_url": "https://dev.to/user/post-1",
      "public_access": true,
      "date": "2026-11-16",
      "time": "12:00:00",
      "error": null
    },
    {
      "platform": "GitHub Gist",
      "status": "success",
      "posted_url": "https://gist.github.com/user/789",
      "public_access": true,
      "date": "2026-11-16",
      "time": "12:00:00",
      "error": null
    },
    {
      "platform": "Pastebin",
      "status": "success",
      "posted_url": "https://pastebin.com/abc12345",
      "public_access": true,
      "date": "2026-11-16",
      "time": "12:00:00",
      "error": null
    }
  ]
}
```

### Validation Error Examples

#### 1. Message Too Long (> 200 characters)
*Request JSON:*
```json
{"message": "A 191-character message with a URL https://example.com ................................................................................................................................................."}
```
*Response JSON:*
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must be at most 200 characters long.",
      "input": "...",
      "ctx": {"error": {}}
    }
  ]
}
```

#### 2. No Link
*Request JSON:*
```json
{"message": "Hello world without any link here"}
```
*Response JSON:*
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must contain a URL.",
      "input": "Hello world without any link here",
      "ctx": {"error": {}}
    }
  ]
}
```

#### 3. Multiple Links (> 1 URL)
*Request JSON:*
```json
{"message": "Visit https://example.com and https://test.com"}
```
*Response JSON:*
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must contain exactly one URL, found multiple.",
      "input": "Visit https://example.com and https://test.com",
      "ctx": {"error": {}}
    }
  ]
}
```

#### 4. Invalid URL Format
*Request JSON:*
```json
{"message": "Check this out not-a-url"}
```
*Response JSON:*
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must contain a URL.",
      "input": "check not-a-url",
      "ctx": {"error": {}}
    }
  ]
}
```

## Screenshots
*No screenshots are currently embedded.* (Place images inside `docs/screenshots/` and reference them here with captions if needed).

## Running Tests
Run code style checks with Ruff and test suite execution with Pytest:
```bash
# Run linter
ruff check .

# Run test suite
python -m pytest
```

## Design Decisions

- **Overall Success Rule (`success`):** The top-level response `success` is `true` if **at least one** platform successfully publishes the message. This ensures partial success is reported positively while individual platform failures are captured in the per-platform results array.
- **Public Access (`public_access`):** All five supported platforms publish posts as publicly accessible items (`public_access: true` on success).
- **Unified Error Handling:** The template method pattern in `SocialPlatform` catches `httpx.TimeoutException`, `httpx.HTTPStatusError` (including status codes and response bodies), and generic exceptions, converting them cleanly into failed `PlatformResult` objects without halting concurrent execution.
- **Known Limitations:**
  - **Rate Limits:** Rapid successive requests may trigger rate limiting or abuse protections on external platform APIs (e.g., GitHub, Pastebin, Telegram).
  - **Spam Filters:** Platforms like Pastebin or Dev.to may flag automated or repetitive identical posts as spam.
