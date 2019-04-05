import algo_battle.util.input

from typing import Iterable
from algo_battle.util import builtin_algorithmen
from algo_battle.domain.wettkampf import Wettkampf
from algo_battle.domain.util import EventStatistiken
from algo_battle.domain import ArenaDefinition


def run_cli(module: Iterable[str] = None):
    print("Algo-Battle")
    anzahl_runden = algo_battle.util.input.lese_zahl("Anzahl der Runden", 9)
    anzahl_teilnehmer = algo_battle.util.input.lese_zahl("Anzahl der Teilnehmer", 2)

    fallback_algorithmen = algo_battle.util.gib_algorithmen_in_modul(builtin_algorithmen)
    if module:
        for modul_pfad in module:
            fallback_algorithmen.extend(algo_battle.util.gib_algorithmen_in_modul(modul_pfad))
    algorithmen = [
        algo_battle.util.input.lese_algorithmus("Algorithmus {}".format(i + 1), fallback_algorithmen) for i in range(anzahl_teilnehmer)
    ]

    arena_groesse = algo_battle.util.input.lese_arena_groesse("Arena Größe", (100, 100))
    arena_definition = ArenaDefinition(*arena_groesse)

    statistiken = EventStatistiken()
    for runde in range(anzahl_runden):
        wettkampf = Wettkampf(arena_definition.punkte_maximum, arena_definition, [algorithmus() for algorithmus in algorithmen])

        print("\nRunde {}".format(runde + 1))
        wettkampf.start()
        wettkampf.warte_auf_ende()
        wettkampf.berechne_punkte_neu()
        statistiken.speicher_runde(wettkampf)
        print(algo_battle.util.wettkampf_ergebnis(wettkampf))
        print("Speichere Bild für Runde {}".format(runde + 1))
        algo_battle.util.speichere_arena_bild(runde, wettkampf)

    print("\n")
    print(statistiken.zusammenfassung)
    
    print("\nSpeichere Overlay Bild für alle Runden")
    algo_battle.util.speichere_overlay_bild(anzahl_runden)