import logging.config
import sys

from algo_battle.app.cli import run_cli
from algo_battle.app.pyside2_gui import start_gui

if __name__ == "__main__":
    logger = logging.getLogger("Main")

    mode = "CLI"
    modul_pfade = None
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        modul_pfade = sys.argv[2:]

    if mode == "CLI":
        run_cli(modul_pfade)
    elif mode == "GUI":
        start_gui(modul_pfade)
    else:
        logger.critical("Unbekannter Modus '{}'".format(mode))
        sys.exit(1)
