from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class MeinAlgorithmus(Algorithmus):

    def __init__(self):
        super().__init__()

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        # Dieser (sehr dumme) Algorithmus fährt immer nur nach rechts :)
        # Hier sollte dein Algorithmus stehen!
        # WICHTIG: Diese Funktion muss eine Richtung, zurückgeben, z.b Richtung.Unten

        return Richtung.Rechts


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
