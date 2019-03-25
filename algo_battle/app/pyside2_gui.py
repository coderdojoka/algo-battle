import logging
import sys
import util
import importlib
import algorithmen.einfach as einfache_algorithmen

from typing import Optional, Iterable, Tuple, List, Type
from PySide2 import QtWidgets as widgets, QtCore as core, QtGui as gui


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
            try:
                modul = importlib.import_module(modul_pfad)
                _verfuegbare_algorithmen.extend(util.gib_algorithmen_in_modul(modul))
            except (ImportError, ValueError):
                logger().exception("Das Modul '{}' konnte nicht gefunden werden".format(modul_pfad))

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

        if not _verfuegbare_algorithmen:
            self._status_bar.showMessage("Es konnten keine Algorithmen gefunden werden.")
        else:
            self.setCentralWidget(self._start_battle_view)

    def start_battle(self):
        if self._start_battle_view.is_valid:
            message_box = widgets.QMessageBox()
            message_box.setWindowTitle("Battle Daten")
            message_box.setText("{} | {}".format(self._start_battle_view.arena_groesse, self._start_battle_view.algorithmen))
            message_box.exec_()


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
    def algorithmen(self) -> Optional[Iterable[str]]:
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
