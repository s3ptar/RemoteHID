import sys
import select
import time

# Poller initialisieren, um auf Daten von sys.stdin (Native USB) zu warten
poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

print("Starte getrennte Kommunikation...")

while True:
    # Prüfen, ob Daten über Native USB ankommen (Timeout 10ms)
    events = poller.poll(10)
    if events:
        # Datenzeile über Native USB einlesen
        line = sys.stdin.readline()

        # Antwort nur über Native USB zurücksenden
        sys.stdout.write(f"ACK: {line}")

    time.sleep(0.05)
