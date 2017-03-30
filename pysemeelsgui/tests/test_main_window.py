#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.tests.test_main_window
   :synopsis: Tests for the module :py:mod:`pysemeelsgui.main_window`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`pysemeelsgui.main_window`.
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
import unittest

# Third party modules.

# Local modules.

# Project modules.
import pysemeelsgui.main_window


# Globals and constants variables.

class TestMainWindow(unittest.TestCase):
    """
    TestCase class for the module `pysemeelsgui.main_window`.
    """

    def setUp(self):
        """
        Setup method.
        """

        unittest.TestCase.setUp(self)

    def tearDown(self):
        """
        Teardown method.
        """

        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        """
        First test to check if the testcase is working with the testing framework.
        """

        #self.fail("Test if the testcase is working.")
        self.assert_(True)


if __name__ == '__main__':  # pragma: no cover
    import nose

    nose.runmodule()
