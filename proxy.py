#!/usr/bin/env python3
import json, os, sys, http.client
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "ollama.com")
OLLAMA_PATH = os.environ.get("OLLAMA_PATH", "/v1/chat/completions")
API_KEY = os.environ.get("OLLAMA_API_KEY", "")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
PORT = int(os.environ.get("PROXY_PORT", "9090"))


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(body)
        except:
            self._json(400, {"error": "bad json"})
            return

        msg = data.get("message", "")
        sp = data.get("system_prompt", "You are a helpful assistant.")
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
                self._json(r.status, {"error": raw.decode()[:300]})
                return
            result = json.loads(raw)
            c = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            self._json(200, {"response": c.strip()})
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self._cors()
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, fmt, *a):
        sys.stderr.write(f"[proxy] {fmt%a}\n")


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: set OLLAMA_API_KEY", file=sys.stderr)
        sys.exit(1)
    s = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Proxy :{PORT} -> {OLLAMA_HOST}{OLLAMA_PATH} [{MODEL}]", flush=True)
    s.serve_forever()
