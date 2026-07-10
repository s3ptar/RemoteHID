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
import logging
import os
import utilities

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
# Local Funtions
#####################################################################"""
class RotatingFileHandler(logging.Handler):
    def __init__(self, filename, max_bytes=1024, backup_count=3):
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._stream = open(filename, "a")

    def emit(self, record):
        try:
            # Format the message
            msg = self.format(record) + "\n"

            # Check if we need to rollover before writing
            if self._stream.tell() + len(msg) >= self.max_bytes:
                self.do_rollover()

            self._stream.write(msg)
            self._stream.flush()
        except Exception:
            # Fail silently or use print() if debugging on hardware
            pass

    def do_rollover(self):
        self._stream.close()

        # Delete the oldest backup if it exists
        oldest_file = f"{self.filename}.{self.backup_count}"
        try:
            os.remove(oldest_file)
        except OSError:
            pass

        # Shift middle backups down: log.1 -> log.2, etc.
        for i in range(self.backup_count - 1, 0, -1):
            sfn = f"{self.filename}.{i}"
            dfn = f"{self.filename}.{i + 1}"
            try:
                os.rename(sfn, dfn)
            except OSError:
                pass

        # Rename current log to log.1
        try:
            os.rename(self.filename, f"{self.filename}.1")
        except OSError:
            pass

        # Open a fresh log file
        self._stream = open(self.filename, "w")

    def close(self):
        self._stream.close()
        super().close()


"""#####################################################################
#! @fn           get_log_level
#  @ brief       Konvertiert den String-Level in die logging-Konstante
#  @ param       level_str - String wie "DEBUG", "INFO", etc.
#  @ exception   none
#  @ return      none
#####################################################################"""
def get_log_level(level_str):
    levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG
    }
    return levels.get(level_str.upper(), logging.INFO)


"""#####################################################################
#! @fn           setup_logger
#  @ brief       read the default config and override it with the override config
#  @ param       name=__name__ - Name des Loggers, standardmäßig der Modulname
#  @ exception   none
#  @ return      none
#####################################################################"""
def setup_logger(name=__name__):
    config = utilities.load_config("Logging")

    # Root Logger anpassen
    logger_ = logging.getLogger()
    logger_.setLevel(get_log_level(config["loglevel_console"]))

    # Bestehende Handler löschen (wichtig bei Soft-Resets in MicroPython)
    logger_.handlers = []
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # --- KONSOLEN-AUSGABE ---
    if config["console_output"]:
        # MicroPython nutzt standardmäßig einen StreamHandler für die Konsole
        ch = logging.StreamHandler()
        logger_.setLevel(get_log_level(config["loglevel_console"]))
        ch.setFormatter(formatter)
        logger_.addHandler(ch)

    # --- FILE-AUSGABE ---
    if config["file_output"]:
        # Standard Python nutzt den professionellen RotatingFileHandler

        fh = RotatingFileHandler(config["filepath"], max_bytes=config["max_bytes"], backup_count=config["backup_count"])
        fh.setLevel(get_log_level(config["loglevel_file"]))
        fh.setFormatter(formatter)
        logger_.addHandler(fh)

    return logging.getLogger(__name__)  # Gibt den Logger für main zurück


"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == "__main__":
    print("main")







