import os
import logging
import random
import numpy as np

from typing import Tuple, Sequence, Type
from framework.wettkampf import Wettkampf
from framework.algorithm import Algorithmus

try:
    from PIL import Image, ImageDraw
    bilder_support = True
except ImportError:
    bilder_support = False


def lese_zahl(prompt: str, default: int = None) -> int:
    eingabe = input(prompt)
    try:
        return int(eingabe)
    except ValueError:
        if default:
            return default
        else:
            return lese_zahl(prompt)


def lade_algorithmus_klasse(algorithmus: str, fallback_algorithmen: Sequence[Type[Algorithmus]]) -> Type[Algorithmus]:
    klasse = None
    error = None

    try:
        modul_name, klasse_name = parse_algorithmus_pfad(algorithmus)
        try:
            modul = __import__(modul_name, globals(), locals())
            klasse = getattr(modul, klasse_name)
        except (ImportError, ValueError) as e:
            logger().error("Das Modul '{}' konnte nicht gefunden werden".format(modul_name))
            error = e
        except AttributeError as e:
            logger().error("Die Klasse '{}' konnte nicht im Modul '{}' gefunden werden".format(klasse_name, modul_name))
            error = e
    except ValueError as e:
        logger().error(str(e))
        error = e

    if error:
        if not fallback_algorithmen:
            raise error
        else:
            klasse = random.choice(fallback_algorithmen)
    return klasse


def parse_algorithmus_pfad(pfad: str) -> Tuple[str, str]:
    if not pfad:
        raise ValueError("Es wurde kein Pfad übergeben")
    trenn_index = pfad.rfind(".")
    if trenn_index < 0:
        raise ValueError("Der Pfad '{}' konnte nicht geparsed werden".format(pfad))
    return pfad[:trenn_index] if trenn_index > 0 else ".", pfad[trenn_index + 1:]


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
    (128, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)
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
    img.save(os.path.join(ordner, "Runde_{}.png".format(runde)))


def logger() -> logging.Logger:
    return logging.getLogger("Util")
