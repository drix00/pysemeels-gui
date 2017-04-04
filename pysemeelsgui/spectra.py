#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.spectra
   :synopsis: Container of EELS spectrum.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Container of EELS spectrum.
"""

###############################################################################
# Copyright 2017 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import os.path

# Third party modules.
import six

# Local modules.
from pysemeels.hitachi.eels_su.elv_file import ElvFile

# Project modules.

# Globals and constants variables.

class Spectra(object):
    def __init__(self):
        self.spectra = {}
        self.current_elv_file = None

    def open_spectrum(self, file_names):
        if six.PY3:
            if isinstance(file_names, str):
                file_names = [file_names]
        elif six.PY2:
            if isinstance(file_names, basestring):
                file_name = [file_names]

        for file_name in file_names:
            if os.path.splitext(file_name)[1] == ".elv":
                with open(file_name, 'r') as elv_text_file:
                    elv_file = ElvFile()
                    elv_file.read(elv_text_file)

                    self.set_current_elv_file(elv_file)

    def set_current_elv_file(self, elv_file):
        self.current_elv_file = elv_file

    def get_current_elv_file(self):
        return self.current_elv_file

