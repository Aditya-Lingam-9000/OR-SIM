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
    allowed_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    ).split(",")

    application = FastAPI(
        title       = "OR-SIM API",
        description = "Real-time OR simulator — voice commands → machine states",
        version     = "0.5.0",
        lifespan    = lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins     = allowed_origins,
        allow_credentials = True,
        allow_methods     = ["*"],
        allow_headers     = ["*"],
    )

    application.include_router(router)

    return application


# Module-level app instance (used by uvicorn and tests)
app = create_app()
