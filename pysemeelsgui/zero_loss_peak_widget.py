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
from qtpy.QtWidgets import QDockWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QGroupBox
from qtpy.QtCore import Qt
import numpy as np

# Local modules.
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

        results_groupbox = QGroupBox("Analyze results")
        results_layout = QGridLayout()
        label_title_position = QLabel("Position (eV): ")
        self.label_value_position = QLabel("")
        results_layout.addWidget(label_title_position, 0, 0)
        results_layout.addWidget(self.label_value_position, 0, 1)

        label_title_fwhm = QLabel("FWHM (eV): ")
        self.label_value_fwhm = QLabel("")
        results_layout.addWidget(label_title_fwhm, 1, 0)
        results_layout.addWidget(self.label_value_fwhm, 1, 1)

        results_groupbox.setLayout(results_layout)
        main_layout.addWidget(results_groupbox)
        main_layout.addStretch(1)

        fit_button = QPushButton("Fit", self)
        fit_button.setToolTip('Find and fit zero loss peak')
        fit_button.resize(fit_button.sizeHint())
        fit_button.clicked.connect(self.fit_zlp)
        main_layout.addWidget(fit_button)

        results_fit_groupbox = QGroupBox("Fit results")
        results_fit_layout = QGridLayout()

        label_title_position = QLabel("Position (eV): ")
        self.label_value_fit_position = QLabel("")
        results_fit_layout.addWidget(label_title_position, 0, 0)
        results_fit_layout.addWidget(self.label_value_fit_position, 0, 1)

        label_title_fwhm = QLabel("FWHM (eV): ")
        self.label_value_fit_fwhm = QLabel("")
        results_fit_layout.addWidget(label_title_fwhm, 1, 0)
        results_fit_layout.addWidget(self.label_value_fit_fwhm, 1, 1)

        label_title_sigma = QLabel("sigma (eV): ")
        self.label_value_fit_sigma = QLabel("")
        results_fit_layout.addWidget(label_title_sigma, 2, 0)
        results_fit_layout.addWidget(self.label_value_fit_sigma, 2, 1)

        label_title_gamma = QLabel("gamma (eV): ")
        self.label_value_fit_gamma = QLabel("")
        results_fit_layout.addWidget(label_title_gamma, 3, 0)
        results_fit_layout.addWidget(self.label_value_fit_gamma, 3, 1)

        label_title_area = QLabel("area: ")
        self.label_value_fit_area = QLabel("")
        results_fit_layout.addWidget(label_title_area, 4, 0)
        results_fit_layout.addWidget(self.label_value_fit_area, 4, 1)

        label_title_height = QLabel("height: ")
        self.label_value_fit_height = QLabel("")
        results_fit_layout.addWidget(label_title_height, 5, 0)
        results_fit_layout.addWidget(self.label_value_fit_height, 5, 1)

        results_fit_groupbox.setLayout(results_fit_layout)

        main_layout.addWidget(results_fit_groupbox)
        main_layout.addStretch(1)

        self.setWidget(main_widget)

        self.setVisible(False)
        print(self.objectName())

    def analyze_zlp(self):
        print("analyze_zlp")

        elv_file = self.spectra.get_current_elv_file()
        if elv_file is not None:
            zlp = ZeroLossPeak(elv_file.energies_eV[:-1], np.array(elv_file.counts[:-1]))
            zlp.compute_statistics()
            zlp.compute_fwhm()

            self.label_value_position.setText(str(zlp.mean_eV))
            self.label_value_fwhm.setText(str(zlp.fwhm_eV))

    def fit_zlp(self):
        print("analyze_zlp")

        elv_file = self.spectra.get_current_elv_file()
        if elv_file is not None:
            zlp = ZeroLossPeak(elv_file.energies_eV[:-1], np.array(elv_file.counts[:-1]))

            zlp.compute_statistics()
            zlp.compute_fwhm()

            self.label_value_position.setText(str(zlp.mean_eV))
            self.label_value_fwhm.setText(str(zlp.fwhm_eV))

            zlp.fit()

            self.label_value_fit_position.setText(str(zlp.fit_results_position_eV))
            self.label_value_fit_fwhm.setText(str(zlp.fit_results_fwhm_eV))
            self.label_value_fit_sigma.setText(str(zlp.fit_results_sigma_eV))
            self.label_value_fit_gamma.setText(str(zlp.fit_results_gamma_eV))
            self.label_value_fit_area.setText(str(zlp.fit_results_area))
            self.label_value_fit_height.setText(str(zlp.fit_results_height))

            parent = self.parentWidget()
            parent.main_widget.spectrum_canvas.fig.clear()
            zlp.fit_results.plot(fig=parent.main_widget.spectrum_canvas.fig)
            parent.main_widget.spectrum_canvas.draw()
