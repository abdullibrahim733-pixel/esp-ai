#!/usr/bin/env python3
"""Upload firmware files to ESP32 via serial raw REPL."""

import serial
import base64
import time
import sys
import os

FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), "firmware")
PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BAUD = 115200

FILES = [
    "boot.py",
    "main.py",
    "lib/__init__.py",
    "lib/server.py",
    "lib/ui.py",
    "lib/ollama_client.py",
    "lib/skills.py",
    "lib/ssd1306.py",
    "lib/display.py",
]


def upload_file(ser, remote, data):
    b64 = base64.b64encode(data).decode()
    d = remote.rsplit("/", 1)
    mkdir = ""
    if len(d) > 1 and d[0]:
        mkdir = f"import os\ntry:os.mkdir('{d[0]}')\nexcept:pass\n"
    ser.write(b"\x01")
    time.sleep(0.3)
    ser.reset_input_buffer()
    code = f"{mkdir}import ubinascii\nf=open('{remote}','wb')\n"
    ser.write(code.encode())
    time.sleep(0.2)
    for i in range(0, len(b64), 200):
        ser.write(f"f.write(ubinascii.a2b_base64('{b64[i:i+200]}'))\n".encode())
        time.sleep(0.02)
    ser.write(b"f.close()\nprint('OK')\n")
    ser.write(b"\x04")
    time.sleep(3)
    out = ser.read(500)
    ok = b"OK" in out
    print(f"  {'OK' if ok else 'FAIL'} {remote} ({len(data)}b)")


def main():
    print(f"Uploading to {PORT} at {BAUD} baud...")
    ser = serial.Serial(PORT, BAUD, timeout=10)
    time.sleep(1)
    ser.reset_input_buffer()
    for _ in range(10):
        ser.write(b"\x03")
        time.sleep(0.05)
    time.sleep(0.3)

    for path in FILES:
        local = os.path.join(FIRMWARE_DIR, path)
        if not os.path.exists(local):
            print(f"  SKIP {path} (not found)")
            continue
        with open(local, "rb") as f:
            data = f.read()
        upload_file(ser, "/" + path, data)

    ser.close()
    print("Done.")


if __name__ == "__main__":
    main()
