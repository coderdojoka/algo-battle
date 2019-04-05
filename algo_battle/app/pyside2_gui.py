import os
import logging
import math
import sys
import random
import numpy as np
import algo_battle.util

from typing import Optional, Iterable, Tuple, Type, Union, List
from PySide2 import QtWidgets as widgets, QtCore as core, QtGui as gui

from algo_battle.util import builtin_algorithmen
from algo_battle.domain import ArenaDefinition
from algo_battle.domain.algorithmus import Algorithmus
from algo_battle.domain.wettkampf import Wettkampf, Gleichstand
from algo_battle.domain.teilnehmer import TeilnehmerInfos, Teilnehmer
from algo_battle.domain.util import EventStatistiken


_font_size = 12
_initial_width = 900
_initial_height = 900

_min_teilnehmer_anzahl = 2
_max_teilnehmer_anzahl = 10
_min_arena_groesse = 75
_max_arena_groesse = 300

_verfuegbare_algorithmen = []


_farben = [
    [gui.QColor(33, 119, 177), gui.QColor(78, 121, 165)],  # Blau
    [gui.QColor(254, 128, 42), gui.QColor(241, 143, 59)],  # Orange
    [gui.QColor(48, 160, 57), gui.QColor(90, 161, 85)],  # Grün
    [gui.QColor(213, 42, 45), gui.QColor(224, 88, 91)],  # Rot
    [gui.QColor(147, 103, 186), gui.QColor(175, 122, 160)],  # Lila
    [gui.QColor(140, 86, 76), gui.QColor(156, 117, 97)],  # Braun
    [gui.QColor(226, 120, 192), gui.QColor(254, 158, 168)],  # Rosa
    [gui.QColor(127, 127, 127), gui.QColor(186, 176, 172)],  # Grau
    [gui.QColor(224, 224, 60), gui.QColor(237, 201, 88)],  # Gelb
    [gui.QColor(31, 190, 205), gui.QColor(119, 183, 178)],  # Türkis
]


def start_gui(module: Iterable[str] = None):
    if module:
        for modul_pfad in module:
            _verfuegbare_algorithmen.extend(algo_battle.util.gib_algorithmen_in_modul(modul_pfad))
    _verfuegbare_algorithmen.extend(algo_battle.util.gib_algorithmen_in_modul(builtin_algorithmen))

    app = widgets.QApplication()
    font = app.font()
    font.setPointSize(_font_size)
    app.setFont(font)

    main_view = MainView()
    main_view.setWindowTitle("Algo-Battle")
    main_view.setGeometry(0, 0, _initial_width, _initial_height)
    main_view.move(widgets.QApplication.desktop().rect().center() - main_view.rect().center())
    main_view.show()
    sys.exit(app.exec_())


def logger() -> logging.Logger:
    return logging.getLogger("GUI")


