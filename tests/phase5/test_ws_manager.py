"""
tests/phase5/test_ws_manager.py
Unit tests for backend/server/websocket.py — ConnectionManager.

Tests use pytest-asyncio for async methods and lightweight mock WebSockets.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.server.websocket import ConnectionManager
from backend.data.models      import ORStateSnapshot


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_mock_ws(raises_on_send: bool = False) -> MagicMock:
    """Create a mock WebSocket with async send_text and accept."""
    ws = MagicMock()
    ws.accept      = AsyncMock()
    if raises_on_send:
        ws.send_text = AsyncMock(side_effect=RuntimeError("connection closed"))
    else:
        ws.send_text = AsyncMock()
    return ws


def _make_snapshot() -> ORStateSnapshot:
    return ORStateSnapshot(
        surgery        = "Heart Transplantation",
        machine_states = {"0": ["Ventilator"], "1": ["Patient Monitor"]},
    )


# ── connect / disconnect ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_connect_adds_client():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    await mgr.connect(ws)
    assert mgr.client_count == 1


@pytest.mark.asyncio
async def test_connect_calls_accept():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    await mgr.connect(ws)
    ws.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect_removes_client():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    await mgr.connect(ws)
    mgr.disconnect(ws)
    assert mgr.client_count == 0


@pytest.mark.asyncio
async def test_disconnect_unknown_client_is_noop():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    mgr.disconnect(ws)   # never connected — should not raise
    assert mgr.client_count == 0


@pytest.mark.asyncio
async def test_multiple_clients_counted():
    mgr = ConnectionManager()
    ws1, ws2, ws3 = _make_mock_ws(), _make_mock_ws(), _make_mock_ws()
    for ws in (ws1, ws2, ws3):
        await mgr.connect(ws)
    assert mgr.client_count == 3
    mgr.disconnect(ws2)
    assert mgr.client_count == 2


# ── broadcast ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_broadcast_sends_to_all_clients():
    mgr  = ConnectionManager()
    ws1  = _make_mock_ws()
    ws2  = _make_mock_ws()
    await mgr.connect(ws1)
    await mgr.connect(ws2)

    payload = {"test": "data"}
    await mgr.broadcast(payload)

    expected = json.dumps(payload, ensure_ascii=False)
    ws1.send_text.assert_awaited_once_with(expected)
    ws2.send_text.assert_awaited_once_with(expected)


@pytest.mark.asyncio
async def test_broadcast_removes_dead_client():
    mgr  = ConnectionManager()
    dead = _make_mock_ws(raises_on_send=True)
    live = _make_mock_ws()
    await mgr.connect(dead)
    await mgr.connect(live)

    await mgr.broadcast({"x": 1})

    assert mgr.client_count == 1   # dead was removed
    live.send_text.assert_awaited_once()
    dead.send_text.assert_awaited_once()   # attempted, then pruned


@pytest.mark.asyncio
async def test_broadcast_no_clients_noop():
    mgr = ConnectionManager()
    # Should not raise
    await mgr.broadcast({"x": 1})


@pytest.mark.asyncio
async def test_broadcast_sends_valid_json():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    await mgr.connect(ws)

    data = {"surgery": "Heart Transplantation", "machine_states": {"0": [], "1": ["Monitor"]}}
    await mgr.broadcast(data)

    sent = ws.send_text.call_args.args[0]
    parsed = json.loads(sent)
    assert parsed["surgery"] == "Heart Transplantation"


# ── send_to ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_to_single_client():
    mgr = ConnectionManager()
    ws  = _make_mock_ws()
    await mgr.send_to(ws, {"hello": "world"})
    ws.send_text.assert_awaited_once_with('{"hello": "world"}')


@pytest.mark.asyncio
async def test_send_to_failing_client_does_not_raise():
    mgr = ConnectionManager()
    ws  = _make_mock_ws(raises_on_send=True)
    await mgr.send_to(ws, {"hello": "world"})   # should not raise


# ── set_event_loop + broadcast_from_thread ────────────────────────────────────

def test_broadcast_from_thread_no_loop_is_noop():
    """No event loop stored — should log warning and not crash."""
    mgr      = ConnectionManager()
    snapshot = _make_snapshot()
    mgr.broadcast_from_thread(snapshot)   # must not raise


def test_broadcast_from_thread_no_clients_skips_scheduling():
    """Event loop stored, but no clients — should not call run_coroutine_threadsafe."""
    loop     = asyncio.new_event_loop()
    mgr      = ConnectionManager()
    mgr.set_event_loop(loop)
    snapshot = _make_snapshot()

    with patch("backend.server.websocket.asyncio.run_coroutine_threadsafe") as mock_rcts:
        mgr.broadcast_from_thread(snapshot)
        mock_rcts.assert_not_called()

    loop.close()


@pytest.mark.asyncio
async def test_broadcast_from_thread_schedules_on_loop():
    """Event loop + clients present — run_coroutine_threadsafe should be called."""
    loop = asyncio.get_running_loop()
    mgr  = ConnectionManager()
    mgr.set_event_loop(loop)

    ws = _make_mock_ws()
    await mgr.connect(ws)

    snapshot = _make_snapshot()

    with patch("backend.server.websocket.asyncio.run_coroutine_threadsafe") as mock_rcts:
        mgr.broadcast_from_thread(snapshot)
        mock_rcts.assert_called_once()
        # First arg is a coroutine, second is the loop
        call_loop = mock_rcts.call_args.args[1]
        assert call_loop is loop


def test_set_event_loop_stores_loop():
    loop = asyncio.new_event_loop()
    mgr  = ConnectionManager()
    mgr.set_event_loop(loop)
    assert mgr._loop is loop
    loop.close()
