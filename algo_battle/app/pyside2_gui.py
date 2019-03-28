import logging
import sys
import util
import random
import numpy as np
import algorithmen.einfach as einfache_algorithmen

from typing import Optional, Iterable, Tuple, Type
from PySide2 import QtWidgets as widgets, QtCore as core, QtGui as gui
from framework.wettkampf import Teilnehmer, Wettkampf, ArenaDefinition
from framework.algorithm import Algorithmus


_font_size = 12
_initial_width = 900
_initial_height = 1000

_min_teilnehmer_anzahl = 2
_max_teilnehmer_anzahl = 10
_min_arena_groesse = 75
_max_arena_groesse = 300

_verfuegbare_algorithmen = []


def start_gui(module: Iterable[str] = None):
    _verfuegbare_algorithmen.extend(util.gib_algorithmen_in_modul(einfache_algorithmen))
    if module:
        for modul_pfad in module:
            _verfuegbare_algorithmen.extend(util.gib_algorithmen_in_modul(modul_pfad))

    app = widgets.QApplication()
    font = app.font()
    font.setPointSize(_font_size)
    app.setFont(font)

    main_view = MainView()
    main_view.setWindowTitle("Algo-Battle")
    main_view.setGeometry(0, 0, _initial_width, _initial_height)
    # main_view.setFixedSize(_initial_width, _initial_height)
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
        self._status_bar.showMessage("Hello World")
        self._toolbar.addWidget(self._status_bar)

        self._start_battle_view = StartBattleView(self._status_bar)
        size_policy = widgets.QSizePolicy(widgets.QSizePolicy.Minimum, widgets.QSizePolicy.Minimum)
        self._start_battle_view.setSizePolicy(size_policy)
        self._start_battle_view.start_knopf.clicked.connect(self.start_battle)

        self._wettkampf_view = WettkampfView(self._status_bar)

        self._content_widget = widgets.QStackedWidget()
        self._content_widget.addWidget(self._start_battle_view)
        self._content_widget.addWidget(self._wettkampf_view)

        if not _verfuegbare_algorithmen:
            self._status_bar.showMessage("Es konnten keine Algorithmen gefunden werden.")
        else:
            self.setCentralWidget(self._content_widget)

    def start_battle(self):
        if self._start_battle_view.is_valid:
            self._wettkampf_view.starte_wettkampf(
                self._start_battle_view.arena_groesse,
                (algorithmus if algorithmus else random.choice(_verfuegbare_algorithmen)
                 for algorithmus in self._start_battle_view.algorithmen)
            )
            self._content_widget.setCurrentIndex(self._content_widget.indexOf(self._wettkampf_view))


