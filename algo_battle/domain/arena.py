import numpy as np

from algo_battle.domain import ArenaDefinition, FeldZustand
from algo_battle.domain.teilnehmer import Teilnehmer


class Arena:

    def __init__(self, definition: ArenaDefinition):
        self._definition = definition
        self._felder = np.full(definition.form, -1)

    @property
    def definition(self):
        return self._definition

    @property
    def breite(self) -> int:
        return self.definition.breite

    @property
    def hoehe(self) -> int:
        return self.definition.hoehe

    @property
    def snapshot(self) -> np.ndarray:
        return self._felder.copy()

    def gib_zustand(self, x: int, y: int, teilnehmer: Teilnehmer) -> FeldZustand:
        if not self.ist_in_feld(x, y):
            return FeldZustand.Wand
        else:
            wert = self._felder[x, y]
            if wert == -1:
                return FeldZustand.Frei
            else:
                return FeldZustand.Besucht if wert == teilnehmer.nummer else FeldZustand.Belegt

    def setze_feld(self, teilnehmer: Teilnehmer):
        self._felder[teilnehmer.x, teilnehmer.y] = teilnehmer.nummer

    def ist_in_feld(self, x: int, y: int) -> bool:
        return 0 <= x < self._felder.shape[0] and 0 <= y < self._felder.shape[1]
