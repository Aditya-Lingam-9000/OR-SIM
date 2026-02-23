# backend/server — Phase 5: FastAPI + WebSocket server

from backend.server.app       import app, create_app
from backend.server.websocket import ws_manager

__all__ = ["app", "create_app", "ws_manager"]
