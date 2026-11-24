#!/usr/bin/env python3
import http.client
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "ollama.com")
OLLAMA_PATH = os.environ.get("OLLAMA_PATH", "/v1/chat/completions")
API_KEY = os.environ.get("OLLAMA_API_KEY", "")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
PORT = int(os.environ.get("PROXY_PORT", "9090"))
ALLOWED_ORIGINS = {
    o.strip().rstrip("/")
    for o in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
}
RATE_LIMIT_PER_MIN = max(1, int(os.environ.get("RATE_LIMIT_PER_MIN", "20")))
MAX_MESSAGE_LEN = 4000
MAX_BODY = 32000
RATE_WINDOW = 60

_requests = {}


class Handler(BaseHTTPRequestHandler):
    def _origin(self):
        origin = self.headers.get("Origin", "").strip().rstrip("/")
        return origin if origin and origin in ALLOWED_ORIGINS else None

    def _rate_limited(self):
        ip = self.client_address[0]
        now = time.monotonic()
        start, count = _requests.get(ip, (now, 0))
        if now - start >= RATE_WINDOW:
            start, count = now, 0
        count += 1
        _requests[ip] = (start, count)
        return count > RATE_LIMIT_PER_MIN

    def do_OPTIONS(self):
        origin = self._origin()
        if not origin:
            self._json(403, {"error": "origin not allowed"})
            return
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self._cors(origin)
        self.end_headers()

    def do_POST(self):
        origin = self._origin()
        if not origin:
            self._json(403, {"error": "origin not allowed"})
            return
        if self._rate_limited():
            self._json(429, {"error": "rate limit exceeded"}, origin)
            return
        n = int(self.headers.get("Content-Length", 0))
        if n > MAX_BODY:
            self._json(413, {"error": "request too large"}, origin)
            return
        body = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(body)
        except (ValueError, TypeError):
            self._json(400, {"error": "bad json"}, origin)
            return
        if not isinstance(data, dict):
            self._json(400, {"error": "bad request"}, origin)
            return

        msg = data.get("message", "")
        if not isinstance(msg, str) or not msg.strip():
            self._json(400, {"error": "empty message"}, origin)
            return
        if len(msg) > MAX_MESSAGE_LEN:
            self._json(413, {"error": "message too long"}, origin)
            return
        sp = data.get("system_prompt", "You are a helpful assistant.")
        if not isinstance(sp, str):
            sp = "You are a helpful assistant."
        payload = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": sp},
                {"role": "user", "content": msg},
            ],
            "stream": False,
        })

        try:
            conn = http.client.HTTPSConnection(OLLAMA_HOST, timeout=30)
            conn.request("POST", OLLAMA_PATH, body=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
            })
            r = conn.getresponse()
            raw = r.read()
            conn.close()
            if r.status != 200:
                self._json(r.status, {"error": raw.decode()[:300]}, origin)
                return
            result = json.loads(raw)
            c = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            self._json(200, {"response": c.strip()}, origin)
        except Exception as e:
            self._json(500, {"error": str(e)}, origin)

    def _cors(self, origin):
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")

    def _json(self, code, data, origin=None):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        if origin:
            self._cors(origin)
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, fmt, *a):
        sys.stderr.write(f"[proxy] {fmt % a}\n")


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: set OLLAMA_API_KEY on the host", file=sys.stderr)
        sys.exit(1)
    if not ALLOWED_ORIGINS:
        print("WARNING: ALLOWED_ORIGINS is empty; all requests will be rejected", file=sys.stderr)
    s = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Proxy :{PORT} -> {OLLAMA_HOST}{OLLAMA_PATH} [{MODEL}]", flush=True)
    s.serve_forever()
