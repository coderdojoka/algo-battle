from abc import ABC, abstractmethod
from framework.domain import Richtung, ArenaDefinition, FeldZustand


class Algorithmus(ABC):

    def __init__(self, name: str):
        self._name = name
        self._richtung = Richtung.zufall()
        self._arena = None
        self.x = -1
        self.y = -1

    @property
    def name(self) -> str:
        return self._name

    @property
    def richtung(self) -> Richtung:
        return self._richtung

    @property
    def arena(self) -> ArenaDefinition:
        return self._arena

    @arena.setter
    def arena(self, arena: ArenaDefinition):
        if self._arena:
            raise ValueError("Die Arena ist schon gesetzt")
        self._arena = arena

    def abstand(self, richtung: Richtung):
        if richtung is Richtung.Oben:
            return self.y
        if richtung is Richtung.Rechts:
            return self.arena.breite - self.x
        if richtung is Richtung.Unten:
            return self.arena.hoehe - self.y
        if richtung is Richtung.Links:
            return self.x
        raise ValueError("Unbekannte Richtung: {}".format(richtung))

    def start(self):
        pass

    def aktualisiere(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int):
        neue_richtung = self._gib_richtung(letzter_zustand, zug_nummer, aktuelle_punkte)
        if neue_richtung:
            self._richtung = neue_richtung

    @abstractmethod
    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        pass
