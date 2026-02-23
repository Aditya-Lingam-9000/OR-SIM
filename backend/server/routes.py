"""
backend/server/routes.py
REST and WebSocket route handlers for OR-SIM.

Endpoints
---------
  POST  /api/session/start   — start a new pipeline session for a surgery
  POST  /api/session/stop    — gracefully stop the running pipeline
  GET   /api/state           — poll current machine states (REST fallback)
  WS    /ws/state            — live WebSocket stream of state updates
"""

from __future__ import annotations

import asyncio
from typing import Literal

import numpy as np
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel

from backend.data.surgeries    import SurgeryType
from backend.server.websocket  import ws_manager

router = APIRouter()

# ── request/response schemas ──────────────────────────────────────────────────

_SURGERY_MAP: dict[str, SurgeryType] = {
    "heart":  SurgeryType.HEART_TRANSPLANT,
    "liver":  SurgeryType.LIVER_RESECTION,
    "kidney": SurgeryType.KIDNEY_PCNL,
}

class SessionStartRequest(BaseModel):
    surgery:      Literal["heart", "liver", "kidney"]
    n_gpu_layers: int = -1  # -1 = full GPU, 0 = CPU only


class SessionStartResponse(BaseModel):
    status:  str
    surgery: str
    message: str


class SessionStopResponse(BaseModel):
    status:  str
    message: str


class StateResponse(BaseModel):
    status:  str
    state:   dict


# ── session endpoints ─────────────────────────────────────────────────────────

@router.post("/api/session/start", response_model=SessionStartResponse)
async def start_session(body: SessionStartRequest, request: Request):
    """
    Start the OR pipeline for the chosen surgery.
    If a pipeline is already running it is stopped first (surgery change).
    """
    app_state = request.app.state

    surgery = _SURGERY_MAP[body.surgery]

    # Stop existing pipeline if one is running
    if getattr(app_state, "pipeline", None) is not None:
        logger.info(f"Stopping previous pipeline before restart…")
        await asyncio.to_thread(app_state.pipeline.stop)
        app_state.pipeline = None

    # Import here to avoid loading heavy deps on import
    from backend.pipeline.pipeline import ORPipeline

    pipeline = ORPipeline(surgery=surgery, n_gpu_layers=body.n_gpu_layers)

    # Register WebSocket broadcast callback on the state manager
    pipeline.state_manager.register_callback(ws_manager.broadcast_from_thread)

    # Start in server mode — no local microphone.
    # Audio is streamed from the browser via the /ws/audio WebSocket endpoint.
    await asyncio.to_thread(pipeline.start, False)

    app_state.pipeline = pipeline
    app_state.surgery  = surgery

    logger.info(f"Session started — surgery={surgery.value}, gpu_layers={body.n_gpu_layers}")

    return SessionStartResponse(
        status  = "started",
        surgery = surgery.value,
        message = f"Pipeline running for {surgery.value}. Connect to WS /ws/state for live updates.",
    )


@router.post("/api/session/stop", response_model=SessionStopResponse)
async def stop_session(request: Request):
    """Stop the currently running pipeline."""
    app_state = request.app.state

    if getattr(app_state, "pipeline", None) is None:
        raise HTTPException(status_code=400, detail="No active pipeline session.")

    await asyncio.to_thread(app_state.pipeline.stop)
    app_state.pipeline = None
    app_state.surgery  = None

    logger.info("Session stopped by API request.")
    return SessionStopResponse(status="stopped", message="Pipeline stopped successfully.")


# ── state polling endpoint ─────────────────────────────────────────────────────

@router.get("/api/state")
async def get_state(request: Request):
    """
    Return current machine states as JSON (REST polling fallback).
    Returns 200 with status='idle' when no session is active so clients
    can poll this endpoint safely at any time (including before session start).
    """
    app_state = request.app.state

    if getattr(app_state, "pipeline", None) is None:
        return {
            "status":  "idle",
            "message": "No active pipeline session. Start one with POST /api/session/start.",
            "state":   {},
        }

    snapshot = app_state.pipeline.state_manager.get_snapshot()
    return {"status": "ok", "state": snapshot.to_json_dict()}


# ── browser audio stream endpoint ────────────────────────────────────────────

@router.websocket("/ws/audio")
async def websocket_audio(ws: WebSocket):
    """
    Receives raw PCM audio from the browser microphone.

    Protocol
    --------
    * Client connects after session is started.
    * Each message is a binary frame of float32 samples at 16 kHz
      (any chunk size — the VAD re-chunks to BLOCK_SIZE=320 internally).
    * Server feeds each chunk into pipeline.push_audio() → VAD → ASR → LLM.
    * Connection should be closed when the session stops.
    """
    await ws.accept()
    logger.info("Audio WS: browser microphone connected.")
    try:
        while True:
            raw = await ws.receive_bytes()
            block = np.frombuffer(raw, dtype=np.float32).copy()
            pipeline = getattr(ws.app.state, "pipeline", None)
            if pipeline is not None:
                pipeline.push_audio(block)
    except WebSocketDisconnect:
        logger.info("Audio WS: browser microphone disconnected.")
    except Exception as exc:
        logger.warning(f"Audio WS error: {exc!r}")


# ── health check ──────────────────────────────────────────────────────────────

@router.get("/api/health")
async def health(request: Request):
    """Simple health check — returns server status and active surgery."""
    app_state = request.app.state
    pipeline  = getattr(app_state, "pipeline", None)
    return {
        "status":        "ok",
        "pipeline_active": pipeline is not None,
        "surgery":         getattr(app_state, "surgery", None) and app_state.surgery.value,
        "ws_clients":      ws_manager.client_count,
    }


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@router.websocket("/ws/state")
async def websocket_state(ws: WebSocket):
    """
    WebSocket endpoint — streams live OR machine state updates.

    On connect:
      1. Client is accepted.
      2. Current state is sent immediately (so the UI can initialise without waiting).
      3. Client waits for broadcast messages triggered by StateManager callbacks.

    The server only sends; it never reads from the client.
    """
    await ws_manager.connect(ws)

    # Send current state immediately on connect (so client can initialise)
    # Access app state through the WebSocket's app reference
    pipeline = getattr(ws.app.state, "pipeline", None)
    if pipeline is not None:
        snapshot = pipeline.state_manager.get_snapshot()
        await ws_manager.send_to(ws, snapshot.to_json_dict())
    else:
        await ws_manager.send_to(ws, {"status": "no_session", "message": "No pipeline active yet."})

    try:
        # Keep connection alive by reading (and discarding) any client messages
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception as exc:
        logger.warning(f"WS handler error: {exc!r}")
        ws_manager.disconnect(ws)
