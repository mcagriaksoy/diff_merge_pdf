__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys
import os
import pdfplumber

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic import loadUi


class MainWindow(QMainWindow):
    """ Main Window Class """

    def __init__(self):
        # Call the inherited classes __init__ method
        super(MainWindow, self).__init__()
        loadUi('ui.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        self.pushButton.clicked.connect(self.left_file_dialog)
        self.pushButton_2.clicked.connect(self.right_file_dialog)

    def open_file_dialog(self):
        """ Open File Dialog """
        file_path, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "PDF Files (*.pdf)")
        if file_path:
            return file_path

    def open_pdf(self, file_path, left_or_right):
        """ Open PDF """
        if file_path:
            index = 0
            with pdfplumber.open(file_path) as pdf:
                if left_or_right == "left":
                    self.textBrowser.append(pdf.pages[index].extract_text())
                else:
                    self.textBrowser_2.append(pdf.pages[index].extract_text())
                index += 1

    def left_file_dialog(self):
        """ Left File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit.setText(file_path)
        self.open_pdf(file_path, "left")

    def right_file_dialog(self):
        """ Right File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit_2.setText(file_path)
        self.open_pdf(file_path, "right")


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
