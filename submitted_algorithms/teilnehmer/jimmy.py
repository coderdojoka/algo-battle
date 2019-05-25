from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class MeinAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__()
        self.richtungen = [Richtung.Rechts, Richtung.Unten, Richtung.Links,Richtung.Oben]

        self.abstände = [0,0,0,0]
        self.aktuelleRichtung = Richtung.Oben
        self.i = 0
        self.mitte = 0
        self.rückweg = 0
        self.anzahl_trennstriche = 0
        self.hinweg = 1
        self.anzahl_füllstriche = 0
        self.fertige_viertel = 0



    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if self.anzahl_trennstriche == 4:
            self.phase3(letzter_zustand)
        else:
            if self.mitte == 1:
                self.phase2(letzter_zustand)
            elif self.mitte == 0:
                self.phase1(letzter_zustand)



        if abs(self.abstände[0] - self.abstände[2] )<= 1 and abs(self.abstände[1] - self.abstände[3]) <= 1:
            self.mitte = 1



        return self.aktuelleRichtung

    def phase1(self,letzter_zustand):  #mitte finden
        if letzter_zustand.ist_blockiert:
            self.anzahl_trennstriche= 4
            self.hinweg = 1
            self.anzahl_füllstriche= self.arena.breite/2 - self.abstand(self.aktuelleRichtung)
            self.i = (self.i+2)%4
        else:
            self.abstände = [self.abstand(r) for r in self.richtungen]
            max_abstand = max(self.abstände)
            max_index = self.abstände.index(max_abstand)
            self.aktuelleRichtung = self.richtungen[max_index]

    def phase2(self,letzter_zustand): #zu einer Wand gehen
        if letzter_zustand.ist_blockiert and self.rückweg== 0:
            self.rückweg = 1
            self.aktuelleRichtung = self.richtungen[(self.i + 1) % 4]
            self.i= (self.i + 2) % 4
            self.aktuelleRichtung= self.richtungen[self.i]
        elif self.abstand(self.richtungen[self.i])==self.arena.breite/2 and self.rückweg==1:
            self.i = (self.i +1 )% 4
            self.rückweg = 0
            self.anzahl_trennstriche += 1


        elif letzter_zustand.ist_blockiert and self.rückweg ==1:
            self.aktuelleRichtung = self.richtungen[(self.i + 1) % 4]
        else:
            self.aktuelleRichtung = self.richtungen[self.i]



    def phase3(self,letzter_zustand):
        if self.fertige_viertel == 2:
            self.fertige_viertel = 0
            self.aktuelleRichtung = self.richtungen[(self.i + 1) % 4]
        elif self.anzahl_füllstriche == self.arena.breite/2-2:
            self.fertige_viertel +=1
            self.i = (self.i + 2) % 4
            self.anzahl_füllstriche = 0
            self.hinweg = 1

        elif letzter_zustand.ist_blockiert and self.hinweg == 1:
            self.aktuelleRichtung= self.richtungen[(self.i - 1) % 4]
            self.i = (self.i + 2) % 4

            self.hinweg = 0
            self.anzahl_füllstriche +=1

        elif letzter_zustand == FeldZustand.Belegt and self.hinweg == 0:
            self.aktuelleRichtung = self.richtungen[(self.i - 1) % 4]

        elif self.abstand(self.richtungen[self.i]) == self.arena.breite/2  and self.hinweg == 0:
            self.aktuelleRichtung = self.richtungen[(self.i + 1) % 4]
            self.i = (self.i + 2) % 4
            self.hinweg = 1
            self.anzahl_füllstriche += 1


        else:
            self.aktuelleRichtung = self.richtungen[self.i]


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui
    start_gui([__name__])