#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.spectrum_widget
   :synopsis: Widget to display an eels spectrum.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Widget to display an eels spectrum.
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
import os.path

# Third party modules.
import six
from qtpy.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from qtpy.QtCore import Qt

from matplotlib.backend_bases import key_press_handler
import qtpy
if qtpy.API == 'pyqt5':
	from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
	from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
elif qtpy.API == 'pyqt':
	from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
	from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Local modules.
from pysemeels.hitachi.eels_su.elv_file import ElvFile

# Project modules.

# Globals and constants variables.


class SpectrumCanvas(FigureCanvas):
    """
    Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    """

    def __init__(self, parent=None, spectra=None, width=3, height=2, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.spectra = spectra

        self.axes = self.fig.add_subplot(111)

        super(SpectrumCanvas, self).__init__(self.fig)
        self.setParent(parent)

        self.compute_initial_figure()

        FigureCanvas.setSizePolicy(self, QSizePolicy.Preferred, QSizePolicy.Preferred)
        FigureCanvas.updateGeometry(self)

        self.setAcceptDrops(True)
        self.draw()

    def compute_initial_figure(self):
        self.axes.set_xlim(0, 1024)
        self.axes.set_ylim(0, 65535)

        self.axes.set_xlabel(r"Energy loss (eV)")
        self.axes.set_ylabel(r"Electron intensity")
        self.figure.tight_layout()

    def update_figure(self, spectrum_data):
        self.axes.cla()
        self.axes.plot(spectrum_data.energies_eV, spectrum_data.counts)

        self.axes.set_xlabel(r"Energy loss (eV)")
        self.axes.set_ylabel(r"Electron intensity")

        self.figure.tight_layout()
        self.draw()

    def resize_canvas(self):
        self.figure.tight_layout()
        self.draw()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-windows-mime;value="FileName"'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-windows-mime;value="FileName"'):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-qt-windows-mime;value="FileName"'):
            if six.PY3:
                data = event.mimeData().text()
                print(data)
                file_path = data.lstrip("file:///")
            elif six.PY2:
                mime_data = event.mimeData().data('application/x-qt-windows-mime;value="FileName"')
                print(mime_data)
                file_path = mime_data.data()
            self.open_spectrum(file_path)
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def open_spectrum(self, file_path):
        self.spectra.open_spectrum(file_path)

        elv_file = self.spectra.get_current_elv_file()
        spectrum_data = elv_file.get_spectrum_data()
        self.update_figure(spectrum_data)


class SpectrumWidget(QWidget):
    def __init__(self, spectra):
        super(SpectrumWidget, self).__init__()

        layout = QVBoxLayout(self)

        self.spectrum_canvas = SpectrumCanvas(self, spectra, width=5, height=4, dpi=100)
        layout.addWidget(self.spectrum_canvas)

        self.mpl_toolbar = NavigationToolbar(self.spectrum_canvas, self)
        layout.addWidget(self.mpl_toolbar)

        self.spectrum_canvas.mpl_connect('key_press_event', self.on_key_press)

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.spectrum_canvas, self.mpl_toolbar)

    def update_figure(self, spectrum_data):
        self.spectrum_canvas.update_figure(spectrum_data)

    def resizeEvent(self, QResizeEvent):
        self.spectrum_canvas.resize_canvas()
