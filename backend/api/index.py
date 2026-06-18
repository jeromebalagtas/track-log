"""
Vercel serverless API (no Django) — uses the same trip planning modules.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from trips.service import build_trip_plan  # noqa: E402


class handler(BaseHTTPRequestHandler):
  def do_OPTIONS(self):
    self._send(204, b"")

  def do_GET(self):
    path = urlparse(self.path).path.rstrip("/")
    if path.endswith("/health") or path == "/health":
      self._json(200, {"status": "ok", "service": "track-log-api"})
      return
    self._json(404, {"error": "Not found"})

  def do_POST(self):
    path = urlparse(self.path).path.rstrip("/")
    if not path.endswith("/plan-trip") and path != "/plan-trip":
      self._json(404, {"error": "Not found"})
      return

    try:
      length = int(self.headers.get("Content-Length", 0))
      raw = self.rfile.read(length) if length else b"{}"
      body = json.loads(raw.decode("utf-8") or "{}")
      result = build_trip_plan(body)
      self._json(200, result)
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
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")
    self.end_headers()
    self.wfile.write(body)

  def log_message(self, format, *args):
    return
