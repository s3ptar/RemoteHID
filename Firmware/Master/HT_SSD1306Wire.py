import machine
import gc

# Konstanten (entsprechend dem Arduino-Code)
DISPLAYOFF = 0xAE
SETDISPLAYCLOCKDIV = 0xD5
SETMULTIPLEX = 0xA8
SETDISPLAYOFFSET = 0xD3
SETSTARTLINE = 0x40
CHARGEPUMP = 0x8D
MEMORYMODE = 0x20
SEGREMAP = 0xA0
COMSCANDEC = 0xC8
SETCOMPINS = 0x12
SETCONTRAST = 0x81
SETPRECHARGE = 0xD9
SETVCOMDETECT = 0xDB
DISPLAYALLON_RESUME = 0xA4
NORMALDISPLAY = 0xA6
DISPLAYON = 0xAF
COLUMNADDR = 0x21
PAGEADDR = 0x22

# Geometrie & Rotation
GEOMETRY_128_64 = 0
GEOMETRY_128_32 = 1
GEOMETRY_RAWMODE = 2

ANGLE_0_DEGREE = 0
ANGLE_90_DEGREE = 1
ANGLE_180_DEGREE = 2
ANGLE_270_DEGREE = 3

# Flag für WIRELESS_STICK_V3 (falls +32 Offset gebraucht wird)
WIRELESS_STICK_V3 = False


