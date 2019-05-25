from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class Diagoliner(Algorithmus):
    def __init__(self):
        super().__init__("David: Diagoliner")

    moveCounter = 0
    wasteCounter = 0
    straightMoves = 0
    turnLeftFirst = 0
    direction = Richtung.Oben

    def moveDiagonal(self):
        if self.moveCounter % 2 == self.turnLeftFirst:
            self.direction = self.direction.drehe_nach_rechts()
        else:
            self.direction = self.direction.drehe_nach_links()
    
    def moveStraight(self):
        self.direction = self.direction
        self.straightMoves -= 1

    def moveAround(self):
        self.direction = Richtung.zufall(ausser=[self.richtung, self.richtung.gegenteil])
        self.straightMoves = 1

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if self.moveCounter == 0:
            if self.abstand(Richtung.Oben) < 50:
                self.direction = Richtung.Unten
            if self.abstand(Richtung.Rechts) < 50:
                self.turnLeftFirst = 1
        
        if letzter_zustand.ist_betretbar: # Frei oder Besucht
            if letzter_zustand == FeldZustand.Besucht:
                self.wasteCounter += 1
                if self.wasteCounter >= 2:
                    self.straightMoves = 3
            if self.straightMoves > 0:
                self.moveStraight()
            else:
                self.moveDiagonal()
        else: # Wand oder Belegt
            self.moveAround()

        self.moveCounter += 1
        return self.direction

class Boxer(Algorithmus):
    def __init__(self):
        super().__init__("David: Boxer")

    moveCounter = 0
    edgeCounter = 1
    cornerCounter = 1
    currentSize = 2
    direction = Richtung.Oben

    def moveStraight(self):
        self.direction = self.direction
        self.edgeCounter += 1

    def moveClockwise(self):
        self.direction = self.direction.drehe_nach_rechts()
        self.edgeCounter = 2
        self.cornerCounter += 1

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if self.edgeCounter < self.currentSize or self.cornerCounter == 3:
            self.moveStraight()
            if self.cornerCounter == 3:
                self.currentSize += 2
                self.cornerCounter = 1
                # self.edgeCounter = self.currentSize
        else:
            self.moveClockwise()

        self.moveCounter += 1
        return self.direction

if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
