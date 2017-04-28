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
import numpy as np

# Local modules.
from pysemeels.hitachi.eels_su.elv_file import ElvFile
from pysemeels.analysis.zero_loss_peak import ZeroLossPeak

# Project modules.

# Globals and constants variables.


class ZeroLossPeakWidget(QDockWidget):
    def __init__(self, parent, spectra):
        super(ZeroLossPeakWidget, self).__init__("Zero loss peak", parent)

        self.spectra = spectra

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.setObjectName("zero_loss_peak_dock")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        analyze_button = QPushButton("Analyze", self)
        analyze_button.setToolTip('Find and analyze zero loss peak')
        analyze_button.resize(analyze_button.sizeHint())
        analyze_button.clicked.connect(self.analyze_zlp)

        main_layout.addWidget(analyze_button)

        results_layout = QGridLayout()
        label_title_position = QLabel("Position (eV): ")
        self.label_value_position = QLabel("")
        results_layout.addWidget(label_title_position, 0, 0)
        results_layout.addWidget(self.label_value_position, 0, 1)

        label_title_fwhm = QLabel("FWHM (eV): ")
        self.label_value_fwhm = QLabel("")
        results_layout.addWidget(label_title_fwhm, 1, 0)
        results_layout.addWidget(self.label_value_fwhm, 1, 1)

        main_layout.addLayout(results_layout)
        main_layout.addStretch(1)

        self.setWidget(main_widget)

        self.setVisible(False)
        print(self.objectName())

    def analyze_zlp(self):
        print("analyze_zlp")

        elv_file = self.spectra.get_current_elv_file()
        zlp = ZeroLossPeak(elv_file.energies_eV[:-1], np.array(elv_file.counts[:-1]))
        zlp.compute_statistics()
        zlp.compute_fwhm()

        self.label_value_position.setText(str(zlp.mean_eV))
        self.label_value_fwhm.setText(str(zlp.fwhm_eV))
