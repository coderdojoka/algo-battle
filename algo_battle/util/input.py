import logging
import random

from importlib import import_module
from typing import Sequence, Type
from algo_battle.domain.algorithmus import Algorithmus


def lese_zahl(text: str, default: int = None) -> int:
    default_text = " ({})".format(default) if default else ""
    eingabe = input("{}{}: ".format(text, default_text))
    try:
        return int(eingabe)
    except ValueError:
        return _nochmal_oder_default(
            "Die Eingabe '{}' konnte nicht als Zahl gelesen.".format(eingabe),
            default, lese_zahl, text, default
        )


def lese_arena_groesse(text: str, default: (int, int) = None) -> (int, int):
    default_text = " ({}x{})".format(default[0], default[1]) if default else ""
    eingabe = input("{}{}: ".format(text, default_text)).strip()
    teile = eingabe.split("x")
    if len(teile) < 2:
        return _nochmal_oder_default(
            "Das Trennzeichen 'x' konnte nicht in der Eingabe '{}' gefunden werden.".format(eingabe),
            default, lese_arena_groesse, text, default
        )

    try:
        breite = int(teile[0])
    except ValueError:
        return _nochmal_oder_default(
            "Die Breite '{}' konnte nicht als Zahl gelesen werden.".format(teile[0]),
            default, lese_arena_groesse, text, default
        )

    try:
        hoehe = int(teile[1])
    except ValueError:
        return _nochmal_oder_default(
            "Die Hoehe '{}' konnte nicht als Zahl gelesen werden.".format(teile[1]),
            default, lese_arena_groesse, text, default
        )

    return breite, hoehe


def _nochmal_oder_default(nachricht: str, default, lese_methode, *args, **kwargs):
    if default:
        return default
    else:
        print(nachricht)
        return lese_methode(*args, **kwargs)


def lese_algorithmus(text: str, fallback_algorithmen: Sequence[Type[Algorithmus]] = None) -> Type[Algorithmus]:
    default_text = " (zufälliger Algorithmus)" if fallback_algorithmen else ""
    eingabe = input("{}{}: ".format(text, default_text)).strip()
    error = None
    try:
        algorithmus_klasse = lade_algorithmus_klasse(eingabe)
    except ValueError as e:
        algorithmus_klasse = random.choice(fallback_algorithmen) if fallback_algorithmen else None
        error = e

    if algorithmus_klasse:
        print("Der Algorithmus {} wurde ausgewählt".format(algorithmus_klasse.__name__))
        return algorithmus_klasse
    else:
        print(str(error))
        return lese_algorithmus(text, fallback_algorithmen)


def lade_algorithmus_klasse(algorithmus: str) -> Type[Algorithmus]:
    modul_name, klasse_name = parse_algorithmus_pfad(algorithmus)
    try:
        modul = import_module(modul_name)
        return getattr(modul, klasse_name)
    except (ImportError, ValueError) as e:
        raise ValueError("Das Modul '{}' konnte nicht gefunden werden".format(modul_name)) from e
    except AttributeError as e:
        raise ValueError("Die Klasse '{}' konnte nicht im Modul '{}' gefunden werden".format(klasse_name, modul_name)) from e


def parse_algorithmus_pfad(pfad: str) -> (str, str):
    if not pfad:
        raise ValueError("Es wurde kein Pfad übergeben")
    trenn_index = pfad.rfind(".")
    if trenn_index < 0:
        raise ValueError("Der Pfad '{}' konnte nicht geparsed werden".format(pfad))
    return pfad[:trenn_index] if trenn_index > 0 else ".", pfad[trenn_index + 1:]


def logger() -> logging.Logger:
    return logging.getLogger("Util")