class MainView(widgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self._toolbar = self.addToolBar("Status")
        self._toolbar.setFloatable(False)
        self._toolbar.setMovable(False)
        self._status_bar = widgets.QStatusBar()
        self._status_bar_widgets = []
        self._toolbar.addWidget(self._status_bar)

        self._erstelle_wettkampf = ErstelleWettkampfView(self)
        size_policy = widgets.QSizePolicy(widgets.QSizePolicy.Minimum, widgets.QSizePolicy.Minimum)
        self._erstelle_wettkampf.setSizePolicy(size_policy)
        self._erstelle_wettkampf.start_knopf.clicked.connect(self.starte_wettkampf)

        self._algorithmen = []
        self._statistiken = EventStatistiken()
        self._wettkampf_view = WettkampfView(self)
        self._neue_runde_button = widgets.QPushButton("Nächste Runde")
        self._neue_runde_button.clicked.connect(self._neue_runde)
        self._speicher_bild_button = widgets.QPushButton("Bild speichern")
        self._speicher_bild_button.clicked.connect(self._speicher_wettkampf_bild)
        self._zeige_statistiken_button = widgets.QPushButton("Statistiken")
        self._zeige_statistiken_button.clicked.connect(self._zeige_event_statistiken)
        self._neuer_wettkampf_button = widgets.QPushButton("Neuer Wettkampf")
        self._neuer_wettkampf_button.clicked.connect(self._neuer_wettkampf)

        self._content_widget = widgets.QStackedWidget()
        self._content_widget.addWidget(self._erstelle_wettkampf)
        self._content_widget.addWidget(self._wettkampf_view)

        if not _verfuegbare_algorithmen:
            self._status_bar.showMessage("Es konnten keine Algorithmen gefunden werden.")
        else:
            self.setCentralWidget(self._content_widget)

    def starte_wettkampf(self):
        if self._erstelle_wettkampf.is_valid:
            if not self._algorithmen:
                self._algorithmen = [algorithmus if algorithmus else random.choice(_verfuegbare_algorithmen)
                                     for algorithmus in self._erstelle_wettkampf.algorithmen]
            self._wettkampf_view.starte_wettkampf(
                self._erstelle_wettkampf.arena_groesse,
                self._algorithmen,
                self._erstelle_wettkampf.zuege_pro_sekunde,
                self._statistiken.anzahl_runden + 1
            )
            self._content_widget.setCurrentIndex(self._content_widget.indexOf(self._wettkampf_view))
            self.window().resize(self.minimumSizeHint())

    def wettkampf_beendet(self):
        wettkampf = self._wettkampf_view.wettkampf
        self._statistiken.speicher_runde(wettkampf)

        sieger = wettkampf.sieger
        if sieger is Gleichstand:
            ergebnis_nachricht = "Gleichstand! Es gibt keinen Gewinner."
        else:
            ergebnis_nachricht = "Teilnehmer {} gewinnt!".format(sieger)

        ergebnis_label = widgets.QLabel(ergebnis_nachricht)
        self.zeige_status_widget(ergebnis_label)
        spacer_label1 = widgets.QLabel("")
        self.zeige_status_widget(spacer_label1, stretch=1)
        self.zeige_status_widget(self._neue_runde_button)
        self.zeige_status_widget(self._speicher_bild_button)
        self.zeige_status_widget(self._zeige_statistiken_button)
        spacer_label2 = widgets.QLabel("")
        self.zeige_status_widget(spacer_label2, stretch=1)
        self.zeige_status_widget(self._neuer_wettkampf_button)

    def zeige_status_nachricht(self, nachricht: str):
        self._status_bar.showMessage(nachricht)

    def zeige_status_widget(self, widget: widgets.QWidget, stretch=0):
        self._status_bar.addPermanentWidget(widget, stretch)
        widget.show()
        self._status_bar_widgets.append(widget)

    def clear_status_bar(self):
        self._status_bar.clearMessage()
        for widget in self._status_bar_widgets:
            self._status_bar.removeWidget(widget)
            if isinstance(widget, widgets.QLabel):
                widget.deleteLater()
        self._status_bar_widgets.clear()

    def _neue_runde(self):
        self.clear_status_bar()
        self.starte_wettkampf()

    def _speicher_wettkampf_bild(self):
        os.makedirs("Bilder", exist_ok=True)
        datei_typen = ["png", "jpg", "jpeg"]
        datei_pfad = widgets.QFileDialog.getSaveFileName(self, "Bild speichern", "Bilder", "Bilder ({})".format(
            " ".join("*.{}".format(typ) for typ in datei_typen)
        ))
        datei_pfad = datei_pfad[0]
        if datei_pfad:
            if datei_pfad.lower().split(".")[-1] not in datei_typen:
                datei_pfad = "{}.png".format(datei_pfad)
            self._wettkampf_view.grab().save(datei_pfad, quality=95)

    def _zeige_event_statistiken(self):
        dialog = widgets.QDialog()
        dialog.setWindowTitle("Statistiken")
        dialog.setWindowFlags(dialog.windowFlags() & ~core.Qt.WindowContextHelpButtonHint)
        dialog_layout = widgets.QVBoxLayout()
        dialog.setLayout(dialog_layout)
        dialog_layout.addWidget(EventStatistikView(self._statistiken))
        dialog.layout().setSizeConstraint(widgets.QLayout.SetFixedSize)
        dialog.exec_()

    def _neuer_wettkampf(self):
        self.clear_status_bar()
        self._algorithmen.clear()
        self._statistiken = EventStatistiken()
        self._content_widget.setCurrentIndex(self._content_widget.indexOf(self._erstelle_wettkampf))


class ErstelleWettkampfView(widgets.QWidget):

    def __init__(self, main_view: MainView):
        super().__init__()
        self._main_view = main_view

        self._anzahl_teilnehmer = widgets.QLineEdit("2")
        self._anzahl_teilnehmer.setFixedWidth(100)
        self._anzahl_teilnehmer.setValidator(gui.QIntValidator(_min_teilnehmer_anzahl, _max_teilnehmer_anzahl))
        self._anzahl_teilnehmer.textChanged.connect(self._teilnehmer_anzahl_geaendert)

        self._arena_breite = widgets.QLineEdit("100")
        self._arena_breite.setFixedWidth(50)
        self._arena_breite.setValidator(gui.QIntValidator(_min_arena_groesse, _max_arena_groesse))
        self._arena_breite.setAlignment(core.Qt.AlignRight)
        self._arena_breite.textChanged.connect(self._eingaben_geaendert)

        self._arena_hoehe = widgets.QLineEdit("100")
        self._arena_hoehe.setFixedWidth(50)
        self._arena_hoehe.setValidator(gui.QIntValidator(_min_arena_groesse, _max_arena_groesse))
        self._arena_hoehe.textChanged.connect(self._eingaben_geaendert)

        self._geschwindigkeit = widgets.QComboBox()
        self._geschwindigkeit.setEditable(False)
        self._geschwindigkeit.addItem("Echtzeit", 100000)
        self._geschwindigkeit.addItem("Schnell", 1000)
        self._geschwindigkeit.addItem("Normal", 500)
        self._geschwindigkeit.addItem("Langsam", 250)
        self._geschwindigkeit.addItem("Sehr Langsam", 100)
        self._geschwindigkeit.setCurrentText("Normal")
        for index in range(self._geschwindigkeit.count()):
            zuege_pro_sekunde = self._geschwindigkeit.itemData(index)
            tooltip = "{} Züge pro Sekunde".format(
                zuege_pro_sekunde if self._geschwindigkeit.itemText(index) != "Echtzeit" else "∞"
            )
            self._geschwindigkeit.setItemData(index, tooltip, core.Qt.ToolTipRole)

        self._algorithmen = []
        self._algorithmus_label = []
        self._algorithmus_felder = []

        self._start_knopf = widgets.QPushButton("Start")
        self._start_knopf.setFixedWidth(200)
        self._start_knopf_spacer = widgets.QSpacerItem(1, 20)
        self._bottom_spacer = widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Minimum, widgets.QSizePolicy.Expanding)

        self._layout = widgets.QGridLayout()
        self.setLayout(self._layout)

        self._layout.addItem(widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Expanding, widgets.QSizePolicy.Minimum), 0, self._layout.columnCount())
        self._layout.addWidget(widgets.QLabel("Anzahl Teilnehmer"), 0, self._layout.columnCount(), core.Qt.AlignRight)
        self._layout.addWidget(self._anzahl_teilnehmer, 0, self._layout.columnCount(), core.Qt.AlignLeft)
        self._layout.addItem(widgets.QSpacerItem(20, 1), 0, self._layout.columnCount())

        self._layout.addWidget(widgets.QLabel("Arena Größe"), 0, self._layout.columnCount())
        self._layout.addWidget(self._arena_breite, 0, self._layout.columnCount())
        self._layout.addWidget(widgets.QLabel("x"), 0, self._layout.columnCount())
        self._layout.addWidget(self._arena_hoehe, 0, self._layout.columnCount())
        self._layout.addItem(widgets.QSpacerItem(20, 1), 0, self._layout.columnCount())

        self._layout.addWidget(widgets.QLabel("Geschwindigkeit"), 0, self._layout.columnCount())
        self._layout.addWidget(self._geschwindigkeit, 0, self._layout.columnCount(), core.Qt.AlignLeft)
        self._layout.addItem(widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Expanding, widgets.QSizePolicy.Minimum), 0, self._layout.columnCount())

        self._layout.addItem(widgets.QSpacerItem(1, 10), 1, 0)

        self._teilnehmer_anzahl_geaendert()

    @property
    def start_knopf(self) -> widgets.QPushButton:
        return self._start_knopf

    @property
    def anzahl_teilnehmer(self) -> Optional[int]:
        if not self._anzahl_teilnehmer.hasAcceptableInput():
            return None
        return int(self._anzahl_teilnehmer.text())

    @property
    def arena_groesse(self) -> Optional[Tuple[int, int]]:
        if not self._arena_groesse_valid:
            return None
        return int(self._arena_breite.text()), int(self._arena_hoehe.text())

    @property
    def zuege_pro_sekunde(self) -> int:
        return self._geschwindigkeit.currentData()

    @property
    def algorithmen(self) -> Iterable[Optional[Type[Algorithmus]]]:
        return [feld.currentData() for feld in self._algorithmus_felder]

    @property
    def is_valid(self):
        return self._anzahl_teilnehmer.hasAcceptableInput() and self._arena_groesse_valid

    @property
    def _arena_groesse_valid(self):
        return self._arena_breite.hasAcceptableInput() and self._arena_hoehe.hasAcceptableInput()

    def _eingaben_geaendert(self):
        self._start_knopf.setEnabled(self.is_valid)

        teilnehmer_anzahl_nachricht = ""
        if not self._anzahl_teilnehmer.hasAcceptableInput():
            teilnehmer_anzahl_nachricht = "Die Anzahl der Teilnehmer muss zwischen {} und {} liegen.".format(
                _min_teilnehmer_anzahl, _max_teilnehmer_anzahl
            )
        arena_groesse_nachricht = ""
        if not self._arena_groesse_valid:
            arena_groesse_nachricht = "Die Breite/Höhe der Arena muss zwischen {} und {} liegen.".format(
                _min_arena_groesse, _max_arena_groesse
            )
        self._main_view.zeige_status_nachricht("{}\n{}".format(teilnehmer_anzahl_nachricht, arena_groesse_nachricht))

    def _teilnehmer_anzahl_geaendert(self):
        if not self._anzahl_teilnehmer.hasAcceptableInput():
            self._eingaben_geaendert()
            return

        while len(self._algorithmen) < self.anzahl_teilnehmer:
            self._algorithmen.append(None)

        for index, feld in enumerate(self._algorithmus_felder):
            algorithmus = feld.currentData()
            self._algorithmen[index] = algorithmus
            self._layout.removeWidget(feld)
            feld.deleteLater()
        for label in self._algorithmus_label:
            self._layout.removeWidget(label)
            label.deleteLater()

        self._layout.removeItem(self._start_knopf_spacer)
        self._layout.removeWidget(self._start_knopf)
        self._layout.removeItem(self._bottom_spacer)

        self._algorithmus_felder.clear()
        self._algorithmus_label.clear()
        reihe = self._layout.rowCount()
        for index in range(self.anzahl_teilnehmer):
            algorithmus_feld = self._ersetelle_algorithmus_feld()
            vorher_ausgewaehlt = algorithmus_feld.findData(self._algorithmen[index])
            if vorher_ausgewaehlt >= 0:
                algorithmus_feld.setCurrentIndex(vorher_ausgewaehlt)
            self._algorithmus_felder.append(algorithmus_feld)

            teilnehmer_farbe = TeilnehmerFarbe(index)
            teilnehmer_label = widgets.QLabel("Teilnehmer {}".format(index + 1))
            self._algorithmus_label.append(teilnehmer_farbe)
            self._algorithmus_label.append(teilnehmer_label)

            algorithmus_auswahl = widgets.QHBoxLayout()
            algorithmus_auswahl.addWidget(teilnehmer_farbe)
            algorithmus_auswahl.addWidget(teilnehmer_label)
            algorithmus_auswahl.addWidget(algorithmus_feld)

            reihe = self._layout.rowCount() + 1
            self._layout.addLayout(algorithmus_auswahl, reihe, 0, 1, -1, core.Qt.AlignHCenter)

        self._layout.addItem(self._start_knopf_spacer, reihe + 1, 0)
        self._layout.addWidget(self._start_knopf, reihe + 2, 0, 1, -1, core.Qt.AlignHCenter)
        self._layout.addItem(self._bottom_spacer, reihe + 3, 0)

        self._eingaben_geaendert()

    @staticmethod
    def _erstelle_algorithmus_label(index: int) -> widgets.QWidget:
        label = widgets.QWidget()
        farbe_und_label_layout = widgets.QHBoxLayout()
        label.setLayout(farbe_und_label_layout)
        farbe_und_label_layout.addWidget(TeilnehmerFarbe(index))
        farbe_und_label_layout.addWidget(widgets.QLabel("Teilnehmer {}".format(index + 1)))
        return label

    @staticmethod
    def _ersetelle_algorithmus_feld() -> widgets.QComboBox:
        algorithmus_feld = widgets.QComboBox()
        algorithmus_feld.setEditable(False)
        algorithmus_feld.addItem("zufälliger Algorithmus", None)
        for algorithmus in _verfuegbare_algorithmen:
            algorithmus_feld.addItem(
                "{}.{}".format(algorithmus.__module__, algorithmus.__name__),
                algorithmus
            )
        return algorithmus_feld


