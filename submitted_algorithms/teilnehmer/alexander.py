from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class MeinAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__("Alexander")
        self.meine_richtung = Richtung.Rechts
        self.zeahler = 10

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int,) -> Richtung:


        if letzter_zustand == FeldZustand.Wand or letzter_zustand == FeldZustand.Belegt and self.zeahler == 11:
            self.meine_richtung = Richtung.zufall()

        if letzter_zustand == FeldZustand.Belegt and self.zeahler == 11:
            self.meine_richtung = Richtung.zufall(ausser=Richtung.Oben)

        if letzter_zustand == FeldZustand.Besucht:
            self.meine_richtung = Richtung.drehe_nach_rechts

        if letzter_zustand == FeldZustand.Belegt and self.zeahler == 11:
            self.meine_richtung = Richtung.zufall(ausser=Richtung.Rechts)

        if letzter_zustand == FeldZustand.Belegt and FeldZustand.Wand or letzter_zustand == FeldZustand.Wand and FeldZustand.Belegt and self.zeahler == 11:
            self.meine_richtung = Richtung.zufall()

        if letzter_zustand == FeldZustand.Besucht and FeldZustand.Belegt or letzter_zustand == FeldZustand.Belegt and FeldZustand.Besucht:
            for d in range (0, 7):
                self.meine_richtung = Richtung.zufall()

        if self.zeahler == 10:
            for i in range(0, 5):
                self.meine_richtung = Richtung.zufall()
                self.zeahler = 11



        return self.meine_richtung


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])