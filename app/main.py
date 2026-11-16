from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.routes import router as posting_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage shared resources during application lifespan."""
    app.state.client = httpx.AsyncClient(timeout=30.0)
    yield
    await app.state.client.aclose()


app = FastAPI(
    title="Automated Posting Service",
    description="Publishes messages concurrently to multiple social platforms.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(posting_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}
