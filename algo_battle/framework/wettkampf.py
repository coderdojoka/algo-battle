import time
import numpy as np
import random

from typing import Iterable, List, Optional, Tuple
from threading import Thread, RLock

import pandas as pd

from framework.domain import ArenaDefinition, FeldZustand, Richtung
from framework.algorithm import Algorithmus

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

    @property
    def wettkampf_snapshot(self) -> Tuple[np.ndarray, List["TeilnehmerSnapshot"]]:
        teilnehmer_snapshots = [tn.snapshot for tn in self._teilnehmer]
        return self._arena.snapshot, teilnehmer_snapshots

    @property
    def sieger(self) -> Optional["Teilnehmer"]:
        if self.laeuft_noch:
            return None

        punkte_liste = list(self._punkte_pro_teilnehmer.values())
        if all(p == punkte_liste[0] for p in punkte_liste):
            return Gleichstand
        else:
            return max(self._punkte_pro_teilnehmer.keys(), key=lambda t: self._punkte_pro_teilnehmer[t])

    def zuege_von(self, teilnehmer: "Teilnehmer") -> int:
        return self._zuege_pro_teilnehmer[teilnehmer]

    def punkte_von(self, teilnehmer: "Teilnehmer") -> int:
        return self._punkte_pro_teilnehmer[teilnehmer]

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

    # ------------- Geschützter Bereich -----------------------------------------------------------

    @property
    def zug_berechtigung(self) -> RLock:
        return self._zug_berechtigung

    def bewege_teilnehmer(self, teilnehmer: "Teilnehmer") -> FeldZustand:
        if not self.laeuft_noch:
            raise ValueError("Der Wettkampf ist beendet")

        with self.zug_berechtigung:
            x_neu = teilnehmer.x + teilnehmer.richtung.dx
            y_neu = teilnehmer.y + teilnehmer.richtung.dy

            zustand = self._arena.gib_zustand(x_neu, y_neu, teilnehmer)
            if zustand.ist_betretbar:
                teilnehmer.x = x_neu
                teilnehmer.y = y_neu
                if zustand is FeldZustand.Frei:
                    self._arena.setze_feld(teilnehmer)
                    self._punkte_pro_teilnehmer[teilnehmer] += 1

            self._aktueller_zug += 1
            self._zuege_pro_teilnehmer[teilnehmer] += 1

            return zustand

    # ---------------------------------------------------------------------------------------------


class Teilnehmer:

    def __init__(self, nummer: int, algorithmus: Algorithmus, wettkampf: Wettkampf, zug_pause: float):
        self._nummer = nummer
        self._algorithmus = algorithmus
        self._wettkampf = wettkampf
        self._zug_pause = zug_pause

        self._thread = None
        self._x = -1
        self._y = -1

    @property
    def nummer(self):
        return self._nummer

    @property
    def name(self):
        return self._algorithmus.name

    @property
    def richtung(self):
        return self._algorithmus.richtung

    @property
    def thread(self):
        return self._thread

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    @property
    def snapshot(self) -> "TeilnehmerSnapshot":
        return TeilnehmerSnapshot(self.nummer, self.x, self.y, self.richtung)

    def start(self):
        self._thread = Thread(name=self.name, target=self._run, daemon=True)
        self._algorithmus.arena = self._wettkampf.arena_definition
        self._algorithmus.start(self.x, self.y)
        self._thread.start()

    def _run(self):
        zustand = None
        while self._wettkampf.laeuft_noch:
            if zustand:
                # Hole aktuelle Informationen
                with self._wettkampf.zug_berechtigung:
                    zug_nummer = self._wettkampf.aktueller_zug
                    aktuelle_punkte = self._wettkampf.punkte_von(self)
                # Plane nächsten Schritt (außerhalb der zug_berechtigung, um Wettkampf nicht zu blockieren)
                self._algorithmus.aktualisiere(self.x, self.y, zustand, zug_nummer, aktuelle_punkte)

            # Führe geplanten Schritt aus
            if self._wettkampf.laeuft_noch:
                zustand = self._wettkampf.bewege_teilnehmer(self)

            time.sleep(self._zug_pause)

    def __repr__(self):
        return "{klasse}[nummer={nummer}, name={name}, position=({x},{y}), richtung={richtung}]".format(
            klasse=self.__class__.__name__,
            nummer=self.nummer,
            name=self.name,
            x=self.x,
            y=self.y,
            richtung=self.richtung
        )

    def __str__(self):
        return "[{}] {}".format(self.nummer + 1, self.name)


class TeilnehmerSnapshot:

    def __init__(self, nummer: int, x: int, y: int, richtung: Richtung):
        self.nummer = nummer
        self.richtung = richtung
        self.x = x
        self.y = y


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


class EventStatistiken:

    def __init__(self):
        self._daten = pd.DataFrame()

    @property
    def daten(self) -> pd.DataFrame:
        return self._daten

    def speicher_runde(self, wettkampf: Wettkampf, runde=-1):
        sieger = wettkampf.sieger
        rohdaten = {}
        for teilnehmer in wettkampf.teilnehmer:
            nummer = teilnehmer.nummer + 1
            name = teilnehmer.name
            rohdaten[(nummer, name, "Züge")] = wettkampf.zuege_von(teilnehmer)
            rohdaten[(nummer, name, "Punkte")] = wettkampf.punkte_von(teilnehmer)
            rohdaten[(nummer, name, "Siege")] = 1 if teilnehmer is sieger else 0

        if runde < 0:
            runde = self._daten.shape[0]
        runden_daten = pd.DataFrame(rohdaten, index=[runde])
        runden_daten.index.name = "Runde"
        runden_daten.columns.names = ["Nummer", "Name", "Statistik"]

        self._daten = self._daten.append(runden_daten)

    @property
    def zusammenfassung(self) -> str:
        siege = self._daten.xs("Siege", axis="columns", level=2, drop_level=True).sum()
        max_siege = siege.max()
        gewinner = siege[siege == max_siege].index
        if len(siege) == len(gewinner):
            gewinner_nachricht = "Gleichstand! Alle Teilnehmer haben {} Runde{} gewonnen.".format(
                max_siege, "n" if max_siege > 1 else ""
            )
        else:
            gewinner_nachricht = "Teilnehmer {} gewinn{} mit {} Sieg{}!".format(
                ", ".join("[{}] {}".format(t[0], t[1]) for t in gewinner),
                "en" if len(gewinner) > 1 else "t", max_siege, "en" if max_siege > 1 else ""
            )

        zuege_durchschnitt = self._daten.xs("Züge", axis="columns", level=2, drop_level=True).mean()
        zuege_nachricht = "Durchschnittliche Züge: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, zuege) for (nummer, name), zuege in zuege_durchschnitt.iteritems()
        ))

        punkte_durchschnitt = self._daten.xs("Punkte", axis="columns", level=2, drop_level=True).mean()
        punkte_nachricht = "Durchschnittliche Punkte: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, punkte) for (nummer, name), punkte in punkte_durchschnitt.iteritems()
        ))

        return "Zusammenfassung: {}\n{}\n{}".format(
            gewinner_nachricht, zuege_nachricht, punkte_nachricht
        )