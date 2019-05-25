from algo_battle.domain.algorithmus import Algorithmus
import random
from algo_battle.domain import FeldZustand, Richtung



class am_meisten_Zufall(Algorithmus):

    def __init__(self):
        super().__init__("Robert")
        self.meine_richtung = Richtung.Rechts
        self.hallo = 0
        self.hallo2 = 0


    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        # Dieser (sehr dumme) Algorithmus fährt immer nur nach rechts :)
        # Hier sollte dein Algorithmus stehen!
        # WICHTIG: Diese Funktion muss eine Richtung, zurückgeben, z.b Richtung.Unten

        if zug_nummer % 40 == 0:
            self.hallo2 = random.randint(0, 3)

        if letzter_zustand == FeldZustand.Wand or letzter_zustand == FeldZustand.Belegt:
            self.hallo2 = random.randint(0, 3)
            self.hallo = random.randint(0, 1)
            # print(self.hallo2)

        if self.hallo2 == 0:
            if self.hallo == 0:
                self.meine_richtung = Richtung.Oben
                self.hallo = 1
                return self.meine_richtung

            if self.hallo == 1:
                self.meine_richtung = Richtung.Rechts
                self.hallo = 0
                return self.meine_richtung

        if self.hallo2 == 1:
            if self.hallo == 0:
                self.meine_richtung = Richtung.Oben
                self.hallo = 1
                return self.meine_richtung

            if self.hallo == 1:
                self.meine_richtung = Richtung.Links
                self.hallo = 0
                return self.meine_richtung

        if self.hallo2 == 2:
            if self.hallo == 0:
                self.meine_richtung = Richtung.Unten
                self.hallo = 1
                return self.meine_richtung

            if self.hallo == 1:
                self.meine_richtung = Richtung.Rechts
                self.hallo = 0
                return self.meine_richtung

        if self.hallo2 == 3:
            if self.hallo == 0:
                self.meine_richtung = Richtung.Unten
                self.hallo = 1
                return self.meine_richtung

            if self.hallo == 1:
                self.meine_richtung = Richtung.Links
                self.hallo = 0
                return self.meine_richtung

        return self.meine_richtung



if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])