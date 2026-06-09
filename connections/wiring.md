# Wiring Guide

## ESP32 ↔ SSD1306 OLED (128×64 I2C)

```
ESP32 Dev Board              SSD1306 OLED Module
┌──────────────┐            ┌──────────────────┐
│              │            │                  │
│ GPIO21 (SDA) │────────────│ SDA              │
│              │            │                  │
│ GPIO22 (SCL) │────────────│ SCL              │
│              │            │                  │
│ 3.3V         │────────────│ VCC              │
│              │            │                  │
│ GND          │────────────│ GND              │
│              │            │                  │
│ GPIO0 (Boot) │ (optional)│ (not connected)  │
│ EN           │ (optional)│ (not connected)  │
└──────────────┘            └──────────────────┘
```

### I2C Details

| Parameter | Value |
|-----------|-------|
| Interface | I2C (not SPI) |
| Address | `0x3C` |
| Frequency | 400kHz (fast mode) |
| Pull-ups | 4.7kΩ (usually on module) |

### Pin Notes

- **GPIO21 / GPIO22** are the ESP32's default I2C peripheral pins. No configuration needed.
- **VCC** can be 3.3V or 5V depending on module. Most SSD1306 modules have an onboard regulator accepting 3.3–5V. Check your module's datasheet.
- **GND** must be common between ESP32 and OLED.

### If the OLED is Not Detected

1. Verify I2C address: run `i2c.scan()` from MicroPython REPL
2. Check wiring (swap SDA/SCL is the most common mistake)
3. Some modules use address `0x3D` instead of `0x3C` — change `OLED_ADDR` in `lib/display.py`
4. Ensure pull-up resistors are present (most breakout boards include them)

---

## Power

```
USB Power Bank / Wall Adapter
┌─────────────────────┐
│                     │
│ USB-A               │
│ 5V / 1A+            │
└─────────┬───────────┘
          │
          │ USB cable
          ▼
    ┌──────────┐
    │ ESP32    │
    │ USB port │
    └──────────┘
          │
          │ 3.3V out
          ▼
    ┌──────────┐
    │ OLED     │
    │ VCC pin  │
    └──────────┘
```

- ESP32 draws ~80mA (WiFi active) + ~20mA (OLED) = ~100mA total
- A standard USB power bank or phone charger works fine
- Do NOT power the OLED from the ESP32's 3.3V pin if drawing >200mA total peripherals

---

## Pinout Reference (ESP32 DevKit V1)

```
         ┌──────────────────────┐
         │ USB                  │
         │                      │
 EN  ────│ 1  EN             D23│──── GPIO23
 VP  ────│ 2  VP  (ADC)     D22│──── GPIO22 (OLED SCL)
 VN  ────│ 3  VN  (ADC)     TX0│──── GPIO1
 D34 ────│ 4  D34            RX0│──── GPIO3
 D35 ────│ 5  D35            D21│──── GPIO21 (OLED SDA)
 D32 ────│ 6  D32            GND│──── GND
 D33 ────│ 7  D33            D19│──── GPIO19
 D25 ────│ 8  D25            D18│──── GPIO18
 D26 ────│ 9  D26            D5 │──── GPIO5
 D27 ────│ 10 D27           D17│──── GPIO17
 D14 ────│ 11 D14           D16│──── GPIO16
 D12 ────│ 12 D12            D4 │──── GPIO4
 GND ────│ 13 GND            D0 │──── GPIO0
 VIN ────│ 14 VIN (5V)      D2 │──── GPIO2
         │ 15 RST           D15│──── GPIO15
         │ 16                      │
         └──────────────────────┘
```
