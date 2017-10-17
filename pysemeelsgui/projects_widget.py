#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeels.projects_widget

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Widget for the projects manager
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

# Third party modules.
from qtpy.QtWidgets import QDockWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from qtpy.QtCore import Qt

# Local modules.

# Project modules.

# Globals and constants variables.


class ProjectWidget(QDockWidget):
    def __init__(self, parent):
        super(ProjectWidget, self).__init__("Projects manager", parent)

        main_tree_widget = QTreeWidget(self)
        # main_layout = QVBoxLayout()
        # main_tree_widget.setLayout(main_layout)

        self.setObjectName("projects_dock")
        self.setAllowedAreas(Qt.AllDockWidgetAreas)

        main_tree_widget.setHeaderLabels(["Untitled project"])

        # main_tree_widget.setHeaderLabels(["ProjectName"])

        # item = QTreeWidgetItem()

        for i in range(3):
            parent = QTreeWidgetItem(main_tree_widget)
            parent.setText(0, "Parent {}".format(i))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(5):
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setCheckState(0, Qt.Unchecked)

        main_tree_widget.currentItemChanged.connect(self.changed_item)

        self.setWidget(main_tree_widget)

        self.setVisible(False)
        print(self.objectName())

    def changed_item(self, current_item, previous_item):
        if current_item:
            print("Current item: {}".format(current_item.text(0)))
        if previous_item:
            print("Previous item: {}".format(previous_item.text(0)))