class SSD1306Wire:
    def __init__(self, address, freq, sda, scl, geometry=GEOMETRY_128_64, rst=-1):
        self._address = address
        self._freq = freq
        self._sda = sda
        self._scl = scl
        self._rst = rst
        self._do_i2c_auto_init = False

        self.geometry = geometry
        self.rotate_angle = ANGLE_0_DEGREE

        # Geometrie setzen
        if geometry == GEOMETRY_128_32:
            self._width = 128
            self._height = 32
        else:
            self._width = 128
            self._height = 64

        self.display_buffer_size = (self._width * self._height) // 8
        self.buffer = bytearray(self.display_buffer_size)
        self.buffer_back = bytearray(self.display_buffer_size)

        self.i2c = None
        self.connect()

    def connect(self):
        # In MicroPython nutzen wir standardmäßig die Hardware- oder Software-I2C-Klasse
        # I2C ID 0 wird hier als Default genutzt, ggf. anpassen oder machine.I2C(sda=..., scl=...) nutzen
        try:
            self.i2c = machine.I2C(0, sda=machine.Pin(self._sda), scl=machine.Pin(self._scl), freq=self._freq)
        except ValueError:
            self.i2c = machine.SoftI2C(sda=machine.Pin(self._sda), scl=machine.Pin(self._scl), freq=self._freq)
        return True

    def width(self):
        return self._width

    def height(self):
        return self._height

    def set_i2c_auto_init(self, do_i2c_auto_init):
        self._do_i2c_auto_init = do_i2c_auto_init

    def init_i2c_if_necessary(self):
        if self._do_i2c_auto_init:
            self.connect()

    def send_command(self, command):
        self.init_i2c_if_necessary()
        # Arduino: Wire.write(0x00) oder 0x80 für Kommandos. Dein Code nutzt 0x80 (Single Command)
        self.i2c.writeto(self._address, bytes([0x80, command]))

    def stop(self):
        # MicroPython I2C Objekte haben kein direktes .end(), wir deinitialisieren falls möglich
        if hasattr(self.i2c, 'deinit'):
            self.i2c.deinit()

    def display(self):
        self.init_i2c_if_necessary()

        if self.rotate_angle in (ANGLE_0_DEGREE, ANANGLE_180_DEGREE):
            # --- DOPPELPUFFER LOGIK (0 / 180 Grad) ---
            min_bound_y = 255
            max_bound_y = 0
            min_bound_x = 255
            max_bound_x = 0

            w = self.width()
            pages = self.height() // 8

            for y in range(pages):
                for x in range(w):
                    pos = x + y * w
                    if self.buffer[pos] != self.buffer_back[pos]:
                        if y < min_bound_y: min_bound_y = y
                        if y > max_bound_y: max_bound_y = y
                        if x < min_bound_x: min_bound_x = x
                        if x > max_bound_x: max_bound_x = x
                    self.buffer_back[pos] = self.buffer[pos]

            if min_bound_y == 255:
                return  # Keine Änderungen

            # Spalten- und Seitenadresse setzen
            if WIRELESS_STICK_V3:
                self.send_command(COLUMNADDR)
                self.send_command(min_bound_x + 32)
                self.send_command(max_bound_x + 32)
            else:
                self.send_command(COLUMNADDR)
                self.send_command(min_bound_x)
                self.send_command(max_bound_x)

            self.send_command(PAGEADDR)
            self.send_command(min_bound_y)
            self.send_command(max_bound_y)

            # Daten chunkweise senden (16 Byte Blöcke wie im Arduino-Code)
            # MicroPython optimiert: Wir bauen ein Paket mit dem Co-Byte (0x40) vornedran
            for y in range(min_bound_y, max_bound_y + 1):
                row_start = y * w
                x = min_bound_x
                while x <= max_bound_x:
                    chunk_size = min(16, max_bound_x - x + 1)
                    data_packet = bytearray([0x40])
                    data_packet.extend(self.buffer[row_start + x: row_start + x + chunk_size])
                    self.i2c.writeto(self._address, data_packet)
                    x += chunk_size

        else:
            # --- ROTATIONS-LOGIK (90 / 270 Grad) ---
            buffer_rotate = bytearray(self.display_buffer_size)
            w = self.width()
            h = self.height()

            for i in range(w):
                for j in range(h):
                    temp = (self.buffer[(j >> 3) * w + i] >> (j & 7)) & 0x01
                    buffer_rotate[(i >> 3) * h + j] |= (temp << (i & 7))

            # Doppelpuffer für rotierte Daten
            min_bound_y = 255
            max_bound_y = 0
            min_bound_x = 255
            max_bound_x = 0

            pages_rot = w // 8
            for y in range(pages_rot):
                for x in range(h):
                    pos = x + y * h
                    if buffer_rotate[pos] != self.buffer_back[pos]:
                        if y < min_bound_y: min_bound_y = y
                        if y > max_bound_y: max_bound_y = y
                        if x < min_bound_x: min_bound_x = x
                        if x > max_bound_x: max_bound_x = x
                    self.buffer_back[pos] = buffer_rotate[pos]

            if min_bound_y == 255:
                return

            if WIRELESS_STICK_V3:
                self.send_command(COLUMNADDR)
                self.send_command(min_bound_x + 32)
                self.send_command(max_bound_x + 32)
            else:
                self.send_command(COLUMNADDR)
                self.send_command(min_bound_x)
                self.send_command(max_bound_x)

            self.send_command(PAGEADDR)
            self.send_command(min_bound_y)
            self.send_command(max_bound_y)

            for y in range(min_bound_y, max_bound_y + 1):
                row_start = y * h
                x = min_bound_x
                while x <= max_bound_x:
                    chunk_size = min(16, max_bound_x - x + 1)
                    data_packet = bytearray([0x40])
                    data_packet.extend(buffer_rotate[row_start + x: row_start + x + chunk_size])
                    self.i2c.writeto(self._address, data_packet)
                    x += chunk_size

    def send_init_commands(self):
        if self.geometry == GEOMETRY_RAWMODE:
            return

        self.send_command(DISPLAYOFF)
        self.send_command(SETDISPLAYCLOCKDIV)
        self.send_command(0xF0)
        self.send_command(SETMULTIPLEX)
        self.send_command(self.height() - 1)
        self.send_command(SETDISPLAYOFFSET)
        self.send_command(0x00)
        self.send_command(SETSTARTLINE)
        self.send_command(CHARGEPUMP)
        self.send_command(0x14)
        self.send_command(MEMORYMODE)
        self.send_command(0x00)
        self.send_command(SEGREMAP | 0x01)
        self.send_command(COMSCANDEC)
        self.send_command(SETCOMPINS)
        self.send_command(0x12)
        self.send_command(SETCONTRAST)
        self.send_command(0xCF)
        self.send_command(SETPRECHARGE)
        self.send_command(0xF1)
        self.send_command(SETVCOMDETECT)
        self.send_command(0x40)
        self.send_command(DISPLAYALLON_RESUME)
        self.send_command(NORMALDISPLAY)
        self.send_command(0x2E)  # stop scroll
        self.send_command(DISPLAYON)

    def send_screen_rotate_command(self):
        if self.rotate_angle == ANGLE_0_DEGREE:
            self.send_command(SEGREMAP | 0x01)
            self.send_command(0xC8)
        elif self.rotate_angle == ANGLE_90_DEGREE:
            self.send_command(SEGREMAP)
            self.send_command(0xC8)
        elif self.rotate_angle == ANGLE_180_DEGREE:
            self.send_command(SEGREMAP)
            self.send_command(0xC0)
        elif self.rotate_angle == ANGLE_270_DEGREE:
            self.send_command(SEGREMAP | 0x01)
            self.send_command(0xC0)