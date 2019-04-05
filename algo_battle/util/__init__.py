import os
import logging
import numpy as np
import inspect

from typing import Type, List
from importlib import import_module
from algo_battle.domain.wettkampf import Wettkampf, Gleichstand
from algo_battle.domain.algorithmus import Algorithmus

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

    arena_felder = wettkampf.wettkampf_snapshot()[0]
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
