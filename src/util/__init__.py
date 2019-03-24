import os
import logging
import numpy as np

from framework.wettkampf import Wettkampf

# Imports zur Bereitstellung innerer Module
import util.input

try:
    from PIL import Image, ImageDraw
    bilder_support = True
except ImportError:
    bilder_support = False


def wettkampf_uebersicht(wettkampf: Wettkampf) -> str:
    zuege_uebersicht = "Züge gesamt: {} | {}".format(
        wettkampf.aktueller_zug,
        " | ".join("[{}] {}: {}".format(t.nummer + 1, t.name, wettkampf.zuege_von(t)) for t in wettkampf.teilnehmer)
    )
    punkte_uebersicht = "Punkte: {}".format(
        " | ".join("[{}] {}: {}".format(t.nummer + 1, t.name, wettkampf.punkte_von(t)) for t in wettkampf.teilnehmer)
    )
    punkte_pro_teilnehmer = wettkampf._punkte_pro_teilnehmer
    punkte_liste = list(punkte_pro_teilnehmer.values())
    if all(p == punkte_liste[0] for p in punkte_liste):
        ergebnis_nachricht = "Gleichstand! Es gibt keinen Gewinner."
    else:
        gewinner = max(punkte_pro_teilnehmer.keys(), key=lambda t: punkte_pro_teilnehmer[t])
        ergebnis_nachricht = "Teilnehmer {} {} gewinnt!".format(gewinner.nummer + 1, gewinner.name)
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

    arena = wettkampf._arena
    img = Image.new("RGB", (arena.breite * feld_groesse, arena.hoehe * feld_groesse))
    draw = ImageDraw.Draw(img)

    arena_felder = arena._felder
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
    img.save(os.path.join(ordner, "Runde_{}.png".format(runde + 1)))


def logger() -> logging.Logger:
    return logging.getLogger("Util")
