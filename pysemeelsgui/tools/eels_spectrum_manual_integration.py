# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import optparse
import time
import logging

from pywinauto.application import Application

ADDITIONAL_WAIT_TIME_s = 1.0


def run(options):
    basename = options.basename
    number_spectra = options.number_spectra
    spectra_acquistion_time_s = options.spectra_acquistion_time_s

    program_path = r"C:\Program Files\ElementsView\30kV ElementsView.exe"
    app = Application(backend="win32").connect(path=program_path)
    print("Application connected")

    top_window = app.top_window()

    print(top_window.print_control_identifiers(depth=1))
    # top_window.Button2.click()

    print(top_window.Button2.print_control_identifiers(depth=1))

    for spectrum_id in range(1, number_spectra+1):
        print("Spectrum id: %i" % (spectrum_id))
        top_window.wait("exists enabled visible ready")

        top_window.Button2.click()

        time.sleep(spectra_acquistion_time_s + ADDITIONAL_WAIT_TIME_s)

        top_window.menu_select("File -> Save")
        logging.info("File->Save")

        app.Comment.wait("exists enabled visible ready")
        logging.info(app.Comment.print_control_identifiers())
        app.CommentEdit.Edit.SetEditText("auto script")
        app.Comment.OK.click()
        logging.info("Comment")

        app['Save As'].wait("exists enabled visible ready")
        logging.info(app['Save As'].print_control_identifiers(depth=2))
        file_name = "%s_%i.elv" % (basename, spectrum_id)
        app['Save As'].Edit.SetEditText(file_name)
        app['Save As'].Save.click()
        logging.info("Save")

    logging.info("Done")


def parse_arguments(argv):
    option_parser = optparse.OptionParser()
    option_parser.add_option("-b", "--basename", action="store", type="string",
                             dest="basename",
                             help="Basename to save EELS spectrum")
    option_parser.add_option("-n", "--number", action="store", type="int",
                             dest="number_spectra",
                             help="Number of EELS spectra to save")
    option_parser.add_option("-t", "--time", action="store", type="float",
                             dest="spectra_acquistion_time_s",
                             help="EELS spectrum acquisition time")

    options, arguments = option_parser.parse_args()
    logging.info("Remaining arguments: {}".format(arguments))
    logging.info("basename: {}".format(options.basename))
    logging.info("number_spectra: {}".format(options.number_spectra))
    logging.info("spectra_acquistion_time_s: {}".format(options.spectra_acquistion_time_s))

    return options


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    import sys
    logging.debug("Number of arguments: {}".format(len(sys.argv)))

    options = parse_arguments(sys.argv)

    run(options)
