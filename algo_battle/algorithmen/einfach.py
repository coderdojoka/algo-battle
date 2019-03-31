import random

from algo_battle.framework.algorithm import Algorithmus
from algo_battle.framework.domain import FeldZustand, Richtung


class Zufall(Algorithmus):

    _max_schritte = 50

    def __init__(self):
        super().__init__()
        self._zaehler = 0
        self._schritte = 0

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if self._zaehler >= self._schritte or letzter_zustand.ist_blockiert:
            self._zaehler = 0
            self._schritte = random.randint(10, self._max_schritte)
            return Richtung.zufall(ausser=self.richtung)

        self._zaehler += 1
        return self.richtung


class Liner(Algorithmus):

    def __init__(self):
        super().__init__()
        self._richtung = Richtung.Links
        self._reihe_aendern = False
        self._linker_rand = True
        self._reihen_aender_richtung = None

    def _bereite_vor(self):
        if self.abstand(Richtung.Unten) > self.abstand(Richtung.Oben):
            self._reihen_aender_richtung = Richtung.Unten
        else:
            self._reihen_aender_richtung = Richtung.Oben

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        richtung = None
        if letzter_zustand.ist_blockiert:
            if self.richtung.ist_horizontal:
                richtung = self._reihen_aender_richtung
                self._reihe_aendern = True
            else:
                self._reihen_aender_richtung = self._reihen_aender_richtung.umdrehen()
                richtung = self._reihen_aender_richtung
        elif self._reihe_aendern:
            self._reihe_aendern = False
            richtung = Richtung.Rechts if self._linker_rand else Richtung.Links
            self._linker_rand = not self._linker_rand
        return richtung