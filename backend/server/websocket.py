"""
backend/server/websocket.py
WebSocket connection manager for OR-SIM live state broadcasting.

Design
------
* ConnectionManager is a single shared instance (imported by app.py and routes.py).
* Async API: connect/disconnect/broadcast are all async — called from FastAPI WS handlers.
* Sync bridge: broadcast_from_thread() is called by the StateManager callback running in
  the LLM worker thread (sync). It uses asyncio.run_coroutine_threadsafe() so it can safely
  schedule a coroutine onto the FastAPI event loop without blocking the worker.

Client lifecycle
----------------
  1. Client connects → accepted + immediately receives current state snapshot.
  2. On every StateManager update → broadcast() pushes new snapshot to all clients.
  3. Client disconnects (browser closed / network drop) → removed from active set.
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from backend.data.models import ORStateSnapshot


class ConnectionManager:
    """
    Manages all active WebSocket connections and broadcasts state updates.

    Thread-safety
    -------------
    * _clients is mutated only inside the asyncio event loop (via connect/disconnect/broadcast).
    * broadcast_from_thread() is the only entry point from non-async threads; it uses
      run_coroutine_threadsafe which is documented thread-safe.
    """

    def __init__(self) -> None:
        self._clients:  set[WebSocket]                       = set()
        self._loop:     Optional[asyncio.AbstractEventLoop]  = None
        self._lock:     threading.Lock                       = threading.Lock()

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Store the running asyncio event loop. Call once from lifespan startup."""
        self._loop = loop
        logger.info("ConnectionManager: event loop stored.")

    # ── async API (called from FastAPI coroutines) ────────────────────────────

    async def connect(self, ws: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await ws.accept()
        with self._lock:
            self._clients.add(ws)
        logger.info(f"WS client connected  — total={len(self._clients)}")

    def disconnect(self, ws: WebSocket) -> None:
        """Remove a disconnected client."""
        with self._lock:
            self._clients.discard(ws)
        logger.info(f"WS client disconnected — total={len(self._clients)}")

    async def broadcast(self, data: dict) -> None:
        """
        Send JSON payload to all connected clients.
        Clients that have disconnected are silently removed.
        """
        payload = json.dumps(data, ensure_ascii=False)
        dead: set[WebSocket] = set()

        with self._lock:
            clients_snapshot = set(self._clients)

        for ws in clients_snapshot:
            try:
                await ws.send_text(payload)
            except Exception as exc:
                logger.debug(f"WS send failed ({exc!r}) — marking client for removal")
                dead.add(ws)

        if dead:
            with self._lock:
                self._clients -= dead
            logger.info(f"Removed {len(dead)} dead WS clients — total={len(self._clients)}")

    async def send_to(self, ws: WebSocket, data: dict) -> None:
        """Send a payload to a single client (used on connect to send current state)."""
        try:
            await ws.send_text(json.dumps(data, ensure_ascii=False))
        except Exception as exc:
            logger.warning(f"WS send_to failed: {exc!r}")

    # ── sync bridge (called from LLM worker thread) ───────────────────────────

    def broadcast_from_thread(self, snapshot: ORStateSnapshot) -> None:
        """
        Thread-safe entry point for the StateManager callback.
        Schedules broadcast() onto the asyncio event loop from the LLM worker thread.
        """
        if self._loop is None:
            logger.warning("broadcast_from_thread: no event loop stored — skipping broadcast")
            return
        if not self._clients:
            return   # No clients — skip scheduling

        asyncio.run_coroutine_threadsafe(
            self.broadcast(snapshot.to_json_dict()),
            self._loop,
        )

    # ── inspection ────────────────────────────────────────────────────────────

    @property
    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)


# ── module-level singleton ────────────────────────────────────────────────────
ws_manager = ConnectionManager()
