from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung


class HDAS_Algorythmus(Algorithmus):

    zahl = 0

    def __init__(self):
        super().__init__("Leon")
        
    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        # Dieser (sehr dumme) Algorithmus fährt immer nur nach rechts :)
        # Hier sollte dein Algorithmus stehen!
        # WICHTIG: Diese Funktion muss eine Richtung, zurückgeben, z.b Richtung.Unten
       
        self.zahl = self.zahl + 1
       
        if self.zahl>500:
            return Richtung.zufall()
       
        if letzter_zustand.ist_blockiert:
            return Richtung.zufall()
        if letzter_zustand.ist_blockiert:
            return Richtung.Unten()
        
if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
