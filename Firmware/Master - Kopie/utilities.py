"""#####################################################################
#! @ file:                   webservices.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ version:                0
#  @ history:                -
#  @ brief:                  Hilfsfunktionen für die LED_ClockRing, erstellt mit Hilfe von Gemini,
#                             einem KI-Tool von OpenAI, um die Entwicklung zu beschleunigen.
#####################################################################"""


"""#####################################################################
# Includes
#####################################################################"""
import logging
import esp
import gc
import machine
import os
import time
import network
import json
# Falls der ESP32 den internen Temperatursensor unterstützt
try:
    import esp32
except ImportError:
    esp32 = None
"""#####################################################################
# Informations
#####################################################################"""

"""#####################################################################
# Declarations
#####################################################################"""

"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Global Variable
#####################################################################"""

"""#####################################################################
# local Variable
#####################################################################"""
logger = logging.getLogger(__name__)
"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Local Funtions
#####################################################################"""

"""#####################################################################
#! @fn           get_device_telemetry() -> dict
#  @ brief       read device telemetry data
#  @ param       none
#  @ exception   none
#  @ return      dict device data
#####################################################################"""
def get_device_telemetry() -> dict:

    telemetry_dict = {}

    #get filesystem information
    # os.statvfs gibt Informationen über das Dateisystem zurück
    # '/' steht für das Hauptverzeichnis
    fs_info = os.statvfs('/')
    # Blockgröße in Bytes
    block_size = fs_info[0]
    # Gesamtzahl der Blöcke
    total_blocks = fs_info[2]
    # Freie Blöcke
    free_blocks = fs_info[3]
    # Berechnung in Bytes und Kilobytes
    total_flash = block_size * total_blocks
    free_flash = block_size * free_blocks
    used_flash = total_flash - free_flash
    telemetry_dict["Filesystem"] = {"pyh Flash": f"{esp.flash_size() / (1024 * 1000):.0f} MB",
                                    "total_flash":f"{total_flash} kB",
                                    "free_flash": f"{free_flash} kB",
                                    "used_flash": f"{used_flash} kB",
                                    "Auslastung": f"{(used_flash / total_flash) * 100:.1f}%"
                                    }

    #logger.debug(f"Physische Flash-Größe: {esp.flash_size() / (1024 * 1000):.0f} MB")
    #logger.debug(f"Freier Flash:     {free_flash / 1024:.2f} KB")
    #logger.debug(f"Belegter Flash:   {used_flash / 1024:.2f} KB")
    #logger.debug(f"Gesamt-Größe:     {total_flash / 1024:.2f} KB")
    #logger.debug(f"Auslastung:       {(used_flash / total_flash) * 100:.1f}%")

    # Holt die aktuellen Speicherwerte (in Bytes)
    free_ram = gc.mem_free()
    allocated_ram = gc.mem_alloc()
    total_ram = free_ram + allocated_ram
    #logger.debug(f"Freier RAM:     {free_ram / 1024:.2f} KB")
    #logger.debug(f"Belegter RAM:   {allocated_ram / 1024:.2f} KB")
    #logger.debug(f"Gesamt verfügbar: {total_ram / 1024:.2f} KB")
    #logger.debug(f"Auslastung:     {(allocated_ram / total_ram) * 100:.1f}%")
    telemetry_dict["RAM"] = { "free": f"{free_ram / 1024:.2f} KB",
                              "allocated": f"{allocated_ram / 1024:.2f} KB",
                              "total": f"{total_ram / 1024:.2f} KB",
                              "Auslastung": f"{(allocated_ram / total_ram) * 100:.1f}%"
                              }

    if gc.isenabled():
        #logger.debug(f"Garbage Collector disable, is now enabled.")
        telemetry_dict["GarbageCollector"] = {"enabled" : True}
    else:
        #logger.debug(f"Garbage Collector enable")
        telemetry_dict["GarbageCollector"] = {"enabled": False}

    # Holt die aktuelle CPU-Frequenz in Hertz
    cpu_freq_hz = machine.freq()
    telemetry_dict["CPU"] = {"Frequenz": f"{cpu_freq_hz / 1000000:.0f} MHz"}
    telemetry_dict["Device"] = {"Type": "ESP32-Generic"}

    try:
        # Liefert die Temperatur in Fahrenheit oder Celsius (je nach Chip/Firmware)
        # Meistens wird die Temperatur in Grad Celsius zurückgegeben
        temp_c = (esp32.raw_temperature() - 32) * 5 / 9
        # Falls deine Firmware Fahrenheit liefert, umrechnen: (temp_f - 32) * 5/9
        #logger.debug(f"Interne Chip-Temperatur: {temp_c:.1f} °C")
        telemetry_dict["Temperatur"] = {"internal": f"{temp_c:.1f}"}
    except AttributeError:
        logger.error("Der Temperatursensor wird von diesem Chip/Firmware nicht unterstützt.")

    return telemetry_dict

