import logging.config
import inspect
import yaml
import util
import algorithmen.einfach as einfache_algorithmen

from typing import Iterable, Type
from framework.wettkampf import Wettkampf, ArenaDefinition
from framework.algorithm import Algorithmus

with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))


# TODO Default values and fallback algorithm module in config
def main():
    print("Algo-Battle")
    anzahl_runden = util.input.lese_zahl("Anzahl der Runden", 9)
    anzahl_teilnehmer = util.input.lese_zahl("Anzahl der Teilnehmer", 2)

    fallback_algorithmen = [m[1] for m in inspect.getmembers(einfache_algorithmen, lambda m: inspect.isclass(m) and m.__module__ == einfache_algorithmen.__name__)]
    algorithmen = [
        util.input.lese_algorithmus("Algorithmus {}".format(i + 1), fallback_algorithmen) for i in range(anzahl_teilnehmer)
    ]

    arena_groesse = util.input.lese_arena_groesse("Arena Größe", (100, 100))
    arena_definition = ArenaDefinition(*arena_groesse)

    statistiken = util.EventStatistiken()
    for runde in range(anzahl_runden):
        wettkampf = Wettkampf(arena_definition.punkte_maximum, arena_definition, erzeuge_algorithmen(arena_definition, algorithmen))

        print("\nRunde {}".format(runde + 1))
        wettkampf.start()
        wettkampf.warte_auf_ende()
        wettkampf.berechne_punkte_neu()
        statistiken.speicher_runde(runde, wettkampf)
        print(util.wettkampf_ergebnis(wettkampf))
        print("Speichere Bild für Runde {}".format(runde + 1))
        util.speichere_arena_bild(runde, wettkampf)

    print("\n")
    print(statistiken.zusammenfassung)
    print("\n")
    print("Speicher Overlay Bild für alle Runden")
    util.speichere_overlay_bild(anzahl_runden)


def erzeuge_algorithmen(arena: ArenaDefinition, algorithmen: Iterable[Type[Algorithmus]]) -> Iterable[Algorithmus]:
    instanzen = [algorithmus() for algorithmus in algorithmen]
    for instanz in instanzen:
        setattr(instanz, "_arena", arena)
    return instanzen


if __name__ == "__main__":
    main()
