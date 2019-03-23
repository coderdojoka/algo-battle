import logging.config
import util
import yaml

from framework.wettkampf import Wettkampf, ArenaDefinition
from einfache_algorithmen import Zufall, Liner

with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))


print("Algo-Battle")
runden = util.lese_zahl("Anzahl der Runden (9): ", 9)
anzahl_teilnehmer = util.lese_zahl("Anzahl der Teilnehmer (2): ", 2)

algorithmen = []
for i in range(anzahl_teilnehmer):
    eingabe = input("Algorithmus {} (zufälliger einfacher Algorithmus): ".format(i + 1)).strip()
    algorithmus_klasse = util.lade_algorithmus_klasse(eingabe, fallback_algorithmen=[Zufall, Liner])
    algorithmen.append(algorithmus_klasse)
    print("Der Algorithmus {} wurde ausgewählt".format(algorithmus_klasse.__name__))

arena_definition = ArenaDefinition(100, 100)

for runde in range(runden):
    wettkampf = Wettkampf(
        arena_definition.punkte_maximum, arena_definition,
        [algorithmus() for algorithmus in algorithmen]
    )

    print("\nRunde {}".format(runde + 1))
    wettkampf.start()
    wettkampf.warte_auf_ende()
    print(util.wettkampf_uebersicht(wettkampf))
    print("Speichere Bild für Runde {}".format(runde))
    util.speichere_arena_bild(runde, wettkampf)


