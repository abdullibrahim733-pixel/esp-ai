# HTTP API Reference

All endpoints serve from the ESP32 at `http://esp32-ip/`. Chat requests go directly to the proxy.

---

## `GET /`

Returns the chat UI as an HTML page.

**Response:** `text/html`, ~14KB of HTML with embedded CSS and JavaScript.

---

## `GET /api/info`

Returns server configuration and status.

**Response:**
```json
{
  "ip": "192.168.1.127",
  "model": "gemma3:4b",
  "skill": "general"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ip` | string | ESP32's WiFi IP address |
| `model` | string | Ollama model name |
| `skill` | string | Currently active skill ID |

---

## `GET /api/skills`

Returns all available skills with their prompts.

**Response:**
```json
{
  "skills": [
    {
      "id": "general",
      "name": "General",
      "desc": "Open-ended conversation",
      "icon": "💬",
      "prompt": "You are a helpful, concise AI assistant..."
    },
    {
      "id": "code",
      "name": "Code Expert",
      "desc": "Write & explain code",
      "icon": "&lt;/&gt;",
      "prompt": "You are a senior software engineer..."
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Skill identifier |
| `name` | string | Display name |
| `desc` | string | Short description |
| `icon` | string | HTML-safe icon character |
| `prompt` | string | System prompt sent to AI |

---

## `POST /api/skills/activate`

Switch the active skill.

**Request:**
```json
{
  "skill": "code"
}
```

**Response:**
```json
{
  "ok": true,
  "skill": "code"
}
```

Returns `400` if the skill ID is unknown.

---

## `POST /api/display`

Push a chat exchange to the OLED display.

**Request:**
```json
{
  "user": "what is quantum computing",
  "ai": "Quantum computing uses qubits..."
}
```

**Response:**
```json
{
  "ok": true
}
```

Gracefully ignored if no OLED is connected.

---

## `GET /favicon.ico`

Returns the SVG favicon.

**Response:** `image/svg+xml`, 169-byte SVG of a dark square with a sage-green triangle.

---

## Proxy Endpoint (not on ESP32)

### `POST http://host-ip:9090/`

Send a chat message to the AI.

**Request:**
```json
{
  "message": "hello",
  "system_prompt": "You are a helpful assistant."
}
```

**Response:**
```json
{
  "response": "Hi there! How can I help you today?"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | User's message |
| `system_prompt` | string | System prompt defining AI behavior |

Returns `500` on network errors or Ollama API failures.
