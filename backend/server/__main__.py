"""
backend/server/__main__.py
CLI entry point: python -m backend.server

Examples
--------
    python -m backend.server                          # default port 8000
    python -m backend.server --port 8080 --reload
    python -m backend.server --host 0.0.0.0 --port 8000
"""

import argparse
import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(
        prog        = "python -m backend.server",
        description = "OR-SIM FastAPI + WebSocket server",
    )
    parser.add_argument("--host",   default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port",   default=8000, type=int, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot-reload (dev only)")
    parser.add_argument("--log-level", default="info", dest="log_level")
    args = parser.parse_args()

    uvicorn.run(
        "backend.server.app:app",
        host      = args.host,
        port      = args.port,
        reload    = args.reload,
        log_level = args.log_level,
    )


if __name__ == "__main__":
    main()
