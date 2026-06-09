# Technology Choices

## Microcontroller: ESP32

**Why ESP32 over alternatives?**

| Factor | ESP32 | Raspberry Pi Pico W | Arduino Uno R4 WiFi |
|--------|-------|--------------------|--------------------|
| WiFi | Dual-mode BLE+WiFi | 2.4GHz WiFi only | Uno WiFi (ESP32-based) |
| Dual core | 240MHz Xtensa | 133MHz Cortex-M0+ | 48MHz Renesas |
| SRAM | 520KB | 264KB | 32KB |
| Flash | 4MB (external) | 2MB | 256KB |
| I2C | Yes (2 interfaces) | Yes (2) | Yes (1) |
| MicroPython | Excellent support | Official support | Unofficial only |
| Price | ~$3-5 | ~$4 | ~$20 |

The ESP32 was chosen for its mature MicroPython support, dual WiFi+Bluetooth, and ample RAM for running an HTTP server alongside display management.

## Firmware: MicroPython

**Why MicroPython over C/Arduino or ESP-IDF?**

| Factor | MicroPython | C/Arduino | ESP-IDF |
|--------|------------|-----------|---------|
| Dev speed | Hours | Days | Weeks |
| Iteration | Upload single files | Full recompile+flash | Full rebuild |
| String handling | Native | Manual buffers | Manual buffers |
| RAM usage | ~100KB baseline | ~30KB | ~50KB |
| HTTP parsing | Manual (no framework) | Libraries available | Libraries available |

The rapid development cycle of MicroPython was the deciding factor. For a project that evolved through multiple architecture changes (direct Ollama → SSL error → proxy → AP isolation → OLED integration), being able to edit and upload individual `.py` files in seconds was critical.

**Trade-off:** MicroPython uses ~100KB of the 520KB SRAM for the runtime. The `framebuf` for the OLED adds ~1KB. The server uses ~30-50KB for buffers and connections. Total usage ~200KB, well within limits.

## AI Model: Ollama Cloud (gemma3:4b)

**Why cloud instead of local?**

1. **ESP32 cannot run LLMs** — needs at least 4GB+ VRAM, impossible on microcontroller
2. **No GPU on host** — the development machine has no CUDA/ROCm-capable GPU
3. **gemma3:4b** — small, fast, free-tier available via Ollama Cloud. Originally requested `llama3.2` was not available on Ollama's cloud offering.

## Proxy Bridge

**Why a local proxy?**

The ESP32's MicroPython `ssl` module consistently fails with `OSError: -202` (mbedTLS handshake error) on any outbound HTTPS connection. This is a known issue with certain ESP32 revisions and MicroPython's mbedTLS configuration. The proxy:

1. Receives plain HTTP from the ESP32 (or browser)
2. Makes HTTPS connection to Ollama Cloud via Python's `http.client.HTTPSConnection`
3. Returns the response as plain HTTP

## UI: Tailwind CSS + Google Fonts + Material Symbols

**Why CDN-loaded resources?**

| Resource | Purpose | Why |
|----------|---------|-----|
| Tailwind CSS | Utility-first layout | Eliminates custom CSS for 95% of styling |
| Inter | UI typography | Clean sans-serif for labels, buttons, metadata |
| Source Serif 4 | Message body | Designed for digital legibility in long-form reading |
| Material Symbols | Icons | Consistent, scalable, variable-weight icons |

Since the ESP32 cannot render HTML, all UI resources are loaded by the browser from CDN. The ESP32 only serves the raw HTML string. This keeps the firmware small (~14KB for the UI) while enabling a rich interface.

## OLED: SSD1306 128×64 I2C

**Why this display?**

- **Most common OLED** for ESP32 projects — widely available, cheap (~$3)
- **I2C interface** — uses only 2 pins (SDA/SCL), leaves GPIO free
- **128×64 resolution** — fits ~8 lines of 16 characters each, enough for scrolling chat
- **framebuf buffer** — only 1KB of RAM needed
- **Address 0x3C** — hardware default, no address jumpers needed

## File System: Embedded Python Modules

All firmware is flat `.py` files on the ESP32's SPIFFS filesystem, uploaded via serial raw REPL. No filesystem compression, no frozen bytecode — simplicity over performance for a project this size.
