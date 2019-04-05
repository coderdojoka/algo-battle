from typing import Tuple, List, Optional

import pandas as pd

from algo_battle.domain.wettkampf import Wettkampf


class EventStatistiken:

    def __init__(self):
        self._daten = pd.DataFrame()

    @property
    def daten(self) -> pd.DataFrame:
        return self._daten

    @property
    def anzahl_runden(self) -> int:
        return self._daten.shape[0]

    def speicher_runde(self, wettkampf: Wettkampf, runde=-1):
        sieger = wettkampf.sieger
        rohdaten = {}
        for teilnehmer in wettkampf.teilnehmer:
            nummer = teilnehmer.nummer + 1
            name = teilnehmer.name
            rohdaten[(nummer, name, "Züge")] = wettkampf.zuege_von(teilnehmer)
            rohdaten[(nummer, name, "Punkte")] = wettkampf.punkte_von(teilnehmer)
            rohdaten[(nummer, name, "Siege")] = teilnehmer is sieger

        if runde < 0:
            runde = self._daten.shape[0]
        runden_daten = pd.DataFrame(rohdaten, index=[runde])
        runden_daten.index.name = "Runde"
        runden_daten.columns.names = ["Nummer", "Name", "Statistik"]

        self._daten = self._daten.append(runden_daten)

    @property
    def sieger(self) -> Tuple[List[Tuple[int, str]], int]:
        siege = self.siege_summe
        max_siege = siege.max()
        return siege[siege == max_siege].index.to_list(), max_siege

    def sieger_von_runde(self, runde: int) -> Optional[Tuple[str, int]]:
        if runde not in self._daten.index:
            return None

        siege = self._daten.xs("Siege", axis="columns", level=2, drop_level=True)
        for teilnehmer, gewonnen in siege.loc[runde].iteritems():
            if gewonnen:
                return teilnehmer
        return None

    @property
    def ist_gleichstand(self) -> bool:
        return len(self.sieger[0]) == self._daten.columns.unique(0).size

    @property
    def siege_summe(self) -> pd.Series:
        return self._daten.xs("Siege", axis="columns", level=2, drop_level=True).sum()

    @property
    def zuege_durchschnitt(self) -> pd.Series:
        return self._daten.xs("Züge", axis="columns", level=2, drop_level=True).mean()

    @property
    def punkte_durchschnitt(self) -> pd.Series:
        return self._daten.xs("Punkte", axis="columns", level=2, drop_level=True).mean()

    @property
    def zusammenfassung(self) -> str:
        zuege_nachricht = "Durchschnittliche Züge: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, zuege) for (nummer, name), zuege in self.zuege_durchschnitt.iteritems()
        ))
        punkte_nachricht = "Durchschnittliche Punkte: {}".format(" | ".join(
            "[{}] {}: {:.2f}".format(nummer, name, punkte) for (nummer, name), punkte in self.punkte_durchschnitt.iteritems()
        ))
        return "Zusammenfassung: {}\n{}\n{}".format(
            self.sieger_nachricht, zuege_nachricht, punkte_nachricht
        )

    @property
    def sieger_nachricht(self) -> str:
        sieger, anzahl_siege = self.sieger
        if self.ist_gleichstand:
            sieger_nachricht = "Gleichstand! Alle Teilnehmer haben {} Runde{} gewonnen.".format(
                anzahl_siege, "n" if anzahl_siege > 1 else ""
            )
        else:
            anzahl_runden = self._daten.shape[0]
            sieger_formatiert = ["[{}] {}".format(*t) for t in sieger]
            if len(sieger_formatiert) > 1:
                sieger_aufzaehlung = " und ".join((", ".join(sieger_formatiert[:-1]), sieger_formatiert[-1]))
            else:
                sieger_aufzaehlung = sieger_formatiert[-1]
            sieger_nachricht = "Teilnehmer {} gewinn{} mit {} von {} Sieg{}!".format(
                sieger_aufzaehlung, "en" if len(sieger) > 1 else "t", anzahl_siege, anzahl_runden, "en" if anzahl_runden > 1 else ""
            )
        return sieger_nachricht
