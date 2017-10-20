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
import time
import os.path
import logging
if six.PY3:
    from tkinter import ttk
    from tkinter import filedialog, N, W, E, S, StringVar, BooleanVar, IntVar, DoubleVar, Tk, DISABLED, NORMAL
elif six.PY2:
    import ttk
    from Tkinter import N, W, E, S, StringVar, BooleanVar, IntVar, DoubleVar, Tk, DISABLED, NORMAL
    import tkFileDialog as filedialog

# Third party modules.
from pywinauto.application import Application, AppNotConnected, ProcessNotFoundError
from pywinauto.timings import TimeoutError

# Local modules.

# Project modules.

# Globals and constants variables.
ADDITIONAL_WAIT_TIME_s = 1.0
ACQUISITION_MODE_LIVE = "Live"
ACQUISITION_MODE_MANUAL = "Manual"


class TkMainGui(ttk.Frame):
    def __init__(self, root, default_folder=""):
        ttk.Frame.__init__(self, root, padding="3 3 12 12")
        self.default_folder = default_folder

        logging.debug("Create main frame")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        logging.debug("Create variable")
        self.program_path = StringVar()
        file_path = os.path.join(self.default_folder, "30kV ElementsView.exe")
        self.program_path.set(file_path)

        self.basename = StringVar()
        self.basename.set("test")

        self.acquisition_mode = StringVar()
        self.acquisition_mode.set(ACQUISITION_MODE_MANUAL)

        self.number_spectra = IntVar()
        self.number_spectra.set(100)

        self.delay_spectrum_s = DoubleVar()
        self.delay_spectrum_s.set(1)

        self.overwrite = BooleanVar()
        self.overwrite.set(False)

        self.is_top_window = BooleanVar()
        self.is_top_window.set(False)
        self.is_manual_acquisition_button = BooleanVar()
        self.is_manual_acquisition_button.set(False)
        self.is_save_as = BooleanVar()
        self.is_save_as.set(False)

        self.results_text = StringVar()

        logging.debug("Create program button")
        row_id = 1
        file_path_entry = ttk.Entry(self, width=80, textvariable=self.program_path)
        file_path_entry.grid(column=2, row=row_id, sticky=(W, E))
        ttk.Button(self, text="Select ElementView program file", command=self.open_element_view_program).grid(column=3, row=row_id, sticky=W)

        logging.debug("Create basename label and edit entry")
        row_id += 1
        basename_label = ttk.Label(self, width=80, text="basename: ", state="readonly")
        basename_label.grid(column=2, row=row_id, sticky=(W, E))
        basename_entry = ttk.Entry(self, textvariable=self.basename)
        basename_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        acquisition_mode_label = ttk.Label(self, width=80, text="Acquisition mode: ", state="readonly")
        acquisition_mode_label.grid(column=2, row=row_id, sticky=(W, E))
        acquisition_mode_entry = ttk.Combobox(self, textvariable=self.acquisition_mode,
                                              values=[ACQUISITION_MODE_LIVE, ACQUISITION_MODE_MANUAL])
        acquisition_mode_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        number_spectra_label = ttk.Label(self, width=80, text="Number of spectra: ", state="readonly")
        number_spectra_label.grid(column=2, row=row_id, sticky=(W, E))
        number_spectra_entry = ttk.Entry(self, textvariable=self.number_spectra)
        number_spectra_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        delay_spectrum_label = ttk.Label(self, width=80, text="Delay between of spectrum (s): ", state="readonly")
        delay_spectrum_label.grid(column=2, row=row_id, sticky=(W, E))
        delay_spectrum_entry = ttk.Entry(self, textvariable=self.delay_spectrum_s)
        delay_spectrum_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        ttk.Checkbutton(self, text="Overwrite file", variable=self.overwrite).grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        ttk.Button(self, text="Find ElementView", command=self.find_element_view, width=80).grid(column=3, row=row_id, sticky=W)

        logging.debug("ElementView elements")
        row_id += 1
        ttk.Checkbutton(self, text="Top window", variable=self.is_top_window, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))
        row_id += 1
        ttk.Checkbutton(self, text="Manual acquisition", variable=self.is_manual_acquisition_button, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))
        row_id += 1
        ttk.Checkbutton(self, text="Save as", variable=self.is_save_as, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        self.start_button = ttk.Button(self, text="Start script", command=self.start_script, width=80, state=DISABLED)
        self.start_button.grid(column=3, row=row_id, sticky=W)

        row_id += 1
        results_label = ttk.Label(self, textvariable=self.results_text, state="readonly")
        results_label.grid(column=2, row=row_id, sticky=(W, E))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        basename_entry.focus()
        self.results_text.set("Start")

    def open_element_view_program(self):
        logging.debug("open_element_view_program")

        file_path = filedialog.askopenfilename(filetypes=(("executable file", "*.exe"), ), initialdir=self.default_folder)
        logging.debug(file_path)
        self.program_path.set(file_path)

    def find_element_view(self):
        try:
            app = Application(backend="win32").connect(path=self.program_path.get())
            print("Application connected")

            try:
                top_window = app.top_window()
                self.is_top_window.set(True)
                print("top_window: {}".format(top_window.print_control_identifiers(depth=1)))

                try:
                    print("Button2: {}".format(top_window.Button2.print_control_identifiers(depth=1)))
                    self.is_manual_acquisition_button.set(True)
                except Exception as message:
                    logging.error(message)
                    self.is_manual_acquisition_button.set(False)

                try:
                    top_window.menu_select("File -> Save")
                    logging.info("File->Save")
                    app.Comment.wait("exists enabled visible ready")
                    logging.info(app.Comment.print_control_identifiers())
                    app.CommentEdit.Edit.SetEditText("auto script")
                    app.Comment.OK.click()
                    logging.info("Comment")

                    app['Save As'].wait("exists enabled visible ready")
                    logging.info(app['Save As'].print_control_identifiers(depth=2))
                    app['Save As'].Cancel.click()
                    logging.info("Cancel")
                    self.is_save_as.set(True)
                except Exception as message:
                    logging.error(message)
                    self.is_save_as.set(False)

            except Exception as message:
                logging.errror(message)
                self.is_top_window.set(False)
                self.is_manual_acquisition_button.set(False)
                self.is_save_as.set(False)

        except (TimeoutError, AppNotConnected, ProcessNotFoundError) as message:
            logging.error(message)
            self.is_top_window.set(False)
            self.is_manual_acquisition_button.set(False)
            self.is_save_as.set(False)

        if self.is_top_window.get() and self.is_manual_acquisition_button.get() and self.is_save_as.get():
            self.results_text.set("ElementView elements found")
            self.start_button.config(state=NORMAL)
        else:
            self.results_text.set("ElementView elements NOT found")
            self.start_button.config(state=DISABLED)

    def start_script(self):
        if self.acquisition_mode.get() == ACQUISITION_MODE_MANUAL:
            self.manual_save()
        if self.acquisition_mode.get() == ACQUISITION_MODE_LIVE:
            self.live_save()

    def manual_save(self):
        self.results_text.set("Manual save")

        app = Application(backend="win32").connect(path=self.program_path.get())
        print("Application connected")

        top_window = app.top_window()

        for spectrum_id in range(1, self.number_spectra.get() + 1):
            print("Spectrum id: {:d}".format(spectrum_id))
            top_window.wait("exists enabled visible ready")

            top_window.Button2.click()

            time.sleep(self.delay_spectrum_s.get())

            top_window.menu_select("File -> Save")

            app.Comment.wait("exists enabled visible ready")
            app.CommentEdit.Edit.SetEditText("auto script")
            app.Comment.OK.click()

            app['Save As'].wait("exists enabled visible ready")
            file_name = "%s_%i.elv" % (self.basename.get(), spectrum_id)
            app['Save As'].Edit.SetEditText(file_name)
            app['Save As'].Save.click()

            try:
                window_confirm = app['Confirm Save As']
                window_confirm.wait("exists enabled visible ready")
                if self.overwrite.get():
                    window_confirm.No.click()
                else:
                    window_confirm.No.click()
            except Exception as message:
                logging.error(message)

        logging.info("Done")
        self.results_text.set("Done")

    def live_save(self):
        self.results_text.set("Live save")

        app = Application(backend="win32").connect(path=self.program_path.get())
        print("Application connected")

        top_window = app.top_window()

        for spectrum_id in range(1, self.number_spectra.get() + 1):
            print("Spectrum id: {:d}".format(spectrum_id))
            top_window.wait("exists enabled visible ready")

            top_window.menu_select("File -> Save")

            app.Comment.wait("exists enabled visible ready")
            app.CommentEdit.Edit.SetEditText("auto script")
            app.Comment.OK.click()

            save_as_window = app['Save As']
            save_as_window.wait("exists enabled visible ready")
            file_name = "%s_%i.elv" % (self.basename.get(), spectrum_id)
            save_as_window.Edit.SetEditText(file_name)
            save_as_window.Save.click()

            try:
                window_confirm = app['Confirm Save As']
                window_confirm.wait("exists enabled visible ready")
                if self.overwrite.get():
                    window_confirm.Yes.click()
                else:
                    window_confirm.No.click()
                    save_as_window.Cancel.click()
                    self.results_text.set("Cancel save file already exist")
                    return
            except Exception as message:
                logging.error(message)

        logging.info("Done")
        self.results_text.set("Done")


def main_gui():
    import sys
    logging.debug("main_gui")

    logging.debug("Create root")
    root = Tk()
    root.title("Controlling ElementView with Python")
    if len(sys.argv) > 1:
        default_folder = sys.argv[1]
    else:
        default_folder = "C:\Program Files\ElementsView\30kV ElementsView.exe"
    TkMainGui(root, default_folder=default_folder).pack()

    logging.debug("Mainloop")
    root.mainloop()


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger().setLevel(logging.INFO)
    main_gui()
