"""#####################################################################
#! @ file:                   main.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ Target:                 esp32
#  @ version:                E01
#  @ history:                -
#  @ brief                  : erstellt mit Hilfe von Gemini, 
#                             einem KI-Tool von OpenAI, um die
                              Entwicklung zu beschleunigen.
                              E01 board umgestellt auf YF-ESP32-23
#####################################################################"""
from lib.logging import debug

"""#####################################################################
# Includes
#####################################################################"""
import sys

import logging
import os
import time
import utilities
import gc
import webrepl
import sys
import select
import time
import asyncio
import loghandler

import usb.device
from usb.device.cdc import CDCInterface


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
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

# 1. Erstelle eine neue CDC-Schnittstelle
cdc = CDCInterface(timeout=0)

"""#####################################################################
# local Variable
#####################################################################"""

"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
async def main_loop():
    while True:
        await asyncio.sleep(30)
        # logger.debug(utilities.get_device_telemetry())
        logger.debug(utilities.get_device_status())

async def read_cdc_uart():
    while True:
        if cdc.is_open():
            # Auf eingehende Daten am nativen USB-Port prüfen
            rx_bytes = cdc.read(-1)
            if rx_bytes:
                #rx_bytes = cdc_uart.readline()
                # Log auf der UART-REPL ausgeben
                logger.info(f"[UART REPL Log] Über nativen USB empfangen: {rx_bytes}")

                # Daten/Antwort über nativen USB zurücksenden
                cdc.write(b"USB-CDC OK: " + rx_bytes)

# ==============================================================================
# Main Task
# ==============================================================================
async def main():
    # task1 = asyncio.create_task(web_server.start())
    # await task1

    # Automatische Aktivierung nach Bootup
    # await asyncio.sleep(20)

    await asyncio.gather(
        # task_hid.evdev_loop(),
        # web_server.start(),
        read_cdc_uart()
        #asyncio.sleep(30)
    )



"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == "__main__":
    print("Starting LED ClockRing Application")

    logger = loghandler.setup_logger()
    logger.info("Logger erfolgreich eingerichtet.")

    # Native USB exklusiv nutzen
    usb.device.get().init(cdc, builtin_driver=False)

    utilities.get_device_telemetry()

    if gc.isenabled():
        logger.info(f"Garbage Collector disable, is now enabled.")
        gc.enable()
        gc.collect()
    else:
        logger.info(f"Garbage Collector enable")

    logger.info("Main loop")

    asyncio.run(main())








