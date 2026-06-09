# Architecture

## System Overview

```
┌──────────────────────────────────────────────────────┐
│                    Host Machine                       │
│  ┌──────────────┐         ┌──────────────────────┐   │
│  │   Browser    │  POST   │   Proxy (:9090)      │   │
│  │  (Tailwind,  │────────→│   urllib HTTPS       │───┼──→ Ollama Cloud
│  │   Serif UI)  │         │   → ollama.com/v1    │   │    (gemma3:4b)
│  │              │←────────│                      │   │
│  │              │  JSON   └──────────────────────┘   │
│  │              │                                     │
│  └──────┬───────┘                                     │
│         │ GET /, /api/*                                │
│         ▼                                             │
│  ┌──────────────────────────────────────────────┐    │
│  │           ESP32 (192.168.1.127:80)           │    │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │    │
│  │  │ HTTP    │  │ Skills   │  │ OLED        │ │    │
│  │  │ Server  │  │ System   │  │ Display     │ │    │
│  │  └─────────┘  └──────────┘  └─────────────┘ │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

## Data Flow

### Chat Flow (Browser → Proxy → Ollama)

1. **User types message** in the browser UI
2. **JavaScript** constructs a JSON payload `{message, system_prompt}` using the active skill's prompt
3. **POST** sent directly to the proxy at `http://host-ip:9090`
4. **Proxy** wraps the request in HTTPS and forwards to `https://ollama.com/v1/chat/completions`
5. **Ollama Cloud** returns the AI response
6. **Proxy** extracts `choices[0].message.content` and returns `{response: "..."}`
7. **Browser** displays the response in the chat UI
8. **Browser also POSTs** `{user, ai}` to the ESP32's `/api/display` endpoint
9. **ESP32** scrolls the conversation onto the OLED display

### Why Not ESP32 → Proxy?

Two blocking issues:

| Issue | Symptom | Solution |
|-------|---------|----------|
| mbedTLS error -202 | ESP32 `ssl.wrap_socket()` fails on any HTTPS connection | Proxy handles HTTPS; ESP32 only does HTTP |
| AP Isolation | ESP32 connects to internet but cannot reach LAN peers (ETIMEDOUT) | Browser (on LAN) talks to proxy directly; ESP32 only serves UI |

## Component Design

### ESP32 HTTP Server (`server.py`)
- Single-threaded, synchronous `while True: accept()`
- Parses raw HTTP/1.1 requests manually (no framework)
- Routes: `/`, `/api/chat`, `/api/skills`, `/api/skills/activate`, `/api/info`, `/api/display`, `/favicon.ico`
- CORS headers on all responses

### Proxy (`proxy.py`)
- Python `http.server.HTTPServer` on port 9090
- `http.client.HTTPSConnection` for Ollama cloud requests
- Environment-configured: API key, model, base URL
- 30-second timeout for Ollama responses

### OLED Display (`display.py`)
- SSD1306 128×64 I2C via `framebuf`
- Terminal-style scrolling: `scroll(0, -8)` then write new line at bottom
- States: splash → connecting → status (IP/model) → live chat scroll
- Graceful fallback if no OLED detected

### UI (`ui.py`)
- Single-file HTML/CSS/JS (~14KB) embedded as a Python string
- Tailwind CSS + Google Fonts + Material Symbols loaded from CDN
- All chat state is client-side (no message history on ESP32)
- Skills fetched from ESP32 API on page load
