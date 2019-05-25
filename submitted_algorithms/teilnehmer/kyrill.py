from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung



class KyrillsAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__("Kyrill")
        self.lrichtung = Richtung.Rechts
        self.nrichtung = Richtung.Unten
        self.a = 0
        self.b = 0
        self.c = 0
        self.oben = 0


    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:

        if self.c == 0:
            self.c = 1
            if self.abstand(Richtung.Oben) >= 50:
                self.nrichtung = Richtung.Oben

        if self.oben != 0:
            self.oben = 0
            return self.nrichtung

        if letzter_zustand == FeldZustand.Wand and self.a < 2 or letzter_zustand == FeldZustand.Belegt and self.a < 2:


            self.a = self.a + 1
            self.lrichtung = self.lrichtung.gegenteil

        elif letzter_zustand in [FeldZustand.Wand, FeldZustand.Belegt] and self.a >= 2:

            if self.b == 0:
                self.b = 1
                self.lrichtung = Richtung.Links
                return self.lrichtung

            elif self.b == 1:

                if letzter_zustand in [FeldZustand.Wand, FeldZustand.Belegt]:

                    self.oben = 1
                    self.lrichtung = self.lrichtung.gegenteil

        return self.lrichtung


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
