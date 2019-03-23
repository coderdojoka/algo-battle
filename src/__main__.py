import logging.config
import util
import yaml

from framework.wettkampf import Wettkampf, ArenaDefinition

with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))


print("Algo-Battle")

runden = util.lese_zahl("Anzahl der Runden (9): ", 9)
anzahl_teilnehmer = util.lese_zahl("Anzahl der Teilnehmer (2): ", 2)

algorithmen = [
    input("Algorithmus {}: ".format(i + 1)).strip() for i in range(anzahl_teilnehmer)
]
util.importiere_algorithmen(algorithmen, fallback=True)

arena_definition = ArenaDefinition(100, 100)

for runde in range(runden):
    wettkampf = Wettkampf(
        arena_definition.punkte_maximum, arena_definition,
        [util.erzeuge_algorithmus(algorithmus) for algorithmus in algorithmen]
    )

    print("\nRunde {}".format(runde + 1))
    wettkampf.start()
    wettkampf.warte_auf_ende()
    print(util.wettkampf_uebersicht(wettkampf))


