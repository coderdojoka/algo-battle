from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class DiagonalMultiLiner(Algorithmus):

    def __init__(self):
        super().__init__("Mark: Diagonal + Liner")
        self.richtung_gerade = None
        self.richtung_2 = None
        self.richtungen_2 = []
        self.richtung_2_index = 0
        self.umdrehen = False
        self.blockiert = 0
        self.total_blockiert = 0
        self.gerade_counter = 0
        self.diagonale_counter = 0
        self.wechsle_liner_zugnummer = 0

        self.richtung_liner = Richtung.Links
        self.reihe_aendern_liner = False
        self.linker_rand_liner = True
        self.reihen_aender_richtung_liner = Richtung.Oben
        self.reihen_richtung_liner = Richtung.Links
        self.liner_besucht_counter = 0

        self.phase = None

    def _bereite_vor(self):
        self.wechsle_liner_zugnummer = self.arena.breite * self.arena.hoehe * 0.1

    def phase_gerade(self, letzter_zustand: FeldZustand):

        self.gerade_counter += 1
        if self.umdrehen:
            self.richtung_gerade = self.richtung_gerade.drehe_nach_rechts()
            self.umdrehen = False

        if letzter_zustand.ist_blockiert:
            self.umdrehen = True
            self.blockiert += 1
            self.richtung_gerade = self.richtung_gerade.drehe_nach_rechts()
            if self.blockiert == 2:
                self.wechlse_zu_diagonale()
                return self.phase_diagonale(FeldZustand.Frei)

        if self.gerade_counter == 40:
            self.wechlse_zu_diagonale()

        return self.richtung_gerade

    def wechsle_zu_gerade_abschneiden(self):
        self.richtung_gerade = self.maximalerAbstandZumRand()
        self.blockiert = 0
        self.umdrehen = False
        self.gerade_counter = 0
        self.phase = self.phase_gerade

    def wechlse_zu_diagonale(self):
        alr, rlr = self.maxLRAbstand()
        auo, ruo = self.maxUOAbstand()
        self.richtungen_2 = [rlr, ruo]
        self.diagonale_counter = 0
        self.phase = self.phase_diagonale

    def phase_diagonale(self, letzter_zustand: FeldZustand):
        self.diagonale_counter += 1

        self.richtung_2_index = (self.richtung_2_index + 1) % 2
        self.richtung_2 = self.richtungen_2[self.richtung_2_index]

        if letzter_zustand.ist_blockiert:
            if self.richtung.ist_horizontal:
                self.richtungen_2[0] = self.richtungen_2[0].gegenteil
            else:
                self.richtungen_2[1] = self.richtungen_2[1].gegenteil

        return self.richtung_2

    def maxLRAbstand(self):
        al, ar = self.abstand(Richtung.Links), self.abstand(Richtung.Rechts)

        if al > ar:
            return al, Richtung.Links
        else:
            return ar, Richtung.Rechts

    def maxUOAbstand(self):
        au, ao = self.abstand(Richtung.Unten), self.abstand(Richtung.Oben)

        if au > ao:
            return au, Richtung.Unten
        else:
            return ao, Richtung.Oben

    def maximalerAbstandZumRand(self):
        alr, rlr = self.maxLRAbstand()
        auo, ruo = self.maxUOAbstand()

        if alr > auo:
            return rlr
        else:
            return ruo

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        self.total_blockiert += letzter_zustand.ist_blockiert
        if self.phase != self.phase_liner and (self.total_blockiert > 15 or zug_nummer > self.wechsle_liner_zugnummer):
            self.wechsle_phase_liner()

        if self.phase is None:
            self.wechlse_zu_diagonale()
        return self.phase(letzter_zustand)

    def wechsle_phase_liner(self):
        if self.abstand(Richtung.Unten) > self.abstand(Richtung.Oben):
            self.reihen_aender_richtung_liner = Richtung.Unten
        else:
            self.reihen_aender_richtung_liner = Richtung.Oben
        self.reihen_richtung_liner = self.reihen_aender_richtung_liner.drehe_nach_rechts()
        self.phase = self.phase_liner

    def phase_liner(self, letzter_zustand: FeldZustand) -> Richtung:

        if letzter_zustand == FeldZustand.Besucht:
            self.liner_besucht_counter += 1
        else:
            self.liner_besucht_counter = 0
        richtung = self.reihen_richtung_liner

        if letzter_zustand.ist_blockiert:
            if not self.reihe_aendern_liner:
                richtung = self.reihen_aender_richtung_liner
                self.reihen_richtung_liner = self.reihen_richtung_liner.gegenteil
                self.reihe_aendern_liner = True
            else:
                self.reihen_aender_richtung_liner = self.reihen_aender_richtung_liner.drehe_nach_links()
                self.reihen_richtung_liner = self.reihen_aender_richtung_liner.drehe_nach_rechts()
                richtung = self.reihen_aender_richtung_liner

        elif self.reihe_aendern_liner:
            self.reihe_aendern_liner = False

        if self.liner_besucht_counter > 51:
            self.reihen_aender_richtung_liner = self.reihen_aender_richtung_liner.drehe_nach_rechts()
            self.reihen_richtung_liner = self.reihen_aender_richtung_liner.drehe_nach_rechts()
            self.liner_besucht_counter = 0

        return richtung




if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
