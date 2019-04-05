import time
import random

from algo_battle.domain.algorithmus import Algorithmus
from domain import FeldZustand, Richtung
from algo_battle.algorithmen.einfach import Zufall


class Faultier(Zufall):

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        time.sleep(0.05)
        return super()._gib_richtung(letzter_zustand, zug_nummer, aktuelle_punkte)


class Punkt(Algorithmus):

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        return self.richtung.drehe_nach_rechts()


class Chell(Algorithmus):

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int):
        self._x = random.randrange(0, self.arena.breite)
        self._y = random.randrange(0, self.arena.hoehe)
