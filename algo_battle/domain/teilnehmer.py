import time
from threading import Thread

from algo_battle.domain import Richtung
from algo_battle.domain.algorithmus import Algorithmus


class TeilnehmerInfos:

    def __init__(self, teilnehmer_snapshot: "TeilnehmerSnapshot", punkte: int, zuege: int):
        self._teilnehmer_snapshot = teilnehmer_snapshot
        self._punkte = punkte
        self._zuege = zuege

    @property
    def snapshot(self) -> "TeilnehmerSnapshot":
        return self._teilnehmer_snapshot

    @property
    def nummer(self) -> int:
        return self._teilnehmer_snapshot.nummer

    @property
    def richtung(self) -> Richtung:
        return self._teilnehmer_snapshot.richtung

    @property
    def x(self) -> int:
        return self._teilnehmer_snapshot.x

    @property
    def y(self) -> int:
        return self._teilnehmer_snapshot.y

    @property
    def punkte(self) -> int:
        return self._punkte

    @property
    def zuege(self) -> int:
        return self._zuege


class TeilnehmerSnapshot:

    def __init__(self, nummer: int, x: int, y: int, richtung: Richtung):
        self._nummer = nummer
        self._richtung = richtung
        self._x = x
        self._y = y

    @property
    def nummer(self) -> int:
        return self._nummer

    @property
    def richtung(self) -> Richtung:
        return self._richtung

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y


class Teilnehmer:

    def __init__(self, nummer: int, algorithmus: Algorithmus, wettkampf, zug_pause: float):
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
    def snapshot(self) -> TeilnehmerSnapshot:
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