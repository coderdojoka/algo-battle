import random
import numpy as np

from typing import Iterable, List, Optional, Tuple
from threading import RLock
from algo_battle.domain import FeldZustand, ArenaDefinition, Richtung
from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain.arena import Arena

from algo_battle.domain.teilnehmer import TeilnehmerInfos, Teilnehmer, TeilnehmerSnapshot

_zug_pause_default = 0.0002


class Wettkampf:

    def __init__(self, anzahl_zuege: int, arena: ArenaDefinition, algorithmen: Iterable[Algorithmus], **kwargs):
        self._anzahl_zuege = anzahl_zuege
        self._aktueller_zug = 0

        self._arena = Arena(arena)
        zug_pause = kwargs.pop("zug_pause", _zug_pause_default)
        self._teilnehmer = [
            Teilnehmer(nummer, algorithmus, self, zug_pause) for nummer, algorithmus in enumerate(algorithmen)
        ]
        self._aufzeichnung = []
        self._zuege_pro_teilnehmer = {teilnehmer: 0 for teilnehmer in self._teilnehmer}
        self._punkte_pro_teilnehmer = {teilnehmer: 0 for teilnehmer in self._teilnehmer}

        self._zug_berechtigung = RLock()

    def start(self):
        if self._aktueller_zug != 0:
            raise ValueError(
                "Der Wettkampf wurde schon gestartet" if self.laeuft_noch else "Der Wettkampf ist beendet"
            )

        with self.zug_berechtigung:
            gemischte_teilnehmer = list(self._teilnehmer)
            random.shuffle(gemischte_teilnehmer)
            for teilnehmer in gemischte_teilnehmer:
                # TODO Smarter Placement
                teilnehmer.x = random.randrange(0, self.arena_definition.breite)
                teilnehmer.y = random.randrange(0, self.arena_definition.hoehe)
                teilnehmer.start()
                self._aufzeichnung.append(ZugSnapshot(teilnehmer, False))

    def warte_auf_ende(self):
        for teilnehmer in self._teilnehmer:
            if teilnehmer.thread.is_alive():
                teilnehmer.thread.join()

    @property
    def anzahl_zuege(self) -> int:
        return self._anzahl_zuege

    @property
    def aktueller_zug(self) -> int:
        return self._aktueller_zug

    @property
    def arena_definition(self) -> ArenaDefinition:
        return self._arena.definition

    @property
    def teilnehmer(self) -> List["Teilnehmer"]:
        return self._teilnehmer

    def wettkampf_snapshot(self, bis_zug: int = None) -> Tuple[np.ndarray, List["TeilnehmerInfos"]]:
        if bis_zug is None or bis_zug < 0 or bis_zug > self.aktueller_zug:
            teilnehmer_infos = [TeilnehmerInfos(tn.snapshot, self._punkte_pro_teilnehmer[tn], self._zuege_pro_teilnehmer[tn]) for tn in self._teilnehmer]
            return self._arena.snapshot, teilnehmer_infos

        anzahl_teilnehmer = len(self._teilnehmer)
        punkte_pro_teilnehmer = {tn.nummer: 0 for tn in self.teilnehmer}
        zuege_pro_teilnehmer = {tn.nummer: 0 for tn in self.teilnehmer}
        teilnehmer_snapshots = [zug.teilnehmer_snapshot for zug in self._aufzeichnung[:anzahl_teilnehmer]]
        arena_snapshot = np.full(self.arena_definition.form, -1)
        for zug_snapshot in self._aufzeichnung[anzahl_teilnehmer:anzahl_teilnehmer + bis_zug]:
            teilnehmer_nummer = zug_snapshot.teilnehmer_nummer
            teilnehmer_snapshots[teilnehmer_nummer] = zug_snapshot.teilnehmer_snapshot
            zuege_pro_teilnehmer[teilnehmer_nummer] += 1
            if zug_snapshot.gab_punkt:
                arena_snapshot[zug_snapshot.x, zug_snapshot.y] = teilnehmer_nummer
                punkte_pro_teilnehmer[teilnehmer_nummer] += 1
        return arena_snapshot, [TeilnehmerInfos(tn, punkte_pro_teilnehmer[tn.nummer], zuege_pro_teilnehmer[tn.nummer]) for tn in teilnehmer_snapshots]

    @property
    def sieger(self) -> Optional["Teilnehmer"]:
        if self.laeuft_noch:
            return None

        punkte_liste = list(self._punkte_pro_teilnehmer.values())
        if all(p == punkte_liste[0] for p in punkte_liste):
            return Gleichstand
        else:
            return max(self._punkte_pro_teilnehmer.keys(), key=lambda t: self._punkte_pro_teilnehmer[t])

    def zuege_von(self, teilnehmer: "Teilnehmer", bis_zug: int = None) -> int:
        if bis_zug is None or bis_zug < 0 or bis_zug > self.aktueller_zug:
            return self._zuege_pro_teilnehmer[teilnehmer]

        anzahl_teilnehmer = len(self._teilnehmer)
        zuege = 0
        for zug_snapshot in self._aufzeichnung[anzahl_teilnehmer:anzahl_teilnehmer + bis_zug]:
            if zug_snapshot.teilnehmer_nummer == teilnehmer.nummer:
                zuege += 1
        return zuege

    def punkte_von(self, teilnehmer: "Teilnehmer", bis_zug: int = None) -> int:
        if bis_zug is None or bis_zug < 0 or bis_zug > self.aktueller_zug:
            return self._punkte_pro_teilnehmer[teilnehmer]

        anzahl_teilnehmer = len(self._teilnehmer)
        punkte = 0
        for zug_snapshot in self._aufzeichnung[anzahl_teilnehmer:anzahl_teilnehmer + bis_zug]:
            if zug_snapshot.gab_punkt and zug_snapshot.teilnehmer_nummer == teilnehmer.nummer:
                punkte += 1
        return punkte

    def berechne_punkte_neu(self):
        felder = self._arena.snapshot
        felder_pro_wert = {t.nummer: 0 for t in self.teilnehmer}
        for feld in np.nditer(felder):
            wert = int(feld)
            if wert >= 0:
                felder_pro_wert[wert] += 1

        for teilnehmer in self.teilnehmer:
            nummer = teilnehmer.nummer
            punkte = felder_pro_wert.get(nummer, 0)
            self._punkte_pro_teilnehmer[teilnehmer] = punkte

    @property
    def laeuft_noch(self) -> bool:
        return self.aktueller_zug < self.anzahl_zuege

    @property
    def zug_berechtigung(self) -> RLock:
        return self._zug_berechtigung

    def bewege_teilnehmer(self, teilnehmer: "Teilnehmer") -> FeldZustand:
        if not self.laeuft_noch:
            raise ValueError("Der Wettkampf ist beendet")

        with self.zug_berechtigung:
            x_neu = teilnehmer.x + teilnehmer.richtung.dx
            y_neu = teilnehmer.y + teilnehmer.richtung.dy

            gab_punkt = False
            zustand = self._arena.gib_zustand(x_neu, y_neu, teilnehmer)
            if zustand.ist_betretbar:
                teilnehmer.x = x_neu
                teilnehmer.y = y_neu
                if zustand is FeldZustand.Frei:
                    self._arena.setze_feld(teilnehmer)
                    self._punkte_pro_teilnehmer[teilnehmer] += 1
                    gab_punkt = True

            self._aufzeichnung.append(ZugSnapshot(teilnehmer, gab_punkt))
            self._aktueller_zug += 1
            self._zuege_pro_teilnehmer[teilnehmer] += 1

            return zustand


