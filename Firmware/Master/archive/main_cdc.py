import time
import usb.device
from usb.device.cdc import CDCInterface


class NativeUSB_UART:
    def __init__(self):
        # timeout=0 für non-blocking I/O
        self.cdc = CDCInterface(timeout=0)

        # Native USB exklusiv nutzen
        usb.device.get().init(self.cdc, builtin_driver=False)

    def wait_for_host(self, timeout_ms=None):
        """Wartet, bis das USB-Kabel am PC erkannt und konfiguriert wurde."""
        start = time.ticks_ms()
        while not self.cdc.is_open():
            if timeout_ms and time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                return False
            time.sleep_ms(50)
        return True

    def is_active(self) -> bool:
        """Prüft, ob ein Terminal/Host-Programm den USB-CDC Port geöffnet hat."""
        return self.cdc.is_open() and self.cdc.dtr

    def any(self) -> int:
        """Gibt die Anzahl der verfügbaren Bytes im Empfangspuffer zurück."""
        if not self.cdc.is_open():
            return 0

        rb = getattr(self.cdc, '_rb', None)
        if rb is not None:
            # Versuche .any() auf dem Buffer-Objekt
            if hasattr(rb, 'any'):
                return rb.any()
            # Versuche .available() auf dem Buffer-Objekt
            if hasattr(rb, 'available'):
                return rb.available()

        # Fallback über ioctl(4, 0) [MP_STREAM_POLL_RD]
        try:
            return 1 if (self.cdc.ioctl(4, 0) & 4) else 0
        except Exception:
            return 0

    def read(self, size: int = -1) -> bytes:
        """Liest verfuegbare Bytes vom CDC-Port (non-blocking)."""
        if not self.cdc.is_open():
            return b""

        data = self.cdc.read(size) if size else self.cdc.read()
        return data if data is not None else b""

    def readline(self) -> bytes:
        """Liest eine komplette Zeile bis '\n' aus."""
        line = bytearray()
        while True:
            char = self.read(1)
            if not char:
                break
            line.extend(char)
            if char == b'\n':
                break
        return bytes(line)

    def write(self, data: bytes | str) -> int:
        """Sendet Daten an den PC über den nativen USB-CDC-Port."""
        if not self.cdc.is_open():
            return 0
        if isinstance(data, str):
            data = data.encode('utf-8')

        res = self.cdc.write(data)
        return res if res is not None else len(data)
# =====================================================================
# Beispiel zur Nutzung
# =====================================================================

# 'print'-Ausgaben landen auf deiner UART-REPL!
print("[UART REPL] Starte nativen USB-CDC Treiber...")

cdc_uart = NativeUSB_UART()

print("[UART REPL] Warte auf Verbindungsaufbau des nativen USB-Ports...")
cdc_uart.wait_for_host()

print("[UART REPL] Nativity USB CDC ist bereit!")

while True:
    # Optional: Nur verarbeiten, wenn am PC ein Terminal/Anwendung geöffnet ist (DTR active)
    if cdc_uart.is_active():
        # Auf eingehende Daten am nativen USB-Port prüfen
        rx_bytes = cdc_uart.read()
        if rx_bytes:
            #rx_bytes = cdc_uart.readline()
            # Log auf der UART-REPL ausgeben
            print(f"[UART REPL Log] Über nativen USB empfangen: {rx_bytes}")

            # Daten/Antwort über nativen USB zurücksenden
            cdc_uart.write(b"USB-CDC OK: " + rx_bytes)


    time.sleep_ms(10)