# TODO Rename
class StartBattleView(widgets.QWidget):

    def __init__(self, status_bar: widgets.QStatusBar):
        super().__init__()
        self._status_bar = status_bar

        self._anzahl_teilnehmer = widgets.QLineEdit("2")
        self._anzahl_teilnehmer.setFixedWidth(100)
        self._anzahl_teilnehmer.setValidator(gui.QIntValidator(_min_teilnehmer_anzahl, _max_teilnehmer_anzahl))
        self._anzahl_teilnehmer.textChanged.connect(self._teilnehmer_anzahl_geaendert)

        self._algorithmen = []
        self._algorithmus_label = []
        self._algorithmus_felder = []

        self._arena_breite = widgets.QLineEdit("100")
        self._arena_breite.setFixedWidth(50)
        self._arena_breite.setValidator(gui.QIntValidator(_min_arena_groesse, _max_arena_groesse))
        self._arena_breite.setAlignment(core.Qt.AlignRight)
        self._arena_breite.textChanged.connect(self._eingaben_geaendert)

        self._arena_hoehe = widgets.QLineEdit("100")
        self._arena_hoehe.setFixedWidth(50)
        self._arena_hoehe.setValidator(gui.QIntValidator(_min_arena_groesse, _max_arena_groesse))
        self._arena_hoehe.textChanged.connect(self._eingaben_geaendert)

        self._start_knopf = widgets.QPushButton("Start")
        self._start_knopf.setFixedWidth(200)
        self._start_knopf_spacer = widgets.QSpacerItem(1, 20)
        self._bottom_spacer = widgets.QSpacerItem(1, 1, widgets.QSizePolicy.Expanding, widgets.QSizePolicy.Expanding)

        self._layout = widgets.QGridLayout()
        self.setLayout(self._layout)

        self._layout.setColumnStretch(0, 1)
        self._layout.addWidget(widgets.QLabel("Anzahl Teilnehmer"), 0, 0, core.Qt.AlignRight)
        self._layout.addWidget(self._anzahl_teilnehmer, 0, 1, core.Qt.AlignLeft)
        self._layout.addItem(widgets.QSpacerItem(20, 1), 0, 2)
        self._layout.addWidget(widgets.QLabel("Arena Größe"), 0, 3)
        self._layout.addWidget(self._arena_breite, 0, 4)
        self._layout.addWidget(widgets.QLabel("x"), 0, 5)
        self._layout.addWidget(self._arena_hoehe, 0, 6, core.Qt.AlignLeft)
        self._layout.setColumnStretch(6, 1)
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
        self._status_bar.showMessage("{}\n{}".format(teilnehmer_anzahl_nachricht, arena_groesse_nachricht))

    def _teilnehmer_anzahl_geaendert(self):
        if not self._anzahl_teilnehmer.hasAcceptableInput():
            self._eingaben_geaendert()
            return

        while len(self._algorithmen) < self.anzahl_teilnehmer:
            self._algorithmen.append("")

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
            algorithmus_feld = widgets.QComboBox()
            algorithmus_feld.setFixedWidth(357)
            algorithmus_feld.setEditable(False)
            algorithmus_feld.addItem("zufälliger Algorithmus", None)
            for algorithmus in _verfuegbare_algorithmen:
                algorithmus_feld.addItem(
                    "{}.{}".format(algorithmus.__module__, algorithmus.__name__),
                    algorithmus
                )
            vorher_ausgewaehlt = algorithmus_feld.findData(self._algorithmen[index])
            if vorher_ausgewaehlt >= 0:
                algorithmus_feld.setCurrentIndex(vorher_ausgewaehlt)
            self._algorithmus_felder.append(algorithmus_feld)

            label = widgets.QLabel("Teilnehmer {}".format(index + 1))
            self._algorithmus_label.append(label)

            reihe = self._layout.rowCount() + 1
            self._layout.addWidget(label, reihe, 0, core.Qt.AlignRight)
            self._layout.addWidget(algorithmus_feld, reihe, 1, 1, -1, core.Qt.AlignLeft)

        self._layout.addItem(self._start_knopf_spacer, reihe + 1, 0)
        self._layout.addWidget(self._start_knopf, reihe + 2, 0, 1, -1, core.Qt.AlignHCenter)
        self._layout.addItem(self._bottom_spacer, reihe + 3, 0)

        self._eingaben_geaendert()


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


# TODO Manage Colors
class WettkampfView(widgets.QWidget):

    def __init__(self, status_bar: widgets.QStatusBar):
        super().__init__()
        self._status_bar = status_bar
        self._teilnehmer_status = []
        self.arena_view = None

        self._wettkampf = None
        # TODO Arena Canvas
        self._layout = widgets.QVBoxLayout()
        self.setLayout(self._layout)

        self._timer = core.QTimer()
        self._timer.timeout.connect(self._aktualisiere_view)

    def starte_wettkampf(self, arena_groesse: (int, int), algorithmen: Iterable[Type[Algorithmus]]):
        arena_definition = ArenaDefinition(*arena_groesse)
        self._wettkampf = Wettkampf(
            arena_definition.punkte_maximum, arena_definition,
            [algorithmus() for algorithmus in algorithmen]
        )
        self._initialisiere_view()
        self._wettkampf.start()
        self._timer.start()

    def _initialisiere_view(self):
        widget = self._layout.takeAt(0)
        while widget:
            # FIXME
            widget.deleteLater()

        status_container = widgets.QWidget()
        self.arena_view = ArenaView(self._wettkampf, hat_gitter=True)

        # TODO: sinnvolles Layout finden
        hbox = widgets.QHBoxLayout()
        vbox = widgets.QHBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.arena_view)
        status_container.setLayout(vbox)
        for teilnehmer in self._wettkampf.teilnehmer:
            teilnehmer_status = TeilnehmerStatus(teilnehmer, self._wettkampf)
            self._teilnehmer_status.append(teilnehmer_status)
            hbox.addWidget(teilnehmer_status)
        self._layout.addWidget(status_container)

    def _aktualisiere_view(self):
        self.arena_view.aktualisiere_view()

        for teilnehmer_status in self._teilnehmer_status:
            teilnehmer_status.aktualisiere_view()

        if not self._wettkampf.laeuft_noch:
            self._timer.stop()
            self.arena_view.aktualisiere_view() #  finales Bild zeichnen
            # TODO Handle finish


