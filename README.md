# ESP32 AI Chat Assistant

An ESP32-powered AI chat assistant with an OLED display, running MicroPython. The web UI connects to the Ollama Cloud API via a local proxy bridge, with skills-based prompting and an engineering-focused design.

```
┌─────────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Browser (Host)     │────→│  Proxy       │────→│  Ollama     │
│  http://esp-ip/     │     │  :9090       │     │  Cloud API  │
└─────────────────────┘     └──────────────┘     └─────────────┘
         │
         │ (HTTP)
         ▼
┌─────────────────────┐
│  ESP32 (192.168.x.x)│
│  - HTML/CSS/JS UI   │
│  - Skills API       │
│  - OLED Display     │
└─────────────────────┘
```

## Features

- **AI Chat** — chat with Ollama cloud models (gemma3:4b) through a local proxy
- **Skills System** — 6 specialized personas (General, Code Expert, Summarizer, Translator, Explainer, Debugger) with custom system prompts
- **OLED Display** — scrolls chat exchanges on a 128×64 SSD1306 display (optional, graceful fallback)
- **Engineering UI** — clean Material 3 tonal palette, Tailwind CSS, Source Serif 4 for assistant responses
- **Standalone** — runs on ESP32 powered via USB or external supply, fully headless after boot

## Hardware Requirements

| Component | Specification | Notes |
|-----------|--------------|-------|
| Microcontroller | ESP32-D0WD-V3 | 4MB flash, any ESP32 dev board works |
| OLED Display (opt.) | SSD1306 128×64 I2C | Address 0x3C, SDA=GPIO21, SCL=GPIO22 |
| Power | 5V USB or 3.3V regulated | ~200mA for ESP32 + OLED |
| Host Machine | Any computer on same LAN | Runs the proxy bridge |

## Wiring

| ESP32 GPIO | OLED SSD1306 |
|-----------|-------------|
| GPIO21 (SDA) | SDA |
| GPIO22 (SCL) | SCL |
| 3.3V | VCC |
| GND | GND |

## Quick Start

### 1. Flash MicroPython

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20260406-v1.28.0.bin
```

### 2. Upload firmware

```bash
python3 upload.py
```

### 3. Configure `.env`

Create `/firmware/.env` on the ESP32 filesystem (see `firmware/.env.example`):

```
WIFI_SSID=YourSSID
WIFI_PASSWORD=YourPassword
OLLAMA_MODEL=gemma3:4b
PROXY_HOST=192.168.1.x
PROXY_PORT=9090
```

Do **not** put `OLLAMA_API_KEY` on the device. The key belongs only on the host machine running `proxy.py`; the ESP32 and the browser never receive it. `PROXY_HOST` and `PROXY_PORT` are injected into the UI automatically when the device serves the page (the `__PROXY_URL__` placeholder in `firmware/lib/ui.py` is replaced at serve time), so set them here only.

### 4. Start the proxy on the host machine

```bash
cd esp-ai
OLLAMA_API_KEY="ollama_..." \
ALLOWED_ORIGINS="http://192.168.1.x" \
RATE_LIMIT_PER_MIN=20 \
OLLAMA_MODEL="gemma3:4b" python3 proxy.py
```

- `OLLAMA_API_KEY` (required) — the Ollama API key, read only by `proxy.py` on the host.
- `ALLOWED_ORIGINS` — comma-separated list of browser origins allowed to call the proxy, e.g. the ESP32 UI address `http://192.168.1.x`. Use the exact scheme, host and port the browser shows. Requests with a missing or unlisted `Origin` are rejected with HTTP 403, and only allowed origins are echoed in CORS headers.
- `RATE_LIMIT_PER_MIN` (optional, default `20`) — maximum chat requests per client IP per minute; excess requests get HTTP 429. Messages over 4000 characters are rejected with HTTP 413.

The proxy runs on port 9090, forwarding chat requests to `ollama.com/v1`.

### 5. Open the UI

Navigate to `http://esp32-ip/` in a browser. Select a skill from the sidebar and start chatting.

## Project Structure

```
esp-ai/
├── firmware/               # ESP32 MicroPython source
│   ├── boot.py             # Boot entry
│   ├── main.py             # Server startup
│   ├── lib/
│   │   ├── server.py       # HTTP server, routing
│   │   ├── ui.py           # HTML/CSS/JS UI
│   │   ├── ollama_client.py# Proxy HTTP client
│   │   ├── skills.py       # Skill definitions
│   │   ├── ssd1306.py      # OLED driver
│   │   └── display.py      # OLED display manager
│   └── .env.example        # Environment config template
├── proxy.py                 # Host-side proxy bridge
├── upload.py                # Firmware upload script
├── connections/
│   └── wiring.md            # Hardware wiring guide
├── docs/
│   ├── architecture.md      # System architecture
│   ├── techstack.md         # Technology choices
│   └── api.md               # HTTP API reference
├── assets/
│   ├── images/              # Photos, screenshots, diagrams
│   └── cad/                 # 3D enclosure files (.f3d, .stl)
├── .gitignore
└── README.md
```

## Why This Architecture

The ESP32 cannot make outbound HTTPS connections (mbedTLS error `-202`). The local proxy bridge converts the browser's HTTP requests to HTTPS and forwards them to Ollama Cloud. Additionally, some WiFi networks use **AP isolation**, blocking peer-to-peer LAN traffic — this is why the chat requests go **browser → proxy** rather than **ESP32 → proxy**.

See [docs/techstack.md](docs/techstack.md) for detailed rationale.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Chat UI (HTML) |
| GET | `/api/info` | Server info (model, IP, active skill) |
| GET | `/api/skills` | List all skills with prompts |
| POST | `/api/skills/activate` | Switch active skill |
| POST | `/api/display` | Push chat content to OLED |
| GET | `/favicon.ico` | SVG favicon |

## License

MIT
