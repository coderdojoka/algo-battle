import logging.config
import util
import yaml

from framework.wettkampf import Wettkampf, ArenaDefinition
from einfache_algorithmen import Zufall, Liner

with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))


print("Algo-Battle")
runden = util.input.lese_zahl("Anzahl der Runden", 9)
anzahl_teilnehmer = util.input.lese_zahl("Anzahl der Teilnehmer", 2)

algorithmen = [
    util.input.lese_algorithmus("Algorithmus {}".format(i + 1), fallback_algorithmen=[Zufall, Liner])
    for i in range(anzahl_teilnehmer)
]

arena_groesse = util.input.lese_arena_groesse("Arena Größe", (100, 100))
arena_definition = ArenaDefinition(*arena_groesse)

for runde in range(runden):
    wettkampf = Wettkampf(
        arena_definition.punkte_maximum, arena_definition,
        [algorithmus() for algorithmus in algorithmen]
    )

    print("\nRunde {}".format(runde + 1))
    wettkampf.start()
    wettkampf.warte_auf_ende()
    print(util.wettkampf_uebersicht(wettkampf))
    print("Speichere Bild für Runde {}".format(runde + 1))
    util.speichere_arena_bild(runde, wettkampf)


