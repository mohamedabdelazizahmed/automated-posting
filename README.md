# Automated Posting Service

A FastAPI application that publishes a message simultaneously to 5 platforms (Telegram, Mastodon, Dev.to, GitHub Gist, Pastebin).

## Tech Stack
- Python 3.12
- FastAPI & Pydantic v2
- HTTPX (Async)
- Docker & Docker Compose

## Setup & Running
1. Copy `.env.example` to `.env` and fill in your credentials.
2. Run with Docker Compose:
   ```bash
   docker compose up --build
   ```
3. Or run locally:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements-dev.txt
   uvicorn app.main:app --port 4000 --reload
   ```

## API Endpoint
- `POST /posting`: Publishes a message containing max 200 characters and exactly one valid URL.
