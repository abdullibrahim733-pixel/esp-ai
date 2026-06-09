import machine
import time

OLED_SDA = 21
OLED_SCL = 22
OLED_ADDR = 0x3C
OLED_W = 128
OLED_H = 64


class Display:
    def __init__(self):
        self.oled = None
        try:
            i2c = machine.I2C(0, sda=machine.Pin(OLED_SDA), scl=machine.Pin(OLED_SCL), freq=400000)
            if OLED_ADDR in i2c.scan():
                from ssd1306 import SSD1306
                self.oled = SSD1306(OLED_W, OLED_H, i2c, addr=OLED_ADDR)
                print("OLED initialized")
            else:
                print("OLED not found at addr", hex(OLED_ADDR))
        except Exception as e:
            print("OLED init skipped:", e)

    def _col(self, c):
        return 1 if c else 0

    def line(self, text, col=1):
        if not self.oled:
            return
        self.oled.scroll(0, -8)
        self.oled.fill_rect(0, self.oled.height - 8, self.oled.width, 8, 0)
        self.oled.text(text[:16], 0, self.oled.height - 8, self._col(col))
        self.oled.show()

    def lines(self, texts, col=1):
        for t in texts:
            self.line(t, col)
            time.sleep(0.15)

    def splash(self):
        if not self.oled:
            return
        self.oled.clear()
        self.oled.text("ESP32 Chat", 16, 16, 1)
        self.oled.text("Starting...", 16, 32, 1)
        self.oled.show()
        time.sleep(1)
        self.oled.clear()
        self.oled.show()

    def status(self, ip, model):
        if not self.oled:
            return
        self.oled.clear()
        self.oled.text("IP: " + ip, 0, 0, 1)
        self.oled.text(model[:14], 0, 12, 1)
        self.oled.text("Ready", 0, 28, 1)
        self.oled.hline(0, 40, 128, 1)
        self.oled.show()

    def show_chat(self, user_msg, ai_msg):
        if not self.oled:
            return
        self.lines(["> " + user_msg[:14]], 1)
        time.sleep(0.2)
        lines = []
        remaining = ai_msg[:60]
        while remaining:
            lines.append("< " + remaining[:14])
            remaining = remaining[14:]
        self.lines(lines, 1)

    def busy(self, label="Thinking..."):
        if not self.oled:
            return
        self.line(label, 1)
