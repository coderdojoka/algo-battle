from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung

liste_andersrum = {Richtung.Oben: Richtung.Unten, Richtung.Unten: Richtung.Oben, Richtung.Links: Richtung.Rechts, Richtung.Rechts: Richtung.Links}


class Rechtecke(Algorithmus):
    def __init__(self):
        super().__init__("Rouven")
        self.meine_richtung = Richtung.Rechts
        self.zustand = 0
        self.blau_gedreht = 0
        self.liste_verschiebung_startpunkt = [0, 0]
        self.nach_start_rechteck = False
        self.liste_zuege = [Richtung.Links]
        self.stelle_zurueck_zuege = 0

        self.phase_rechts = True

    def richtung_eins_drehen(self):
        if self.phase_rechts:
            self.meine_richtung = self.meine_richtung.drehe_nach_rechts()

        else:
            self.meine_richtung = self.meine_richtung.drehe_nach_links()

    def richtung_zwei_drehen(self):
        if self.phase_rechts:
            self.meine_richtung = self.meine_richtung.drehe_nach_links()

        else:
            self.meine_richtung = self.meine_richtung.drehe_nach_rechts()

    def verschiebung_verrechnen(self):
        if self.meine_richtung == Richtung.Oben:
            self.liste_verschiebung_startpunkt[1] -= 1

        if self.meine_richtung == Richtung.Unten:
            self.liste_verschiebung_startpunkt[1] += 1

        if self.meine_richtung == Richtung.Links:
            self.liste_verschiebung_startpunkt[0] -= 1

        if self.meine_richtung == Richtung.Rechts:
            self.liste_verschiebung_startpunkt[0] += 1

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if self.blau_gedreht > 4:
            if not self.phase_rechts:
                if letzter_zustand != FeldZustand.Frei:
                    return Richtung.zufall(ausser=self.meine_richtung.gegenteil)

                else:
                    return self.meine_richtung

            if self.liste_verschiebung_startpunkt[0] < 0:
                self.meine_richtung = Richtung.Rechts

            elif self.liste_verschiebung_startpunkt[0] > 0:
                self.meine_richtung = Richtung.Links

            else:
                if self.liste_verschiebung_startpunkt[1] < 0:
                    self.meine_richtung = Richtung.Unten

                elif self.liste_verschiebung_startpunkt[1] > 0:
                    self.meine_richtung = Richtung.Oben

                else:
                    self.liste_zuege = self.liste_zuege[::-1]
                    self.zustand = 3
                    self.blau_gedreht = 0

        elif self.zustand == 3:
            self.meine_richtung = self.liste_zuege[self.stelle_zurueck_zuege]
            self.stelle_zurueck_zuege += 1

            if self.stelle_zurueck_zuege == len(self.liste_zuege):
                self.phase_rechts = False
                self.zustand = 0
                self.blau_gedreht = 0
                self.liste_verschiebung_startpunkt = [0, 0]
                self.nach_start_rechteck = False
                self.liste_zuege = [liste_andersrum[self.meine_richtung]]
                self.stelle_zurueck_zuege = 0

        elif self.zustand == 1:
            self.richtung_eins_drehen()
            self.zustand = 2

        elif self.zustand == 2:
            self.richtung_zwei_drehen()
            self.zustand = 0

        else:
            if letzter_zustand == FeldZustand.Belegt or letzter_zustand == FeldZustand.Wand:
                if len(self.liste_zuege) > 0:
                    self.richtung_eins_drehen()
                    self.liste_zuege.pop(-1)

            elif letzter_zustand == FeldZustand.Besucht:
                self.verschiebung_verrechnen()
                self.liste_zuege.append(liste_andersrum[self.meine_richtung])
                self.nach_start_rechteck = True
                self.zustand = 1
                self.richtung_eins_drehen()
                self.blau_gedreht += 1

            else:
                self.blau_gedreht = 0

        if self.nach_start_rechteck:
            self.verschiebung_verrechnen()

        else:
            self.liste_zuege.append(liste_andersrum[self.meine_richtung])

        return self.meine_richtung


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    from algo_battle.app.cli import run_cli

    start_gui([__name__])
