import framebuf
import time


SET_CONTRAST = 0x81
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_MEM_ADDR = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


class SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = height // 8
        self.buffer = bytearray(width * self.pages)
        self.fb = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x00, cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b"\x40" + buf)

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,
            SET_MEM_ADDR, 0x00,
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08,
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0xF1,
            SET_VCOM_DESEL, 0x30,
            SET_CONTRAST, 0xFF,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_CHARGE_PUMP, 0x14,
            SET_DISP | 0x01,
        ):
            self.write_cmd(cmd)
        self.clear()

    def clear(self):
        self.fb.fill(0)
        self.show()

    def show(self):
        for i in range(self.pages):
            self.write_data(self.buffer[i * self.width : (i + 1) * self.width])

    def contrast(self, val):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(val)

    def invert(self, inv):
        self.write_cmd(SET_NORM_INV | (inv & 1))

    def power(self, on):
        self.write_cmd(SET_DISP | (1 if on else 0))

    def hline(self, x, y, w, c):
        self.fb.hline(x, y, w, c)

    def vline(self, x, y, h, c):
        self.fb.vline(x, y, h, c)

    def rect(self, x, y, w, h, c):
        self.fb.rect(x, y, w, h, c)

    def fill_rect(self, x, y, w, h, c):
        self.fb.fill_rect(x, y, w, h, c)

    def text(self, s, x, y, c=1):
        self.fb.text(s, x, y, c)

    def scroll(self, dx, dy):
        self.fb.scroll(dx, dy)

    def pixel(self, x, y, c):
        self.fb.pixel(x, y, c)
