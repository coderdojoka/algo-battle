import os
import logging
import numpy as np
import pandas as pd
import inspect

from typing import Type, List
from importlib import import_module
from framework.wettkampf import Wettkampf, Gleichstand
from framework.algorithm import Algorithmus

# Imports zur Bereitstellung innerer Module
import util.input

try:
    from PIL import Image, ImageDraw
    bilder_support = True
except ImportError:
    bilder_support = False


def gib_algorithmen_in_modul(modul) -> List[Type[Algorithmus]]:
    if isinstance(modul, str):
        try:
            modul = import_module(modul)
        except (ImportError, ValueError):
            logger().error("Das Modul '{}' konnte nicht gefunden werden".format(modul))
            return []

    return [
        m[1] for m in inspect.getmembers(modul,
            lambda m: inspect.isclass(m) and m.__module__ == modul.__name__ and issubclass(m, Algorithmus)
        )
    ]


def wettkampf_ergebnis(wettkampf: Wettkampf) -> str:
    zuege_uebersicht = "Züge gesamt: {} | {}".format(
        wettkampf.aktueller_zug,
        " | ".join("{}: {}".format(t, wettkampf.zuege_von(t)) for t in wettkampf.teilnehmer)
    )

    punkte_uebersicht = "Punkte: {}".format(
        " | ".join("{}: {}".format(t, wettkampf.punkte_von(t)) for t in wettkampf.teilnehmer)
    )

    sieger = wettkampf.sieger
    if sieger is Gleichstand:
        ergebnis_nachricht = "Gleichstand! Es gibt keinen Gewinner."
    else:
        ergebnis_nachricht = "Teilnehmer {} gewinnt!".format(sieger)
    return "\n".join([zuege_uebersicht, punkte_uebersicht, ergebnis_nachricht])


class EventStatistiken:

    def __init__(self):
        self._daten = pd.DataFrame()

    @property
    def daten(self) -> pd.DataFrame:
        return self._daten

    def speicher_runde(self, runde: int, wettkampf: Wettkampf):
        sieger = wettkampf.sieger
        rohdaten = {}
        for teilnehmer in wettkampf.teilnehmer:
            nummer = teilnehmer.nummer + 1
            name = teilnehmer.name
            rohdaten[(nummer, name, "Züge")] = wettkampf.zuege_von(teilnehmer)
            rohdaten[(nummer, name, "Punkte")] = wettkampf.punkte_von(teilnehmer)
            rohdaten[(nummer, name, "Siege")] = 1 if teilnehmer is sieger else 0

        runden_daten = pd.DataFrame(rohdaten, index=[runde])
        runden_daten.index.name = "Runde"
        runden_daten.columns.names = ["Nummer", "Name", "Statistik"]

        self._daten = self._daten.append(runden_daten)

    @property
    def zusammenfassung(self) -> str:
        siege = self._daten.xs("Siege", axis="columns", level=2, drop_level=True).sum()
        max_siege = siege.max()
        gewinner = siege[siege == max_siege].index
        if len(siege) == len(gewinner):
            gewinner_nachricht = "Gleichstand! Alle Teilnehmer haben {} Runde{} gewonnen.".format(
                max_siege, "n" if max_siege > 1 else ""
            )
        else:
            gewinner_nachricht = "Teilnehmer {} gewinn{} mit {} Sieg{}!".format(
                ", ".join("[{}] {}".format(t[0], t[1]) for t in gewinner),
                "en" if len(gewinner) > 1 else "t", max_siege, "en" if max_siege > 1 else ""
            )

        zuege_durchschnitt = self._daten.xs("Züge", axis="columns", level=2, drop_level=True).mean()
        zuege_nachricht = "Durchschnittliche Züge: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, zuege) for (nummer, name), zuege in zuege_durchschnitt.iteritems()
        ))

        punkte_durchschnitt = self._daten.xs("Punkte", axis="columns", level=2, drop_level=True).mean()
        punkte_nachricht = "Durchschnittliche Punkte: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, punkte) for (nummer, name), punkte in punkte_durchschnitt.iteritems()
        ))

        return "Zusammenfassung: {}\n{}\n{}".format(
            gewinner_nachricht, zuege_nachricht, punkte_nachricht
        )


hintergrund_farbe = (0, 0, 0)
teilnehmer_farben = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
    (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (0, 128, 128), (128, 0, 128), (128, 128, 128)
]


def speichere_arena_bild(runde: int, wettkampf: Wettkampf, feld_groesse=9, ordner="Bilder"):
    if not bilder_support:
        logger().warning("Bilder können nicht gespeichert werden. Installiere das Modul 'pillow' zuerst.")
        return

    arena = wettkampf.arena_definition
    img = Image.new("RGB", (arena.breite * feld_groesse, arena.hoehe * feld_groesse))
    draw = ImageDraw.Draw(img)

    arena_felder = wettkampf.wettkampf_snapshot
    it = np.nditer(arena_felder, flags=["multi_index"])
    while not it.finished:
        wert = it[0]
        x, y = it.multi_index
        if wert < 0:
            farbe = hintergrund_farbe
        else:
            farbe = teilnehmer_farben[wert]
        draw.rectangle(
            (
                (x * feld_groesse, y * feld_groesse),
                ((x + 1) * feld_groesse, (y + 1) * feld_groesse)
            ),
            fill=farbe
        )
        it.iternext()

    os.makedirs(ordner, exist_ok=True)
    img.convert(mode="RGBA").save(os.path.join(ordner, "Runde_{}.png".format(runde + 1)))


def speichere_overlay_bild(anzahl_runden: int, ordner="Bilder"):
    if not bilder_support:
        logger().warning("Bilder können nicht gespeichert werden. Installiere das Modul 'pillow' zuerst.")
        return

    img = None
    for runde in range(1, anzahl_runden + 1):
        next_img = Image.open(os.path.join(ordner, "Runde_{}.png".format(runde)))
        if not img:
            img = next_img
        else:
            img = Image.blend(img, next_img, 0.5)

    img.save(os.path.join(ordner, "Overlay_Runden_1-{}.png".format(anzahl_runden)))


def logger() -> logging.Logger:
    return logging.getLogger("Util")
