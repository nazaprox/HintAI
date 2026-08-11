"""HintAI V2 - production FastAPI application.

The application layer stays intentionally thin. Feature-specific logic belongs
in its dedicated package (auth, abuse, ads, AI, credits, help_me, learn,
streak, tools, uploads).
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS


APP_NAME = "HintAI"
APP_VERSION = "2.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Keep startup lightweight. External clients/resources should be created
    # lazily by their own modules so a cold start does not make unnecessary
    # API calls or consume Gemini quota.
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI educational tutor for guided problem solving and learning.",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT", "production") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "production") != "production" else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-User-ID"],
)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    """Basic service information."""
    return {
        "service": APP_NAME,
        "status": "online",
        "version": APP_VERSION,
    }


@app.get("/health", tags=["system"])
@app.get("/api/health", tags=["system"], include_in_schema=False)
async def health() -> dict[str, str]:
    """Render-compatible health endpoint."""
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
    }


@app.get("/ready", tags=["system"])
@app.get("/api/ready", tags=["system"], include_in_schema=False)
async def ready() -> dict[str, str]:
    """Readiness endpoint for deployment/platform checks."""
    return {
        "status": "ready",
        "service": APP_NAME,
        "version": APP_VERSION,
    }