class WettkampfView(widgets.QWidget):

    def __init__(self, main_view: MainView):
        super().__init__()
        self._main_view = main_view
        self._aktueller_zug = 0
        self._zuege_pro_sekunde = 1
        # TODO Change progress bar to timeline and controls (like a video player)?
        self._fortschritts_balken = widgets.QProgressBar()
        self._teilnehmer_status = []
        self._teilnehmer_layout = widgets.QVBoxLayout()
        self._arena_view = None

        self._wettkampf = None
        self._layout = widgets.QHBoxLayout()
        self.setLayout(self._layout)

        self._timer = core.QTimer()
        self._timer.timeout.connect(self._aktualisiere_view)
        self._elapsed_timer = core.QElapsedTimer()

    @property
    def wettkampf(self):
        return self._wettkampf

    def starte_wettkampf(self, arena_groesse: (int, int), algorithmen: Iterable[Type[Algorithmus]], zuege_pro_sekunde: int, runde: int):
        arena_definition = ArenaDefinition(*arena_groesse)
        self._wettkampf = Wettkampf(
            arena_definition.punkte_maximum, arena_definition,
            [algorithmus() for algorithmus in algorithmen]
        )
        self._zuege_pro_sekunde = zuege_pro_sekunde
        self._initialisiere_view(runde)
        self._wettkampf.start()
        self._elapsed_timer.start()
        self._timer.start()

    def _initialisiere_view(self, runde: int):
        for teilnehmer_status in self._teilnehmer_status:
            teilnehmer_status.deleteLater()
            self._teilnehmer_layout.removeWidget(teilnehmer_status)
        self._teilnehmer_status.clear()
        self._teilnehmer_layout.takeAt(0)  # Removing the spacer item

        layout_item = self._layout.takeAt(0)
        while layout_item:
            widget = layout_item.widget()
            if widget:
                widget.deleteLater()
            layout_item = self._layout.takeAt(0)

        runde_label = widgets.QLabel()
        runde_label.setStyleSheet("font-weight: bold;")
        runde_label.setText("Runde {}".format(runde))
        self._main_view.zeige_status_widget(runde_label)

        self._aktueller_zug = 0
        self._fortschritts_balken.setRange(0, self._wettkampf.anzahl_zuege)
        self._fortschritts_balken.setValue(self._aktueller_zug)
        self._fortschritts_balken.setFormat("Züge %v/{}".format(self._wettkampf.anzahl_zuege))
        self._main_view.zeige_status_widget(self._fortschritts_balken, stretch=1)

        scroll_container = widgets.QScrollArea()
        scroll_container.setMinimumWidth(200)
        scroll_container.setContentsMargins(0,0,0,0)
        scroll_container.setWidgetResizable(True)
        scroll_container.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)

        teilnehmer_container = widgets.QWidget()
        teilnehmer_container.setLayout(self._teilnehmer_layout)
        self._teilnehmer_status.extend(None for _ in range(len(self._wettkampf.teilnehmer)))
        for teilnehmer in self._wettkampf.teilnehmer:
            teilnehmer_status = TeilnehmerStatus(teilnehmer)
            self._teilnehmer_status[teilnehmer.nummer] = teilnehmer_status
            self._teilnehmer_layout.addWidget(teilnehmer_status)
        self._teilnehmer_layout.addItem(widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Minimum, widgets.QSizePolicy.Expanding))

        scroll_container.setWidget(teilnehmer_container)
        self._arena_view = ArenaView(self._wettkampf, hat_gitter=True)
        self._layout.addWidget(scroll_container)
        self._layout.addWidget(self._arena_view)

    def _aktualisiere_view(self):
        if self._aktueller_zug >= self._wettkampf.anzahl_zuege:
            self._elapsed_timer.invalidate()
            self._timer.stop()
            self._wettkampf.berechne_punkte_neu()
            self._main_view.clear_status_bar()
            self._main_view.wettkampf_beendet()

        arena_data, teilnehmer_infos = self._wettkampf.wettkampf_snapshot(bis_zug=self._aktueller_zug)
        teilnehmer_infos.sort(key=lambda tn: tn.punkte, reverse=True)

        self._arena_view.aktualisiere_view(arena_data, teilnehmer_infos)
        for rang, teilnehmer in enumerate(teilnehmer_infos):
            teilnehmer_status = self._teilnehmer_status[teilnehmer.nummer]
            teilnehmer_status.aktualisiere_view(teilnehmer)
            self._teilnehmer_layout.insertWidget(rang, teilnehmer_status)

        self._fortschritts_balken.setValue(self._aktueller_zug)
        elapsed_seconds = self._elapsed_timer.elapsed() / 1000
        self._aktueller_zug = min(int(elapsed_seconds * self._zuege_pro_sekunde), self._wettkampf.aktueller_zug)


