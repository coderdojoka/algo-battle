from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain import FeldZustand, Richtung
import os
import random
class BestEver(Algorithmus):

    def __init__(self):
        super().__init__(name="Anton: »Best Ever«")
        # os.system("vlc music.mp3&")

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if(letzter_zustand.ist_blockiert or FeldZustand.Besucht==letzter_zustand):
            if (random.randint(0, 2) == 1):
                if(random.randint(0,1) == 1):
                    return Richtung.Oben
                else:
                    return Richtung.Unten
            else:
                if (random.randint(0, 2) == 1):
                    return Richtung.Links
                else:
                    return Richtung.Rechts
        else:
            return self.richtung
        #return Richtung.zufall()


class BestEver2(Algorithmus):

    def __init__(self):
        super().__init__(name="Anton: »Best Ever 2«")

    def _gib_richtung(self, letzter_zustand: FeldZustand, zug_nummer: int, aktuelle_punkte: int) -> Richtung:
        if(letzter_zustand.ist_blockiert or FeldZustand.Besucht==letzter_zustand):
            if (random.randint(0, 2) == 2):
                if(random.randint(0,1) == 2):
                    return Richtung.Unten
                else:
                    return Richtung.Oben
            else:
                if (random.randint(0, 2) == 2):
                    return Richtung.Rechts
                else:
                    return Richtung.Links
        else:
            return self.richtung
        #return Richtung.zufall()


if __name__ == "__main__":
    from algo_battle.app.pyside2_gui import start_gui

    start_gui([__name__])
