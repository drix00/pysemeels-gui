#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.tools.batch_processing
   :synopsis: GUI to process EELS files in batch mode.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

GUI to process EELS files in batch mode.
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
import six
import logging
if six.PY3:
    from tkinter import ttk
    from tkinter import filedialog, N, W, E, S, StringVar, BooleanVar, Tk
elif six.PY2:
    import ttk
    from Tkinter import N, W, E, S, StringVar, BooleanVar, Tk
    import tkFileDialog as filedialog


# Third party modules.

# Local modules.
from pysemeels.tools.convert_elv import ConvertElv
from pysemeels.tools.batch_convert_elv import BatchConvertElv
from pysemeels.tools.batch_generate_spectra import BatchGenerateSpectra
from pysemeels.tools.batch_generate_windows_figure import BatchGenerateWindowsFigure

# Project modules.

# Globals and constants variables.


class TkMainGui(ttk.Frame):
    def __init__(self, root, default_folder=""):
        ttk.Frame.__init__(self, root, padding="3 3 12 12")
        self.default_folder = default_folder

        logging.debug("Create main frame")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        logging.debug("Create variable")
        self.file_path = StringVar()
        self.data_folder = StringVar()

        self.recursive = BooleanVar()
        self.recursive.set(True)
        self.overwrite = BooleanVar()
        self.overwrite.set(True)

        self.convert_msa = BooleanVar()
        self.convert_msa.set(False)
        self.convert_hdf5 = BooleanVar()
        self.convert_hdf5.set(False)
        self.use_project_hdf5_file = BooleanVar()
        self.use_project_hdf5_file.set(True)
        self.project_hdf5_file = StringVar()

        self.generate_spectrum_figure = BooleanVar()
        self.generate_spectrum_figure.set(False)
        self.generate_window_figure = BooleanVar()
        self.generate_window_figure.set(False)

        self.results_text = StringVar()

        logging.debug("Create file button")
        row_id = 1
        file_path_entry = ttk.Entry(self, width=80, textvariable=self.file_path)
        file_path_entry.grid(column=2, row=1, sticky=(W, E))
        ttk.Button(self, text="Select a elv file", command=self.open_file).grid(column=3, row=row_id, sticky=W)

        logging.debug("Create folder button")
        row_id += 1
        data_folder_entry = ttk.Entry(self, width=80, textvariable=self.data_folder)
        data_folder_entry.grid(column=2, row=2, sticky=(W, E))
        ttk.Button(self, text="Select a folder", command=self.open_data_folder).grid(column=3, row=row_id, sticky=W)

        row_id += 1
        ttk.Checkbutton(self, text="Recursive folder", var=self.recursive, width=80).grid(column=3, row=row_id,
                                                                                          sticky=W)

        row_id += 1
        ttk.Checkbutton(self, text="Overwrite processing result files", var=self.overwrite, width=80).grid(column=3,
                                                                                                           row=row_id,
                                                                                                           sticky=W)

        row_id += 1
        ttk.Checkbutton(self, text="Export MSA", var=self.convert_msa, width=80).grid(column=3, row=row_id, sticky=W)

        row_id += 1
        ttk.Checkbutton(self, text="Export single HDF5", var=self.convert_hdf5, width=80).grid(column=3, row=row_id, sticky=W)
        row_id += 1
        ttk.Checkbutton(self, text="Export in project HDF5", var=self.use_project_hdf5_file, width=80).grid(column=3, row=row_id, sticky=W)

        row_id += 1
        file_path_entry = ttk.Entry(self, width=80, textvariable=self.project_hdf5_file)
        file_path_entry.grid(column=2, row=row_id, sticky=W)
        ttk.Button(self, text="Select a project HDF5 file", command=self.save_as_project_hdf5_file).grid(column=3, row=row_id, sticky=W)

        row_id += 1
        ttk.Checkbutton(self, text="Generate spectrum figure", var=self.generate_spectrum_figure, width=80).grid(column=3, row=row_id, sticky=W)
        row_id += 1
        ttk.Checkbutton(self, text="Generate window figure", var=self.generate_window_figure, width=80).grid(column=3, row=row_id, sticky=W)

        row_id += 1
        ttk.Button(self, text="Process data", command=self.process_data, width=80).grid(column=2, row=row_id, sticky=W)

        row_id += 1
        results_label = ttk.Label(self, textvariable=self.results_text, state="readonly")
        results_label.grid(column=2, row=row_id, sticky=(W, E))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        file_path_entry.focus()

    def open_file(self):
        logging.debug("open_element_view_program")

        filename = filedialog.askopenfilename(filetypes=(("ELV file", "*.elv"), ), initialdir=self.default_folder)
        logging.debug(filename)
        self.file_path.set(filename)

    def open_data_folder(self):
        logging.debug("open_data_folder")

        folder_name = filedialog.askdirectory(initialdir=self.default_folder)
        logging.debug(folder_name)
        self.data_folder.set(folder_name)

    def save_as_project_hdf5_file(self):
        filename = filedialog.asksaveasfilename(initialdir=self.data_folder.get(),
                                                title="Save as Project HDF5 file",
                                                filetypes=[("Project HDF5 file", "*.hdf5")])
        if filename:
            self.project_hdf5_file.set(filename)

    def process_data(self):
        logging.debug("process_data")

        elv_file_path = self.file_path.get()

        if self.is_conversion_needed() and len(elv_file_path) > 0:
            self.results_text.set("Convert file ...")
            convert_elv = ConvertElv(elv_file_path)

            convert_elv.convert_msa = self.convert_msa.get()
            convert_elv.convert_hdf5 = self.convert_hdf5.get()

            convert_elv.convert()
            self.results_text.set("Convert file ... Done")

        data_folder = self.data_folder.get()
        if len(data_folder) > 0:
            if self.is_conversion_needed():
                self.results_text.set("Batch converting files ...")
                batch_convert_elv = BatchConvertElv(data_folder)
                batch_convert_elv.overwrite = self.overwrite.get()
                batch_convert_elv.recursive = self.recursive.get()
                batch_convert_elv.convert_msa = self.convert_msa.get()
                batch_convert_elv.convert_hdf5 = self.convert_hdf5.get()
                batch_convert_elv.project_hdf5_file = self.project_hdf5_file.get()

                batch_convert_elv.convert()
                self.results_text.set("Batch converting files ... Done")

            if self.generate_spectrum_figure.get():
                self.results_text.set("Generate spectra figures ...")
                batch_generate_spectra = BatchGenerateSpectra(data_folder)
                batch_generate_spectra.generate()
                self.results_text.set("Generate spectra figures ... Done")

            if self.generate_window_figure.get():
                self.results_text.set("Generate windows figures ...")
                batch_generate_windows_figure = BatchGenerateWindowsFigure(data_folder)
                batch_generate_windows_figure.generate()
                self.results_text.set("Generate windows figures ... Done")

        self.results_text.set("Completed")

    def is_conversion_needed(self):
        return self.convert_msa.get() or self.convert_hdf5.get() or self.convert_hdf5.get()


def main_gui():
    import sys
    logging.debug("main_gui")

    logging.debug("Create root")
    root = Tk()
    root.title("Batch processing of EELS data files")
    if len(sys.argv) > 1:
        default_folder = sys.argv[1]
    else:
        default_folder = ""
    TkMainGui(root, default_folder=default_folder).pack()

    logging.debug("Mainloop")
    root.mainloop()


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger().setLevel(logging.INFO)
    main_gui()
