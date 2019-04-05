import random
from enum import unique, Enum
from typing import Tuple, Union, Iterable


@unique
class FeldZustand(Enum):
    Frei = 1
    Wand = 2
    Belegt = 3
    Besucht = 4

    @property
    def ist_betretbar(self):
        return self is FeldZustand.Frei or self is FeldZustand.Besucht

    @property
    def ist_blockiert(self):
        return not self.ist_betretbar


class ArenaDefinition:

    def __init__(self, breite: int, hoehe: int):
        self._breite = breite
        self._hoehe = hoehe

    @property
    def breite(self) -> int:
        return self._breite

    @property
    def hoehe(self) -> int:
        return self._hoehe

    @property
    def form(self) -> Tuple[int, int]:
        return self.breite, self.hoehe

    @property
    def punkte_maximum(self):
        return self.breite * self.hoehe

    def __str__(self):
        return "{}[{}x{}]".format(
            self.__class__.__name__, self.breite, self.hoehe
        )


@unique
class Richtung(Enum):
    Oben = (0, -1)
    Rechts = (1, 0)
    Unten = (0, 1)
    Links = (-1, 0)

    def __init__(self, dx: int, dy: int):
        self._dx = dx
        self._dy = dy

    @property
    def dx(self) -> int:
        return self._dx

    @property
    def dy(self) -> int:
        return self._dy

    @property
    def ist_horizontal(self):
        return self is Richtung.Links or self is Richtung.Rechts

    @property
    def ist_vertikal(self):
        return not self.ist_horizontal

    @property
    def gegenteil(self):
        return Richtung((self.dx * -1, self.dy * -1))

    def drehe_nach_rechts(self):
        if self is Richtung.Oben:
            return Richtung.Rechts
        if self is Richtung.Rechts:
            return Richtung.Unten
        if self is Richtung.Unten:
            return Richtung.Links
        if self is Richtung.Links:
            return Richtung.Oben

    def drehe_nach_links(self):
        if self is Richtung.Oben:
            return Richtung.Links
        if self is Richtung.Rechts:
            return Richtung.Oben
        if self is Richtung.Unten:
            return Richtung.Rechts
        if self is Richtung.Links:
            return Richtung.Unten

    @staticmethod
    def zufall(*, ausser: Union["Richtung", Iterable["Richtung"]] = None) -> "Richtung":
        if ausser is None:
            ausser = {}
        elif isinstance(ausser, Richtung):
            ausser = {ausser}

        richtung = random.choice(_richtungen)
        while richtung in ausser:
            richtung = random.choice(_richtungen)
        return richtung


_richtungen = list(Richtung)