"""#####################################################################
#! @fn           load_config
#  @ brief       read the default config and override it with the override config
#  @ param       none
#  @ exception   none
#  @ return      dict with the merged configuration
#####################################################################"""
def load_config(config_name = None) -> dict:
    """Lädt die Default-Basis und überschreibt sie mit der Override-Config."""
    # Standardkonfiguration
    config = {} 
    # 1. Default-Config laden
    try:
        with open("config/default_config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Hinweis: default_config.json nicht gefunden. Nutze Hardcoded Defaults. Error {e}")

    # 2. Override-Config laden und Werte überschreiben
    try:
        with open("config/override_config.json", "r") as f:
            override = json.load(f)
            config.update(override)
    except Exception:
        # Falls keine Override-Datei existiert, ist das völlig okay
        pass
    
    if config_name is not None:
        return config[config_name]
    else:
        return config


"""#####################################################################
#! @fn           get_device_status()
#  @ brief       read the default config and override it with the override config
#  @ param       none
#  @ exception   none
#  @ return      dict with the merged configuration
#####################################################################"""
def get_device_status() -> dict:
    # 1. RAM auslesen
    ram_free = gc.mem_free()
    ram_used = gc.mem_alloc()
    ram_max = ram_free + ram_used

    # 2. CPU Frequenz in MHz
    cpu_mhz = machine.freq() // 1000000

    # 3. Flash-Speicher auslesen
    try:
        fs_info = os.statvfs('/')
        block_size = fs_info[0]
        total_blocks = fs_info[2]
        free_blocks = fs_info[3]

        flash_total = block_size * total_blocks
        flash_used = flash_total - (block_size * free_blocks)
    except Exception:
        flash_total, flash_used = 0, 0

    # 4. Interne Temperatur (mit Fallback, falls nicht unterstützt)
    temp_c = None
    if esp32 and hasattr(esp32, 'raw_temperature'):
        try:
            # raw_temperature() liefert Fahrenheit
            tf = esp32.raw_temperature()
            temp_c = round((tf - 32) * 5 / 9, 1)
        except Exception:
            pass

    # 5. System Uptime (Sekunden seit Start)
    uptime_s = time.ticks_ms() // 1000

    # 6. Wi-Fi Status
    wlan = network.WLAN(network.STA_IF)
    wifi_connected = wlan.isconnected()

    wifi_ssid = ""
    wifi_rssi = 0

    if wifi_connected:
        try:
            wifi_ssid = wlan.config('essid')
            # Hinweis: RSSI ist oft über wlan.status('rssi') abrufbar,
            # hängt aber stark von der MicroPython-Version ab.
            wifi_rssi = wlan.status('rssi')
        except Exception:
            pass

    # JSON-Struktur befüllen
    status_dict = {
        "ram": {
            "unit" : "Bytes",
            "free": ram_free,
            "used": ram_used,
            "max": ram_max
        },
        "cpu": {
            "unit": "MHz",
            "frequency_mhz": cpu_mhz
        },
        "flash": {
            "unit": "Bytes",
            "total_bytes": flash_total,
            "used_bytes": flash_used
        },
        "environment": {
            "unit": "°C",
            "temperature_c": temp_c
        },
        "system": {
            "unit": "s",
            "uptime_seconds": uptime_s
        },
        "wifi": {
            "connected": wifi_connected,
            "ssid": wifi_ssid,
            "rssi_dbm": wifi_rssi
        }
    }

    # In JSON-String konvertieren
    return status_dict


# Test-Ausgabe
print(get_device_status())

"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""


if __name__ == "__main__":
    print("Hello World!")
