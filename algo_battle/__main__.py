import logging.config
import sys

from algo_battle.app.cli import run_cli

_gui_available = False
try:
    from algo_battle.app.pyside2_gui import start_gui

    _gui_available = True
except ImportError as e:
    print("GUI Modus nicht verfügbar. Stelle sicher das du Pyside2 installiert hast.", file=sys.stderr)

if __name__ == "__main__":
    logger = logging.getLogger("Main")

    mode = "CLI"
    modul_pfade = None
    if len(sys.argv) > 1:
        mode = sys.argv[1].upper()
        modul_pfade = sys.argv[2:]

    if not _gui_available and mode == "GUI":
        print("GUI Modus nicht verfügbar. Starte CLI Modus.", file=sys.stderr)
        mode = "CLI"

    if mode == "CLI":
        run_cli(modul_pfade)
    elif mode == "GUI":
        start_gui(modul_pfade)
    else:
        logger.critical("Unbekannter Modus '{}'".format(mode))
        sys.exit(1)
