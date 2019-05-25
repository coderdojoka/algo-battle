from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung
import random


class ricisAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__("Rici: Spirale")
        self._r = random.randint(0, 3)
        self._mode = 0
        self._zirkel = [Richtung.Oben, Richtung.Rechts, Richtung.Unten, Richtung.Links]
        self.counter = 0
        self.besucht_richtung = 0

    def _bereite_vor(self):
        max = -1
        r_max = -1
        for i, ri in enumerate(self._zirkel):
            if self.abstand(ri) > max:
                max = self.abstand(ri)
                r_max = i
        self._r = r_max

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:

        if self._mode == 5:
            self.counter -= 1
            # print("besucht mode")
            if self.counter == 0:
                self._mode = 0
            return self.besucht_richtung

        if letzter_zustand == FeldZustand.Besucht:
            self.counter += 1
            if self.counter == 5:
                self.counter = 30
                self._mode = 5
                self.besucht_richtung = Richtung.zufall(ausser=[self.richtung, self.richtung.gegenteil])
        else:
            self.counter =0

        if self._mode == 0:
            #print("0")
            if letzter_zustand.ist_blockiert:
                self._r = (self._r + 1) % 4
            elif letzter_zustand == FeldZustand.Besucht:
                self._mode = 1
                self._r = (self._r + 2) % 4
        elif self._mode == 2:
            #print("2")

            if letzter_zustand == FeldZustand.Besucht or letzter_zustand.ist_blockiert:
                self._mode = 1
                self._r = (self._r + 2) % 4

        elif self._mode == 1:
            #print("1")
            self._r = (self._r + 3) % 4
            self._mode = 2


        return self._zirkel[self._r]


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