class TeilnehmerStatus(widgets.QGroupBox):

    def __init__(self, teilnehmer: Teilnehmer):
        super().__init__("{}".format(teilnehmer))
        self._punkte_anzeige = widgets.QLabel()
        self._zuege_anzeige = widgets.QLabel()

        self._layout = widgets.QFormLayout()
        self._layout.setLabelAlignment(core.Qt.AlignRight)
        self._layout.addRow("Punkte:", self._punkte_anzeige)
        self._layout.addRow("Züge:", self._zuege_anzeige)
        self.setLayout(self._layout)
        self.setMinimumWidth(150)
        self.setPalette(gui.QPalette(_farben[teilnehmer.nummer][1].darker(80)))
        self.setAutoFillBackground(True)

        self.setStyleSheet("""
            QGroupBox::title {
                margin-left: 5px;
            }
        """)

    def aktualisiere_view(self, teilnehmer_infos: TeilnehmerInfos):
        self._punkte_anzeige.setText(str(teilnehmer_infos.punkte))
        self._zuege_anzeige.setText(str(teilnehmer_infos.zuege))


class ArenaView(widgets.QWidget):

    def __init__(self, wettkampf: Wettkampf, block_breite: int = 8, block_hoehe: int = 8, hat_gitter: bool = True,
                 gitter_farbe=gui.QColor(200, 200, 200)):
        super().__init__()
        self._wettkampf = wettkampf

        self._teilnehmer_infos = []
        self._painter = gui.QPainter()
        self._gitter_color = gitter_farbe
        self._gitter_dicke = 1 if hat_gitter else 0
        self._block_breite = block_breite
        self._block_hoehe = block_hoehe

        self._bloecke_in_breite = wettkampf.arena_definition.breite
        self._bloecke_in_hoehe = wettkampf.arena_definition.hoehe

        # Es werden pro Feld ein Block und um jeden Block eine Gitter Linie gezeichnet
        self._img_width = self._bloecke_in_breite * self._block_breite + self._gitter_dicke * (self._bloecke_in_breite + 1)
        self._img_height = self._bloecke_in_hoehe * self._block_hoehe + self._gitter_dicke * (self._bloecke_in_hoehe + 1)
        self._pixmap = gui.QPixmap(self._img_width, self._img_height)

        self._direction_arrow = gui.QPolygonF([core.QPointF(-self._block_breite, -self._block_hoehe),
                                               core.QPointF(self._block_breite, 0),
                                               core.QPointF(-self._block_breite, self._block_hoehe)])

        self.setFixedSize(self._img_width, self._img_height)
        self._initialisiere_view()

    def _initialisiere_view(self):
        self._painter.begin(self._pixmap)
        self._painter.fillRect(0, 0, self._img_width, self._img_height, self.palette().color(self.backgroundRole()))
        self._painter.end()
        self._draw_gitter()

    def _draw_gitter(self):
        if self._gitter_dicke <= 0:
            return

        self._painter.begin(self._pixmap)

        pen = gui.QPen(self._gitter_color, 1)
        self._painter.setPen(pen)

        for x in range(self._bloecke_in_breite + 1):
            tmp_x = x * (self._block_breite + self._gitter_dicke)
            self._painter.drawLine(tmp_x, 0, tmp_x, self._img_height)

        for y in range(self._bloecke_in_hoehe + 1):
            tmp_y = y * (self._block_hoehe + self._gitter_dicke)
            self._painter.drawLine(0, tmp_y, self._img_width, tmp_y)

        self._painter.end()

    def aktualisiere_view(self, arena_data: np.ndarray, teilnehmer_infos: List[TeilnehmerInfos]):
        self._teilnehmer_infos = teilnehmer_infos
        self._painter.begin(self._pixmap)

        with np.nditer(arena_data, flags=["multi_index"]) as it:
            for field in it:
                block_x, block_y = self._coordinates_to_point(it.multi_index)
                if field > -1:
                    self._painter.fillRect(block_x, block_y, self._block_breite, self._block_hoehe, _farben[field][1])

        self._painter.end()
        self.repaint()

    def _coordinates_to_point(self, coordinates: (int, int)) -> (float, float):
        return (
            self._gitter_dicke + (self._block_breite + self._gitter_dicke) * coordinates[0],
            self._gitter_dicke + (self._block_hoehe + self._gitter_dicke) * coordinates[1]
        )

    def paintEvent(self, event: gui.QPaintEvent):
        self._painter.begin(self)
        self._painter.drawPixmap(0, 0, self._pixmap)

        # Position/Richtung hier zeichnen, da der Pfeil sonst nicht überzeichnet wird
        for tn in self._teilnehmer_infos:

            self._painter.save()
            angle = math.degrees(math.atan2(tn.richtung.dy, tn.richtung.dx))

            arrow_x, arrow_y = self._coordinates_to_point((tn.x + 0.5, tn.y + 0.5))
            self._painter.translate(arrow_x, arrow_y)
            self._painter.rotate(angle)

            self._painter.setBrush(gui.QBrush(_farben[tn.nummer][0]))
            self._painter.drawPolygon(self._direction_arrow)
            self._painter.restore()

        self._painter.end()


