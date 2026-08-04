# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# boot.py
# boot.py
import machine
import os

# REPL explizit auf Hardware-UART0 leiten (Anschluss "COM/UART")
#uart0 = machine.UART(0, baudrate=115200)
#os.dupterm(uart0, 0)