# TODO Use dataclasses for Snapshots?
class ZugSnapshot:

    def __init__(self, teilnehmer: "Teilnehmer", gab_punkt: bool):
        self._teilnehmer_snapshot = teilnehmer.snapshot
        self._gab_punkt = gab_punkt

    @property
    def teilnehmer_snapshot(self) -> TeilnehmerSnapshot:
        return self._teilnehmer_snapshot

    @property
    def teilnehmer_nummer(self) -> int:
        return self._teilnehmer_snapshot.nummer

    @property
    def teilnehmer_richtung(self) -> Richtung:
        return self._teilnehmer_snapshot.richtung

    @property
    def x(self) -> int:
        return self._teilnehmer_snapshot.x

    @property
    def y(self) -> int:
        return self._teilnehmer_snapshot.y

    @property
    def gab_punkt(self) -> bool:
        return self._gab_punkt


class GleichstandDummy(Teilnehmer):

    # noinspection PyTypeChecker
    def __init__(self):
        super().__init__(-1, None, None, -1)

    @property
    def name(self):
        return "Gleichstand"

    @property
    def richtung(self):
        return None

    @property
    def x(self) -> int:
        return -1

    @property
    def y(self) -> int:
        return -1

    def start(self):
        pass

    def _run(self):
        pass


Gleichstand = GleichstandDummy()
