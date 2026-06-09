import json
import socket

import skills


class OllamaClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def chat(self, message, skill_id="general"):
        sp = skills.get_system_prompt(skill_id)
        body = json.dumps({
            "message": message,
            "skill": skill_id,
            "system_prompt": sp,
        })

        try:
            s = socket.socket()
            s.settimeout(30)
            s.connect((self.host, self.port))

            req = (
                f"POST / HTTP/1.1\r\n"
                f"Host: {self.host}:{self.port}\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
                f"{body}"
            )
            s.send(req.encode())

            resp = b""
            while True:
                b = s.recv(4096)
                if not b:
                    break
                resp += b
            s.close()

            parts = resp.split(b"\r\n\r\n", 1)
            if len(parts) < 2:
                return {"error": "no body"}
            body = parts[1].decode()
            data = json.loads(body)
            if "error" in data:
                return {"error": data["error"]}
            return {"response": data.get("response", "")}
        except Exception as e:
            return {"error": str(e)}
