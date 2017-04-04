#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.main_window
   :synopsis: Main window of the application.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Main window of the application.
"""

###############################################################################
# GUI for pySEM-EELS project.
# Copyright (C) 2017  Hendrix Demers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

# Standard library modules.
import sys
import os.path

# Third party modules.
from qtpy.QtWidgets import QMainWindow, QAction, QApplication, QStyle, QFileDialog, QDockWidget, QLabel
from qtpy.QtCore import QSettings, Qt

import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

# Local modules.

# Project modules.
from pysemeelsgui.spectrum_widget import SpectrumWidget
from pysemeelsgui.zero_loss_peak_widget import ZeroLossPeakWidget
from pysemeelsgui.spectra import Spectra

# Globals and constants variables.


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.spectra = Spectra()

        self.init_ui()

        self.read_settings()

    def init_ui(self):
        # Define standard icon.
        standard_icon = self.style().standardIcon

        # Central widget.
        self.main_widget = SpectrumWidget(self.spectra)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # Open spectrum action
        open_spectrum_action = QAction(standard_icon(QStyle.SP_DialogOpenButton), 'Open spectrum', self)
        open_spectrum_action.setShortcut('Ctrl+O')
        open_spectrum_action.setStatusTip('Open spectrum')
        open_spectrum_action.triggered.connect(self.open_spectrum)

        # Exit action
        exit_action = QAction(standard_icon(QStyle.SP_TitleBarCloseButton), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        # Status bar.
        self.statusBar()

        # Menu bar.
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_spectrum_action)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('&View')

        analysis_menu = menubar.addMenu('&Analysis')

        # Toolbar
        file_toolbar = self.addToolBar('File')
        file_toolbar.addAction(open_spectrum_action)
        file_toolbar.addAction(exit_action)
        view_menu.addAction(file_toolbar.toggleViewAction())

        analysis_toolbar = self.addToolBar('Analysis')
        view_menu.addAction(analysis_toolbar.toggleViewAction())

        view_menu.addSeparator()

        # Dock widget.
        self.graphic_settings_dock = QDockWidget("Graphic settings", self)
        self.graphic_settings_dock.setObjectName("graphic_settings_dock")
        self.graphic_settings_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        label_test = QLabel("Test label")
        self.graphic_settings_dock.setWidget(label_test)
        view_menu.addAction(self.graphic_settings_dock.toggleViewAction())
        self.addDockWidget(Qt.AllDockWidgetAreas, self.graphic_settings_dock)
        print(self.graphic_settings_dock.objectName())

        self.zero_loss_peak_dock = ZeroLossPeakWidget(self, self.spectra)
        analysis_menu.addAction(self.zero_loss_peak_dock.toggleViewAction())
        self.addDockWidget(Qt.AllDockWidgetAreas, self.zero_loss_peak_dock)

        # Final options.
        self.setWindowTitle('pySEM-EELS')
        self.show()

    def closeEvent(self, event):
        self.save_settings()
        super(MainWindow, self).closeEvent(event)

    def save_settings(self):
        settings = QSettings("openMicroanalysis", "pysemeelsgui")
        #print(settings.fileName())

        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("window_state", self.saveState())
        settings.endGroup()

        settings.beginGroup("graphic_settings_dock")
        settings.setValue("visible", self.graphic_settings_dock.isVisible())
        settings.endGroup()

        settings.beginGroup("zero_loss_peak_dock")
        settings.setValue("visible", self.zero_loss_peak_dock.isVisible())
        settings.endGroup()

    def read_settings(self):
        settings = QSettings("openMicroanalysis", "pysemeelsgui")
        #print(settings.fileName())
        #settings.clear()

        settings.beginGroup("MainWindow")
        geometry_value = settings.value("geometry")
        if geometry_value is None:
            self.setGeometry(300, 300, 600, 400)
        else:
            self.restoreGeometry(geometry_value)
        window_state_value = settings.value("window_state")
        if window_state_value is not None:
            self.restoreState(window_state_value)
        settings.endGroup()

        settings.beginGroup("graphic_settings_dock")
        visible_value = settings.value("visible")
        if visible_value is not None:
            if visible_value == "true":
                self.graphic_settings_dock.setVisible(True)
            elif visible_value == "false":
                self.graphic_settings_dock.setVisible(False)
        settings.endGroup()

        settings.beginGroup("zero_loss_peak_dock")
        visible_value = settings.value("visible")
        if visible_value is not None:
            if visible_value == "true":
                self.zero_loss_peak_dock.setVisible(True)
            elif visible_value == "false":
                self.zero_loss_peak_dock.setVisible(False)
        settings.endGroup()


    def open_spectrum(self):
        self.statusBar().showMessage("Opening spectrum", 2000)

        path = os.path.dirname(__file__)
        formats = ["*.elv"]
        filter = "Spectrum file ({:s})".format(" ".join(formats))
        file_names = QFileDialog.getOpenFileName(self, "Open an EELS spectrum", path, filter)

        self.spectra.open_spectrum(file_names)

        elv_file = self.spectra.get_current_elv_file()
        spectrum_data = elv_file.get_spectrum_data()
        self.main_widget.update_figure(spectrum_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
