"""
Unified Vercel API entrypoint for Services mode.
Routes: GET /api/health, POST /api/plan-trip
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        if path.endswith("/health") or path == "/health":
            self._json(200, {"status": "ok", "service": "track-log-api"})
            return
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        if not (path.endswith("/plan-trip") or path == "/plan-trip"):
            self._json(404, {"error": "Not found"})
            return

        try:
            from trips.service import build_trip_plan  # noqa: WPS433

            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
            self._json(200, build_trip_plan(body))
        except ValueError as exc:
            self._json(400, {"error": str(exc)})
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON body"})
        except Exception as exc:
            self._json(500, {"error": f"Trip planning failed: {exc}"})

    def _json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        return
