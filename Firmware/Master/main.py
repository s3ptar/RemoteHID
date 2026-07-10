"""#####################################################################
#! @ file:                   main.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ Target:                 esp32
#  @ version:                0
#  @ history:                -
#  @ brief                  : erstellt mit Hilfe von Gemini, 
#                             einem KI-Tool von OpenAI, um die
                              Entwicklung zu beschleunigen.
#####################################################################"""

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

import asyncio
import loghandler
from HT_SSD1306Wire import (
    SSD1306Wire, GEOMETRY_128_64, GEOMETRY_128_32,
    ANGLE_0_DEGREE, ANGLE_90_DEGREE, ANGLE_180_DEGREE, ANGLE_270_DEGREE
)
from machine import Pin
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
        #logger.debug(utilities.get_device_telemetry())
        logger.debug(utilities.get_device_status())

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

    utilities.get_device_telemetry()

    if gc.isenabled():
        logger.info(f"Garbage Collector disable, is now enabled.")
        gc.enable()
        gc.collect()
    else:
        logger.info(f"Garbage Collector enable")

    logger.info("Main loop")


    asyncio.run(main_loop())



    




    
