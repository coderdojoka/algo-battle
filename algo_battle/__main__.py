import logging.config
import yaml
import sys

from app.cli import run_cli
from app.pyside2_gui import start_gui

# TODO Only algorithm loggers should log the thread name
# TODO Check if file exists
with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))


if __name__ == "__main__":
    logger = logging.getLogger("Main")

    mode = "CLI"
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == "CLI":
        run_cli()
    elif mode == "GUI":
        start_gui()
    else:
        logger.critical("Unbekannter Modus '{}'".format(mode))
        sys.exit(1)