class TeilnehmerStatus(widgets.QGroupBox):

    def __init__(self, teilnehmer: Teilnehmer, wettkampf: Wettkampf):
        super().__init__("[{}] {}".format(teilnehmer.nummer + 1, teilnehmer.name))
        self._teilnehmer = teilnehmer
        self._wettkampf = wettkampf

        self._punkte_anzeige = widgets.QLabel()
        self._zuege_anzeige = widgets.QLabel()

        self._layout = widgets.QFormLayout()
        self._layout.setLabelAlignment(core.Qt.AlignRight)
        self._layout.addRow("Punkte:", self._punkte_anzeige)
        self._layout.addRow("Züge:", self._zuege_anzeige)
        self.setLayout(self._layout)
        self.setMinimumWidth(125)

    def aktualisiere_view(self):
        punkte_text = str(self._wettkampf.punkte_von(self._teilnehmer))
        self._punkte_anzeige.setText(punkte_text)

        zuege_text = str(self._wettkampf.zuege_von(self._teilnehmer))
        self._zuege_anzeige.setText(zuege_text)


class ArenaView(widgets.QWidget):

    def __init__(self, wettkampf: Wettkampf, block_breite: int = 8, block_hoehe: int = 8, hat_gitter: bool = True,
                 gitter_farbe=core.Qt.blue):
        super().__init__()
        self._wettkampf = wettkampf

        self._painter = gui.QPainter()
        self._gitter_color = gitter_farbe
        self._gitter_dicke = 1 if hat_gitter else 0
        self._block_breite = block_breite
        self._block_hoehe = block_hoehe

        self._bloecke_in_breite = wettkampf.arena_definition.breite
        self._bloecke_in_hoehe = wettkampf.arena_definition.hoehe

        # Es werden pro Feld ein Block und um jeden Block eine Gitter Linie gezeichnet
        self._img_width = self._bloecke_in_breite * self._block_breite + self._gitter_dicke * (self._bloecke_in_breite + 1)
        self._img_height = self._bloecke_in_hoehe * self._block_hoehe + self._gitter_dicke * (
                self._bloecke_in_hoehe + 1)

        self._buffer = gui.QPixmap(self._img_width, self._img_height)
        """
        Pufferbild, um Off-Screen zu zeichnen.
        """

        self.setFixedSize(self._img_width, self._img_height)

        # Gitter einmal zeichnen
        self.clear()

    def clear(self):
        self._painter.begin(self._buffer)
        self._painter.fillRect(0, 0, self._img_width, self._img_height, self.palette().color(self.backgroundRole()))
        self._painter.end()
        self._draw_gutter()

    def _draw_gutter(self):
        if self._gitter_dicke <= 0:
            return

        self._painter.begin(self._buffer)

        pen = gui.QPen(self._gitter_color, 1)
        self._painter.setPen(pen)

        for x in range(self._bloecke_in_breite + 1):
            tmp_x = x * (self._block_breite + self._gitter_dicke)
            self._painter.drawLine(tmp_x, 0, tmp_x, self._img_height)

        for y in range(self._bloecke_in_hoehe + 1):
            tmp_y = y * (self._block_hoehe + self._gitter_dicke)
            self._painter.drawLine(0, tmp_y, self._img_width, tmp_y)

        self._painter.end()

    def selektive_update(self, teilnehmer):
        pass

    def aktualisiere_view(self):
        data = self._wettkampf.arena_snapshot
        self._painter.begin(self._buffer)

        with np.nditer(data, flags=["multi_index"]) as it:
            for field in it:
                x, y = it.multi_index
                block_x = self.x_index2block_x(x)
                block_y = self.y_index2block_y(y)

                if field > -1:
                    self._painter.fillRect(block_x, block_y, self._block_breite, self._block_hoehe, _farben[field][1])

        # TODO: Versatz zwischen gezeichneten Felder und Teilnehmer Position! (im Hintergrund aktualisiert)
        for tn in self._wettkampf.teilnehmer:
            self._painter.fillRect(self.x_index2block_x(tn.x), self.y_index2block_y(tn.y), self._block_breite, self._block_hoehe, _farben[tn.nummer][0])

        self._painter.end()
        self.repaint()

    def y_index2block_y(self, y):
        return self._gitter_dicke + (self._block_hoehe + self._gitter_dicke) * y

    def x_index2block_x(self, x):
        return self._gitter_dicke + (self._block_breite + self._gitter_dicke) * x

    def paintEvent(self, event: gui.QPaintEvent):
        self._painter.begin(self)
        self._painter.drawPixmap(0, 0, self._buffer)
        self._painter.end()
