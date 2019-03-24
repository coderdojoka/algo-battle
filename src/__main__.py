import logging.config
import inspect
import yaml
import util
import algorithmen.einfach as einfache_algorithmen

from framework.wettkampf import Wettkampf, ArenaDefinition

with open("config/logging_config.yml") as f:
    logging.config.dictConfig(yaml.load(f, Loader=yaml.FullLoader))

# TODO Default values and fallback algorithm module in config


print("Algo-Battle")
runden = util.input.lese_zahl("Anzahl der Runden", 9)
anzahl_teilnehmer = util.input.lese_zahl("Anzahl der Teilnehmer", 2)

fallback_algorithmen = [m[1] for m in inspect.getmembers(einfache_algorithmen, lambda m: inspect.isclass(m) and m.__module__ == einfache_algorithmen.__name__)]
algorithmen = [
    util.input.lese_algorithmus("Algorithmus {}".format(i + 1), fallback_algorithmen) for i in range(anzahl_teilnehmer)
]

arena_groesse = util.input.lese_arena_groesse("Arena Größe", (100, 100))
arena_definition = ArenaDefinition(*arena_groesse)

statistiken = util.EventStatistiken()
for runde in range(runden):
    wettkampf = Wettkampf(
        arena_definition.punkte_maximum, arena_definition,
        [algorithmus() for algorithmus in algorithmen]
    )

    print("\nRunde {}".format(runde + 1))
    wettkampf.start()
    wettkampf.warte_auf_ende()
    statistiken.speicher_runde(runde, wettkampf)
    print(util.wettkampf_ergebnis(wettkampf))
    print("Speichere Bild für Runde {}".format(runde + 1))
    util.speichere_arena_bild(runde, wettkampf)

print("\n")
print(statistiken.zusammenfassung)

# runden_sieger = max(runden_statistiken.keys(), key=lambda t: runden_statistiken[t]["siege"])
# print("\n\nZusammenfassung: Teilnehmer [{}] {} gewinnt mit {} Siegen!".format(runden_sieger[0], runden_sieger[1], runden_statistiken[runden_sieger]["siege"]))
# runden_durchschnitt = {t: {"züge": mean(stats["züge"]), "punkte": mean(stats["punkte"])} for t, stats in runden_statistiken.items()}
# print("Durchschnittliche Züge: {}".format(" | ".join("[{}] {}: {}".format(t[0], t[1], stats["züge"]) for t, stats in runden_durchschnitt.items())))
# print("Durchschnittliche Punkte: {}".format(" | ".join("[{}] {}: {}".format(t[0], t[1], stats["punkte"]) for t, stats in runden_durchschnitt.items())))
