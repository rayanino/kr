"""Launch the KR Autonomous System Dashboard.

Usage:
    python scripts/dashboard.py [--port PORT]

Opens http://localhost:8000 (or custom port) serving the dashboard.
"""
from __future__ import annotations

import argparse
import logging
import sys
import webbrowser
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="KR Autonomous Dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    args = parser.parse_args()

    import uvicorn
    from scripts.autonomous_dashboard.app import app  # noqa: F811

    url = f"http://localhost:{args.port}"
    logger.info("Starting KR Autonomous Dashboard at %s", url)

    if not args.no_browser:
        # Open browser after a short delay (uvicorn blocks)
        import threading
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
