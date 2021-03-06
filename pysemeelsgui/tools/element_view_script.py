#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pysemeelsgui.tools.element_view_script
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
from pywinauto.timings import TimeoutError, Timings

# Local modules.

# Project modules.

# Globals and constants variables.
ADDITIONAL_WAIT_TIME_s = 1.0
ACQUISITION_MODE_LIVE = "Live"
ACQUISITION_MODE_MANUAL = "Manual"


def get_current_module_path(module_path, relative_path=""):
    base_path = os.path.dirname(module_path)

    filepath = os.path.join(base_path, relative_path)
    filepath = os.path.normpath(filepath)

    return filepath


def get_save_path():
    path = get_current_module_path(__file__, "../../log")
    if not os.path.isdir(path):
        os.makedirs(path)

    return path


def setup_logger():
    new_logger = logging.getLogger()
    new_logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    log_format = '%(asctime)s : %(name)-40s : %(levelname)-10s : %(message)s'
    formatter = logging.Formatter(log_format)

    ch.setFormatter(formatter)

    new_logger.addHandler(ch)

    path = get_save_path()
    log_file_path = os.path.join(path, "{}.log".format("element_view_script"))
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    new_logger.addHandler(fh)

    return new_logger


logger = setup_logger()


class TkMainGui(ttk.Frame):
    def __init__(self, root, default_folder=""):
        ttk.Frame.__init__(self, root, padding="3 3 12 12")
        self.default_folder = default_folder

        logger.debug("Create main frame")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        logger.debug("Create variable")
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

        self.fast_acquisition = BooleanVar()
        self.fast_acquisition.set(False)

        self.is_top_window = BooleanVar()
        self.is_top_window.set(False)
        self.is_manual_acquisition_button = BooleanVar()
        self.is_manual_acquisition_button.set(False)
        self.is_save_as = BooleanVar()
        self.is_save_as.set(False)

        self.results_text = StringVar()

        widget_width = 40

        logger.debug("Create program button")
        row_id = 1
        file_path_entry = ttk.Entry(self, width=widget_width, textvariable=self.program_path)
        file_path_entry.grid(column=2, row=row_id, sticky=(W, E))
        ttk.Button(self, width=widget_width, text="Select ElementView program file", command=self.open_element_view_program).grid(column=3, row=row_id, sticky=W)

        logger.debug("Create basename label and edit entry")
        row_id += 1
        basename_label = ttk.Label(self, width=widget_width, text="basename: ", state="readonly")
        basename_label.grid(column=2, row=row_id, sticky=(W, E))
        basename_entry = ttk.Entry(self, width=widget_width, textvariable=self.basename)
        basename_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        acquisition_mode_label = ttk.Label(self, width=widget_width, text="Acquisition mode: ", state="readonly")
        acquisition_mode_label.grid(column=2, row=row_id, sticky=(W, E))
        acquisition_mode_entry = ttk.Combobox(self, width=widget_width, textvariable=self.acquisition_mode,
                                              values=[ACQUISITION_MODE_LIVE, ACQUISITION_MODE_MANUAL])
        acquisition_mode_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        number_spectra_label = ttk.Label(self, width=widget_width, text="Number of spectra: ", state="readonly")
        number_spectra_label.grid(column=2, row=row_id, sticky=(W, E))
        number_spectra_entry = ttk.Entry(self, width=widget_width, textvariable=self.number_spectra)
        number_spectra_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        delay_spectrum_label = ttk.Label(self, width=widget_width, text="Delay between of spectrum (s): ", state="readonly")
        delay_spectrum_label.grid(column=2, row=row_id, sticky=(W, E))
        delay_spectrum_entry = ttk.Entry(self, width=widget_width, textvariable=self.delay_spectrum_s)
        delay_spectrum_entry.grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="Overwrite file", variable=self.overwrite).grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="Fast acquisition", variable=self.fast_acquisition).grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        ttk.Button(self, width=widget_width, text="Find ElementView", command=self.find_element_view).grid(column=3, row=row_id, sticky=W)

        logger.debug("ElementView elements")
        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="Top window", variable=self.is_top_window, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))
        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="Manual acquisition", variable=self.is_manual_acquisition_button, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))
        row_id += 1
        ttk.Checkbutton(self, width=widget_width, text="Save as", variable=self.is_save_as, state=DISABLED).grid(column=3, row=row_id, sticky=(W, E))

        row_id += 1
        self.start_button = ttk.Button(self, width=widget_width, text="Start script", command=self.start_script, state=DISABLED)
        self.start_button.grid(column=3, row=row_id, sticky=W)

        row_id += 1
        results_label = ttk.Label(self, textvariable=self.results_text, state="readonly")
        results_label.grid(column=2, row=row_id, sticky=(W, E))

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        basename_entry.focus()
        self.results_text.set("Start")

    def open_element_view_program(self):
        logger.debug("open_element_view_program")

        file_path = filedialog.askopenfilename(filetypes=(("executable file", "*.exe"), ), initialdir=self.default_folder)
        logger.debug(file_path)
        self.program_path.set(file_path)

    def find_element_view(self):
        try:
            app = Application(backend="win32").connect(path=self.program_path.get())
            logger.info("Application connected")
            # logger.info("app: {}".format(app.print_control_identifiers(depth=1)))

            try:
                top_window = app.top_window()
                top_window.wait("exists enabled visible ready")
                self.is_top_window.set(True)
                logger.info("top_window: {}".format(top_window.print_control_identifiers(depth=1)))

                try:
                    logger.info("Button2: {}".format(top_window.Button2.print_control_identifiers(depth=1)))
                    self.is_manual_acquisition_button.set(True)
                except Exception as message:
                    logger.error(message)
                    self.is_manual_acquisition_button.set(False)

                try:
                    top_window.menu_select("File -> Save")
                    logger.info("File->Save")
                    app.Comment.wait("exists enabled visible ready")
                    logger.info(app.Comment.print_control_identifiers())
                    # app.CommentEdit.Edit.SetEditText("auto script")
                    app.Comment.OK.click()
                    logger.info("Comment")

                    app['Save As'].wait("exists enabled visible ready")
                    logger.info(app['Save As'].print_control_identifiers(depth=2))
                    app['Save As'].Cancel.click()
                    logger.info("Cancel")
                    self.is_save_as.set(True)
                except Exception as message:
                    logger.error(message)
                    self.is_save_as.set(False)

            except Exception as message:
                logger.errror(message)
                self.is_top_window.set(False)
                self.is_manual_acquisition_button.set(False)
                self.is_save_as.set(False)

        except (TimeoutError, AppNotConnected, ProcessNotFoundError) as message:
            logger.error(message)
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
        self.save_spectra()

    def save_spectra(self):
        acquisition_mode = self.acquisition_mode.get()
        safe_acquisition = not self.fast_acquisition.get()
        overwrite = self.overwrite.get()

        if self.fast_acquisition.get():
            Timings.Fast()
            Timings.window_find_timeout = 2

        if acquisition_mode == ACQUISITION_MODE_MANUAL:
            self.results_text.set("Manual save")
        if acquisition_mode == ACQUISITION_MODE_LIVE:
            self.results_text.set("Live save")

        app = Application(backend="win32").connect(path=self.program_path.get())
        logger.info("Application connected")

        top_window = app.window(title_re=".*ElementsView.*")
        if safe_acquisition:
            top_window.wait("exists enabled visible ready")

        for spectrum_id in range(1, self.number_spectra.get() + 1):
            logger.info("Spectrum id: {:d}".format(spectrum_id))

            if safe_acquisition:
                top_window.wait("exists enabled visible ready")

            if acquisition_mode == ACQUISITION_MODE_MANUAL:
                top_window.Button2.click()

                time.sleep(self.delay_spectrum_s.get())

            if safe_acquisition:
                top_window.wait("exists enabled visible ready")
            top_window.menu_select("File -> Save")

            if safe_acquisition:
                app.Comment.wait("exists enabled visible ready")
                app.CommentEdit.Edit.SetEditText("auto script")
            app.Comment.OK.click()

            save_as_window = app['Save As']
            if safe_acquisition:
                save_as_window.wait("exists enabled visible ready")
            file_name = "%s_%i.elv" % (self.basename.get(), spectrum_id)
            save_as_window.Edit.SetEditText(file_name)
            save_as_window.Save.click()

            if overwrite:
                try:
                    window_confirm = app['Confirm Save As']
                    if safe_acquisition:
                        window_confirm.wait("exists enabled visible ready")
                    if self.overwrite.get():
                        window_confirm.Yes.click()
                    else:
                        window_confirm.No.click()
                        save_as_window.Cancel.click()
                        self.results_text.set("Cancel save file already exist")
                        return
                except Exception as message:
                    logger.error(message)

        logger.info("Done")
        self.results_text.set("Done")


def main_gui():
    import sys
    logger.debug("main_gui")

    logger.debug("Create root")
    root = Tk()
    root.title("Controlling ElementView with Python")
    if len(sys.argv) > 1:
        default_folder = sys.argv[1]
    else:
        default_folder = r"C:\Program Files\ElementsView"
    TkMainGui(root, default_folder=default_folder).pack()

    logger.debug("Mainloop")
    root.mainloop()


if __name__ == '__main__':  # pragma: no cover
    main_gui()
