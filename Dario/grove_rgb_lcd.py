import time

class RgbLcd:
    def __init__(self, i2c, addr=0x3E, addr_rgb=0x62):
        self.i2c = i2c
        self.addr = addr
        self.addr_rgb = addr_rgb
        self._init()
    
    def _init(self):
        time.sleep(0.1)
        # LCD initialisieren
        self.i2c.writeto(self.addr, bytes([0x80, 0x38]))  # 8-bit, 2 Zeilen
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x39]))  # Instruction table select
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x04]))  # Bias setting
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x14]))  # Power control
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x56]))  # Follower control
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x6D]))  # Contrast
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x38]))  # Normal instruction set
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x0C]))  # Display on
        time.sleep(0.01)
        self.i2c.writeto(self.addr, bytes([0x80, 0x01]))  # Clear display
        time.sleep(0.05)
        # RGB initialisieren
        self.set_rgb(255, 255, 255)
    
    def clear(self):
        self.i2c.writeto(self.addr, bytes([0x80, 0x01]))
        time.sleep(0.05)
    
    def set_cursor(self, col, row):
        if row == 0:
            addr = 0x80 + col
        else:
            addr = 0xC0 + col
        self.i2c.writeto(self.addr, bytes([0x80, addr]))
    
    def write(self, text):
        for char in text:
            self.i2c.writeto(self.addr, bytes([0x40, ord(char)]))
            time.sleep(0.001)
    
    def set_rgb(self, r, g, b):
        self.i2c.writeto(self.addr_rgb, bytes([0x00, 0x00, 0x00]))
        time.sleep(0.001)
        self.i2c.writeto(self.addr_rgb, bytes([0x01, r, g, b]))
        time.sleep(0.001)
