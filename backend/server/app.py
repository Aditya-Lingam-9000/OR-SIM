"""
backend/server/app.py
FastAPI application factory for OR-SIM.

Run
---
    uvicorn backend.server.app:app --reload --port 8000

Or via Python:
    python -m backend.server

CORS
----
All origins are allowed in development (localhost:5173 = Vite dev server).
Tighten in production by setting CORS_ORIGINS env var.

Lifespan
--------
  startup  → store asyncio event loop for WebSocket broadcast thread-bridge
  shutdown → stop pipeline (if running) to prevent zombie audio capture
"""

from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.server.routes    import router
from backend.server.websocket import ws_manager


# ── logging ───────────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
)


# ── lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: give ws_manager the running loop so sync threads can schedule broadcasts.
    Shutdown: stop any running pipeline gracefully.
    """
    # Initialise app state
    app.state.pipeline = None
    app.state.surgery  = None

    # Store event loop for the WS broadcast thread bridge
    loop = asyncio.get_running_loop()
    ws_manager.set_event_loop(loop)
    logger.info("OR-SIM server started.")

    yield   # ── server is running ──

    # Graceful shutdown
    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is not None:
        logger.info("Shutting down active pipeline…")
        await asyncio.to_thread(pipeline.stop)
        app.state.pipeline = None

    logger.info("OR-SIM server stopped.")


# ── app factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    application = FastAPI(
        title       = "OR-SIM API",
        description = "Real-time OR simulator — voice commands → machine states",
        version     = "0.5.0",
        lifespan    = lifespan,
    )

    # Allow any localhost port (Vite may start on 5173, 5174, etc.) and any
    # ngrok / remote origin.  Production deployments should restrict this via
    # the CORS_ORIGINS env-var which overrides the regex when set.
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        # Explicit override: comma-separated list, e.g. "https://my-app.com"
        application.add_middleware(
            CORSMiddleware,
            allow_origins     = cors_origins_env.split(","),
            allow_credentials = True,
            allow_methods     = ["*"],
            allow_headers     = ["*"],
        )
    else:
        # Development default: allow any localhost port + any ngrok/remote origin.
        # allow_origin_regex with allow_credentials=True is safe here because it
        # still requires an explicit matching origin (not a wildcard *).
        application.add_middleware(
            CORSMiddleware,
            allow_origins        = [],   # empty — regex takes precedence
            allow_origin_regex   = r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.ngrok(-free)?\..*",
            allow_credentials    = True,
            allow_methods        = ["*"],
            allow_headers        = ["*"],
        )

    application.include_router(router)

    return application


# Module-level app instance (used by uvicorn and tests)
app = create_app()
