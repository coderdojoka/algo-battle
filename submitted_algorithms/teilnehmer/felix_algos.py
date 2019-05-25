from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class Ablaufer(Algorithmus):
    def __init__(self):
        super().__init__()
        self.aktuelle_richtung = Richtung.zufall()
        self.komisch = 0
        self.verbleibend = 0

    def _bereite_vor(self):
        pass

    def _gib_richtung(self, lz: FeldZustand, zn: int, ap: int) -> Richtung:

        def abbiegen_erdenken() -> Richtung:
            if self.aktuelle_richtung.ist_horizontal:
                if self.abstand(Richtung.Oben) > self.abstand(Richtung.Unten):
                    return Richtung.Oben
                else:
                    return Richtung.Unten
            elif self.aktuelle_richtung.ist_vertikal:
                if self.abstand(Richtung.Links) > self.abstand(Richtung.Rechts):
                    return Richtung.Links
                else:
                    return Richtung.Rechts
            else:
                return Richtung.zufall(ausser=self.aktuelle_richtung)
        if self.verbleibend > 0:
            self.verbleibend -= 1
            return self.aktuelle_richtung
        if lz == lz.Frei:
            self.komisch = 0
            self.verbleibend = 0

        if lz == lz.ist_blockiert or lz == lz.Besucht:
            self.komisch += 1
            if self.komisch > 5:
                self.verbleibend = 5
            else:
                self.aktuelle_richtung = abbiegen_erdenken()

        return self.aktuelle_richtung

class WenigerZufall_Lite(Algorithmus):
    def __init__(self):
        super().__init__()
        self.aktuelle_richtung = Richtung.zufall()
        self.count = 0
        self.verschwendung = 0

    def _bereite_vor(self):
        pass

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if letzter_zustand == FeldZustand.Besucht:
            self.verschwendung += 1

        if self.verschwendung >= 3:
            self.aktuelle_richtung.zufall(ausser=(self.aktuelle_richtung, self.aktuelle_richtung.gegenteil))
            self.count = 0
            self.verschwendung = 0
            return self.aktuelle_richtung

        if self.count >= 30:
            self.aktuelle_richtung = Richtung.zufall()
            self.count = 0
        else:
            self.count += 1

        if letzter_zustand.ist_blockiert:
            self.aktuelle_richtung = Richtung.zufall(ausser=(self.aktuelle_richtung))

        return self.aktuelle_richtung

class Quadrater(Algorithmus):

    def __init__(self):
        super().__init__("Felix: Quadrater")

        self.pending = []
        self.verschwendung = 0
    def _bereite_vor(self):
        self.verschwendergrenze = 2
    def _gib_richtung(self, lz: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if lz == lz.Besucht:
            self.verschwendung += 1
        if zug_nummer > self.arena.punkte_maximum /2:
            self.verschwendergrenze = 5
        if self.verschwendung >= self.verschwendergrenze:
            self.pending = []
            self.verschwendung = 0
            return self.richtung.zufall(ausser=[self.richtung, self.richtung.gegenteil])

        if len(self.pending) > 0:
            return self.pending.pop()

        if lz == lz.Frei:
            return self.richtung

        if lz.ist_blockiert:
            return self.richtung.drehe_nach_rechts()

