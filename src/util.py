import logging

from typing import Tuple, Iterable
from framework.wettkampf import Wettkampf
from framework.algorithm import Algorithmus
from einfache_algorithmen import Zufall, Liner

_importierte_algorithmen = {}


def lese_zahl(prompt: str, default: int = None) -> int:
    eingabe = input(prompt)
    try:
        return int(eingabe)
    except ValueError:
        if default:
            return default
        else:
            return lese_zahl(prompt)


def importiere_algorithmen(algorithmen: Iterable[str], fallback: bool):
    for algorithmus in algorithmen:
        importiere_algorithmus(algorithmus, fallback)


def importiere_algorithmus(algorithmus: str, fallback: bool):
    modul_name, klasse_name = parse_algorithmus_pfad(algorithmus)
    error = None
    try:
        modul = __import__(modul_name, globals(), locals())
        klasse = getattr(modul, klasse_name)
        _importierte_algorithmen[algorithmus] = klasse
    except (ImportError, ValueError) as e:
        logger().error("Das Modul '{}' konnte nicht gefunden werden".format(modul_name))
        error = e
    except AttributeError as e:
        logger().error("Die Klasse '{}' konnte nicht im Modul '{}' gefunden werden".format(klasse_name, modul_name))
        error = e

    if error:
        if not fallback:
            raise error
        else:
            _importierte_algorithmen[algorithmus] = _algorithmus_fallback_factory


def erzeuge_algorithmus(algo_pfad: str) -> Algorithmus:
    if algo_pfad not in _importierte_algorithmen:
        importiere_algorithmus(algo_pfad, fallback=False)
    return _importierte_algorithmen[algo_pfad]()


def parse_algorithmus_pfad(pfad: str) -> Tuple[str, str]:
    trenn_index = pfad.rfind(".")
    return pfad[:trenn_index], pfad[trenn_index + 1:]


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


def logger() -> logging.Logger:
    return logging.getLogger("Util")


class AlgorithmusFallbackFactory:

    def __init__(self):
        self._fallback_algorithmen = [Zufall, Liner]
        self._index = 0

    def __call__(self, *args, **kwargs):
        algorithmus = self._fallback_algorithmen[self._index]()
        self._index += 1
        if self._index >= len(self._fallback_algorithmen):
            self._index = 0
        return algorithmus


_algorithmus_fallback_factory = AlgorithmusFallbackFactory()
