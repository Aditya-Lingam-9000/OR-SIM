"""
tests/phase5/test_routes.py
Integration tests for backend/server/routes.py — REST + WebSocket endpoints.

Uses FastAPI's TestClient (wraps httpx + anyio) which supports:
  - Synchronous HTTP requests against async routes
  - WebSocket connections: `with client.websocket_connect("/ws/state") as ws:`

All heavy dependencies (ORPipeline, MedGemmaModel, AudioCapture) are mocked.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.data.models    import ORStateSnapshot
from backend.data.surgeries import SurgeryType
from backend.server.app     import create_app


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_snapshot(surgery: str = "Heart Transplantation") -> ORStateSnapshot:
    return ORStateSnapshot(
        surgery        = surgery,
        machine_states = {"0": ["Ventilator"], "1": ["Patient Monitor"]},
        transcription  = "turn on the patient monitor",
        reasoning      = "Activating monitoring.",
    )


def _mock_pipeline(surgery: SurgeryType = SurgeryType.HEART_TRANSPLANT) -> MagicMock:
    """Build a minimal mock ORPipeline with a wired-up mock StateManager."""
    mock_sm = MagicMock()
    mock_sm.get_snapshot.return_value = _make_snapshot(surgery.value)
    mock_sm.register_callback         = MagicMock()

    pipeline = MagicMock()
    pipeline.state_manager = mock_sm
    pipeline.start         = MagicMock()   # sync — called via asyncio.to_thread
    pipeline.stop          = MagicMock()   # sync — called via asyncio.to_thread
    return pipeline


@pytest.fixture()
def client():
    """Fresh TestClient with a clean app instance for each test."""
    app = create_app()
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ── GET /api/health ───────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_health_no_pipeline(self, client):
        r = client.get("/api/health")
        assert r.json()["pipeline_active"] is False

    def test_health_ws_clients_zero(self, client):
        r = client.get("/api/health")
        assert r.json()["ws_clients"] == 0

    def test_health_surgery_none_without_session(self, client):
        r = client.get("/api/health")
        assert r.json()["surgery"] is None


# ── GET /api/state ────────────────────────────────────────────────────────────

class TestGetState:
    def test_state_no_session_returns_400(self, client):
        r = client.get("/api/state")
        assert r.status_code == 400

    def test_state_no_session_error_message(self, client):
        r = client.get("/api/state")
        assert "No active pipeline session" in r.json()["detail"]

    def test_state_with_session_returns_200(self, client):
        app = create_app()
        mock_pl = _mock_pipeline()
        with TestClient(app) as c:
            with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
                c.post("/api/session/start", json={"surgery": "heart"})
            r = c.get("/api/state")
        assert r.status_code == 200

    def test_state_with_session_contains_machine_states(self, client):
        app = create_app()
        mock_pl = _mock_pipeline()
        with TestClient(app) as c:
            with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
                c.post("/api/session/start", json={"surgery": "heart"})
            r = c.get("/api/state")
        data = r.json()
        assert "state" in data
        assert "machine_states" in data["state"]


# ── POST /api/session/start ───────────────────────────────────────────────────

class TestSessionStart:
    def test_start_returns_200(self, client):
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=_mock_pipeline()):
            r = client.post("/api/session/start", json={"surgery": "heart"})
        assert r.status_code == 200

    def test_start_status_is_started(self, client):
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=_mock_pipeline()):
            r = client.post("/api/session/start", json={"surgery": "heart"})
        assert r.json()["status"] == "started"

    def test_start_returns_correct_surgery_name(self, client):
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=_mock_pipeline()):
            r = client.post("/api/session/start", json={"surgery": "heart"})
        assert "Heart" in r.json()["surgery"]

    @pytest.mark.parametrize("surgery_key,expected", [
        ("heart",  "Heart Transplantation"),
        ("liver",  "Liver Resection"),
        ("kidney", "Kidney PCNL"),
    ])
    def test_start_all_surgery_types(self, client, surgery_key, expected):
        from backend.data.surgeries import SurgeryType, MACHINES
        stype = {"heart": SurgeryType.HEART_TRANSPLANT,
                 "liver": SurgeryType.LIVER_RESECTION,
                 "kidney": SurgeryType.KIDNEY_PCNL}[surgery_key]
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=_mock_pipeline(stype)):
            r = client.post("/api/session/start", json={"surgery": surgery_key})
        assert r.status_code == 200

    def test_start_invalid_surgery_returns_422(self, client):
        r = client.post("/api/session/start", json={"surgery": "appendix"})
        assert r.status_code == 422

    def test_start_registers_ws_callback(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        mock_pl.state_manager.register_callback.assert_called_once()

    def test_start_calls_pipeline_start(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        mock_pl.start.assert_called_once()

    def test_start_twice_stops_first_pipeline(self, client):
        """Starting a new session should stop the previous one."""
        app = create_app()
        pl1 = _mock_pipeline()
        pl2 = _mock_pipeline(SurgeryType.LIVER_RESECTION)
        with TestClient(app) as c:
            with patch("backend.pipeline.pipeline.ORPipeline", return_value=pl1):
                c.post("/api/session/start", json={"surgery": "heart"})
            with patch("backend.pipeline.pipeline.ORPipeline", return_value=pl2):
                c.post("/api/session/start", json={"surgery": "liver"})
        pl1.stop.assert_called_once()


# ── POST /api/session/stop ────────────────────────────────────────────────────

class TestSessionStop:
    def test_stop_no_session_returns_400(self, client):
        r = client.post("/api/session/stop")
        assert r.status_code == 400

    def test_stop_with_session_returns_200(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        r = client.post("/api/session/stop")
        assert r.status_code == 200

    def test_stop_status_is_stopped(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        r = client.post("/api/session/stop")
        assert r.json()["status"] == "stopped"

    def test_stop_calls_pipeline_stop(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        client.post("/api/session/stop")
        mock_pl.stop.assert_called_once()

    def test_stop_clears_pipeline_from_app_state(self, client):
        """After stop, GET /api/state should return 400 (no session)."""
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        client.post("/api/session/stop")
        r = client.get("/api/state")
        assert r.status_code == 400

    def test_stop_twice_returns_400_second_time(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        client.post("/api/session/stop")
        r = client.post("/api/session/stop")
        assert r.status_code == 400


# ── WS /ws/state ──────────────────────────────────────────────────────────────

class TestWebSocket:
    def test_ws_connect_no_session_sends_no_session_message(self, client):
        """Without a running pipeline, WS connect should receive a no_session payload."""
        with client.websocket_connect("/ws/state") as ws:
            msg  = ws.receive_text()
            data = json.loads(msg)
        assert data.get("status") == "no_session"

    def test_ws_connect_with_session_receives_current_state(self, client):
        """With a running pipeline, WS connect should immediately receive current state."""
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        with client.websocket_connect("/ws/state") as ws:
            msg  = ws.receive_text()
            data = json.loads(msg)
        # Should be a valid state snapshot with surgery + machine_states
        assert "machine_states" in data
        assert "surgery" in data

    def test_ws_state_snapshot_has_both_keys(self, client):
        mock_pl = _mock_pipeline()
        with patch("backend.pipeline.pipeline.ORPipeline", return_value=mock_pl):
            client.post("/api/session/start", json={"surgery": "heart"})
        with client.websocket_connect("/ws/state") as ws:
            data = json.loads(ws.receive_text())
        assert "0" in data["machine_states"]
        assert "1" in data["machine_states"]

    def test_multiple_ws_clients_can_connect(self, client):
        """Two simultaneous WebSocket connections should both be accepted."""
        with (
            client.websocket_connect("/ws/state") as ws1,
            client.websocket_connect("/ws/state") as ws2,
        ):
            msg1 = json.loads(ws1.receive_text())
            msg2 = json.loads(ws2.receive_text())
        # Both should have received some response
        assert isinstance(msg1, dict)
        assert isinstance(msg2, dict)