class EventStatistikView(widgets.QWidget):

    def __init__(self, statistiken: EventStatistiken):
        super().__init__()
        self._layout = widgets.QGridLayout()
        self.setLayout(self._layout)

        teilnehmer = statistiken.daten.columns.droplevel("Statistik").unique().to_list()
        statistik_namen = ["Punkte", "Züge"]
        teilnehmer_span = len(statistik_namen)
        runden = sorted(statistiken.daten.index)

        # Tabellen-Kopf
        for j, tn in enumerate(teilnehmer):
            teilnehmer_label = self._erzeuge_teilnehmer_label(tn, "bold")
            self._layout.addLayout(teilnehmer_label, 0, 1 + j * teilnehmer_span, 1, teilnehmer_span, core.Qt.AlignCenter)
            for k, statistik_name in enumerate(statistik_namen):
                self._layout.addWidget(self._erzeuge_label(statistik_name), 1, 1 + j * teilnehmer_span + k, core.Qt.AlignCenter)
        self._layout.addWidget(self._erzeuge_label("Sieger", "bold"), 0, 1 + len(teilnehmer) * teilnehmer_span + 1, 2, 1, core.Qt.AlignBottom | core.Qt.AlignLeft)

        # Werte der Runden
        for i, runde in enumerate(runden):
            self._layout.addWidget(self._erzeuge_label("Runde {}".format(runde + 1), "bold"), 2 + runde, 0, core.Qt.AlignRight)
            runden_sieger = statistiken.sieger_von_runde(runde)
            for j, (nummer, name) in enumerate(teilnehmer):
                for k, statistik_name in enumerate(statistik_namen):
                    wert = statistiken.daten.loc[runde, (nummer, name, statistik_name)]
                    werte_label = self._erzeuge_label(wert, "bold" if runden_sieger[0] == nummer and statistik_name == "Punkte" else None)
                    self._layout.addWidget(werte_label, 2 + i, 1 + j * teilnehmer_span + k, core.Qt.AlignCenter)
            sieger_label = self._erzeuge_teilnehmer_label(runden_sieger)
            self._layout.addLayout(sieger_label, 2 + i, 1 + len(teilnehmer) * teilnehmer_span + 1, core.Qt.AlignLeft)

        # Durchschnitte aller Runden
        letzte_zeile = self._layout.rowCount()
        self._layout.addWidget(self._erzeuge_label("Durchschnitt", "bold"), letzte_zeile, 0, core.Qt.AlignRight)
        punkte_durchschnitt = statistiken.punkte_durchschnitt.round()
        punkte_durchschnitt_max_tn = punkte_durchschnitt.idxmax()
        zuege_durchschnitt = statistiken.zuege_durchschnitt.round()
        for j, tn in enumerate(teilnehmer):
            punkte_weight = "bold" if tn == punkte_durchschnitt_max_tn else None
            self._layout.addWidget(self._erzeuge_label(int(punkte_durchschnitt[tn]), punkte_weight), letzte_zeile, 1 + j * teilnehmer_span, core.Qt.AlignCenter)
            self._layout.addWidget(self._erzeuge_label(int(zuege_durchschnitt[tn])), letzte_zeile, 1 + j * teilnehmer_span + 1, core.Qt.AlignCenter)

        # Sieger Nachricht
        self._layout.addItem(widgets.QSpacerItem(1, 10), self._layout.rowCount(), 0)
        sieger_nachricht = self._erzeuge_label(statistiken.sieger_nachricht, "bold")
        self._layout.addWidget(sieger_nachricht, self._layout.rowCount(), 0, 1, self._layout.columnCount() + 1, core.Qt.AlignCenter)

        # Layout Details
        for c in range(1, 1 + len(teilnehmer) * teilnehmer_span):
            self._layout.setColumnMinimumWidth(c, 70)
        bottom_spacer = widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Minimum, widgets.QSizePolicy.Expanding)
        self._layout.addItem(bottom_spacer, self._layout.rowCount(), 0)

    def _erzeuge_teilnehmer_label(self, teilnehmer: (int, str), font_weight: Union[int, str] = None) -> widgets.QLayout:
        layout = widgets.QHBoxLayout()
        layout.addWidget(TeilnehmerFarbe(teilnehmer[0] - 1))
        layout.addWidget(self._erzeuge_label("[{}] {}".format(*teilnehmer), font_weight))
        return layout

    def _erzeuge_label(self, text, font_weight: Union[int, str] = None):
        label = widgets.QLabel(str(text))
        if font_weight:
            label.setStyleSheet("font-weight: {};".format(font_weight))
        return label


class TeilnehmerFarbe(widgets.QLabel):

    def __init__(self, teilnehmer_nummer: int, hoehe=15, breite=15):
        super().__init__()
        pixmap = gui.QPixmap(hoehe, breite)
        pixmap.fill(_farben[teilnehmer_nummer][0])
        self.setPixmap(pixmap)
