import json
import machine
import network
import os
import socket
import time

from ui import PAGE_HTML
import skills
from ollama_client import OllamaClient

FAVICON_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="4" fill="#0a0a0a"/><polygon points="12,8 24,16 12,24" fill="#5c614d"/></svg>'


def _import_display():
    try:
        from display import Display
        return Display()
    except Exception as e:
        print("Display not available:", e)
        return None


def load_env():
    conf = {
        "WIFI_SSID": "",
        "WIFI_PASSWORD": "",
        "OLLAMA_MODEL": "llama3.2",
        "OLLAMA_BASE_URL": "https://ollama.com/v1",
        "PROXY_HOST": "192.168.1.197",
        "PROXY_PORT": "9090",
    }
    try:
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    conf[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return conf


class Server:
    def __init__(self, display=None):
        self.cfg = load_env()
        self.ollama = OllamaClient(
            self.cfg.get("PROXY_HOST", "192.168.1.197"),
            int(self.cfg.get("PROXY_PORT", "9090")),
        )
        self.proxy_url = "http://%s:%s" % (
            self.cfg.get("PROXY_HOST", "192.168.1.197"),
            self.cfg.get("PROXY_PORT", "9090"),
        )
        self.active_skill = "general"
        self.ip = ""
        self.disp = display or _import_display()
        if self.disp:
            self.disp.splash()

    def connect_wifi(self):
        ssid = self.cfg.get("WIFI_SSID", "")
        pwd = self.cfg.get("WIFI_PASSWORD", "")
        if not ssid:
            print("WiFi SSID not set in .env")
            return False
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        if sta.isconnected():
            self.ip = sta.ifconfig()[0]
            print(f"Already connected: {self.ip}")
            return True
        print(f"Connecting to '{ssid}'...")
        if self.disp:
            self.disp.lines(["Connecting WiFi..."])
        sta.connect(ssid, pwd)
        for _ in range(45):
            time.sleep_ms(1000)
            if sta.isconnected():
                self.ip = sta.ifconfig()[0]
                print(f"Connected: {self.ip}")
                if self.disp:
                    self.disp.status(self.ip, self.cfg.get("OLLAMA_MODEL", "?"))
                return True
            s = sta.status()
            if s == network.STAT_NO_AP_FOUND:
                print("  AP not found")
                return False
            elif s == network.STAT_WRONG_PASSWORD:
                print("  Wrong password")
                return False
        print(f"WiFi timeout")
        return False

    def _recv(self, client, sz):
        try:
            return client.recv(sz)
        except:
            return b""

    def _send(self, client, code, ctype, body):
        codes = {200: "OK", 400: "Bad", 404: "Not Found", 500: "Error"}
        msg = codes.get(code, "?")
        if isinstance(body, str):
            body = body.encode()
        blen = len(body)
        resp = "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % (code, msg, ctype, blen)
        resp = resp.encode() + body
        try:
            client.send(resp)
        except:
            pass

    def _send_json(self, client, code, data):
        s = json.dumps(data)
        self._send(client, code, "application/json", s)

    def _recv_request(self, client):
        raw = b""
        while True:
            b = self._recv(client, 1)
            if not b:
                return None, None, None
            raw += b
            if raw.endswith(b"\r\n\r\n"):
                break
        head = raw.decode("utf-8")
        lines = head.split("\r\n")
        if not lines:
            return None, None, None
        parts = lines[0].split()
        if len(parts) < 2:
            return None, None, None
        method = parts[0]
        path = parts[1].split("?")[0]
        cl = 0
        for l in lines[1:]:
            if l.lower().startswith("content-length:"):
                cl = int(l.split(":")[1].strip())
                break
        body = b""
        while len(body) < cl:
            b = self._recv(client, cl - len(body))
            if not b:
                break
            body += b
        return method, path, body

    def handle_client(self, client):
        try:
            method, path, body = self._recv_request(client)
            if not method:
                return
            if path == "/" and method == "GET":
                page = PAGE_HTML.replace("__PROXY_URL__", self.proxy_url)
                self._send(client, 200, "text/html", page)
            elif path == "/api/chat" and method == "POST":
                self._api_chat(client, body)
            elif path == "/api/display" and method == "POST":
                self._api_display(client, body)
            elif path == "/api/skills" and method == "GET":
                self._send_json(client, 200, {"skills": skills.get_skills_list()})
            elif path == "/api/skills/activate" and method == "POST":
                self._api_skill_activate(client, body)
            elif path == "/favicon.ico":
                self._send(client, 200, "image/svg+xml", FAVICON_SVG)
            elif path == "/api/info" and method == "GET":
                self._send_json(client, 200, {
                    "model": self.cfg.get("OLLAMA_MODEL", "?"),
                    "ip": self.ip,
                    "skill": self.active_skill,
                })
            else:
                self._send(client, 404, "text/plain", "not found")
        except Exception as e:
            import sys
            buf = ""
            try:
                sys.print_exception(e)
            except:
                pass
            try:
                self._send(client, 500, "text/plain", str(e))
            except:
                pass
        finally:
            try:
                client.close()
            except:
                pass

    def _api_chat(self, client, body):
        try:
            data = json.loads(body)
        except:
            self._send_json(client, 400, {"error": "bad json"})
            return
        msg = data.get("message", "")
        skill = data.get("skill", self.active_skill)
        if not msg:
            self._send_json(client, 400, {"error": "empty message"})
            return
        result = self.ollama.chat(msg, skill)
        self._send_json(client, 200, result)

    def _api_skill_activate(self, client, body):
        try:
            data = json.loads(body)
        except:
            self._send_json(client, 400, {"error": "bad json"})
            return
        s = data.get("skill", "general")
        if skills.get_skill(s) is None:
            self._send_json(client, 400, {"error": "unknown skill"})
            return
        self.active_skill = s
        self._send_json(client, 200, {"ok": True, "skill": s})

    def _api_display(self, client, body):
        try:
            data = json.loads(body)
        except:
            self._send_json(client, 400, {"error": "bad json"})
            return
        if self.disp:
            self.disp.show_chat(data.get("user", ""), data.get("ai", ""))
        self._send_json(client, 200, {"ok": True})

    def run(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", 80))
            s.listen(3)
        except Exception as e:
            print(f"Bind error: {e}")
            return
        print(f"Server on http://{self.ip}:80")
        while True:
            try:
                client, addr = s.accept()
                self.handle_client(client)
            except Exception as e:
                print(f"accept err: {e}")
