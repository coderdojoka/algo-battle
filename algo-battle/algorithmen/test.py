import time

from framework.algorithm import Algorithmus
from framework.domain import FeldZustand, Richtung
from algorithmen.einfach import Zufall


class Faultier(Zufall):

    def __init__(self):
        super().__init__()
        self._name = "Faultier"

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        time.sleep(0.05)
        return super()._gib_richtung(letzter_zustand, zug_nummer, aktuelle_punkte)


class Punkt(Algorithmus):

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        return self.richtung.drehe_nach_rechts()
