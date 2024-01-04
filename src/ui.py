__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)
    window_object = QMainWindow()

    file_path = os.path.join("ui.ui")
    if not os.path.exists(file_path):
        print("UI File Not Found!")
        sys.exit(1)
    loadUi(file_path, window_object)

    window_object.show()
    sys.exit(app.exec())
