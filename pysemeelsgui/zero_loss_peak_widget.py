#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.zero_loss_peak_widget
   :synopsis: Widget to analyze zero loss peak.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Widget to analyze zero loss peak.
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

# Third party modules.
from qtpy.QtWidgets import QDockWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget
from qtpy.QtCore import Qt


# Local modules.

# Project modules.

# Globals and constants variables.


class ZeroLossPeakWidget(QDockWidget):
    def __init__(self, parent):
        super().__init__("Aero loss peak", parent)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.setObjectName("zero_loss_peak_dock")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        analyze_button = QPushButton("Analyze", self)
        analyze_button.setToolTip('Find and analyze zero loss peak')
        analyze_button.resize(analyze_button.sizeHint())
        analyze_button.clicked.connect(self.find_analyze_zlp)

        main_layout.addWidget(analyze_button)

        results_layout = QGridLayout()
        label_title_position = QLabel("Position (eV): ")
        label_value_position = QLabel("")
        results_layout.addWidget(label_title_position, 0, 0)
        results_layout.addWidget(label_value_position, 0, 1)

        label_title_fwhm = QLabel("FWHM (eV): ")
        label_value_fwhm = QLabel("")
        results_layout.addWidget(label_title_fwhm, 1, 0)
        results_layout.addWidget(label_value_fwhm, 1, 1)

        main_layout.addLayout(results_layout)
        main_layout.addStretch(1)

        self.setWidget(main_widget)

        self.setVisible(False)
        print(self.objectName())


    def find_analyze_zlp(self):
        print("find_analyze_zlp")
