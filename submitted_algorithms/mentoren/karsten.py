from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class KarstensAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__()
        self.len = 1
        self.steps = 0
        self.turnLeft = True

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if letzter_zustand.ist_blockiert:
            self.len = 1
            self.steps = 0
        elif self.steps < self.len:
            self.steps += 1
            return self.richtung
        self.steps = 0
        self.len += 1
        return self.richtung.drehe_nach_links()


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui
    start_gui([__name__])