__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

from operator import is_
import sys
import os
import pdfplumber

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.uic import loadUi

is_left_opened = False
is_right_opened = False

pages_dict_right = {}
pages_dict_left = {}


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

    def open_pdf(self, file_path):
        """ Open PDF """
        pages_dict = {}  # Create an empty dictionary to store the pages
        if file_path:
            with pdfplumber.open(file_path) as pdf:
                index = 0
                for page in pdf.pages:
                    # Store the page text in the dictionary
                    pages_dict[index] = page.extract_text()
                    index += 1
        return pages_dict  # Return the dictionary

    def fill_text_browser(self, pages_dict, left_or_right):
        ''' Fill Text Browser '''
        for page in pages_dict:
            if left_or_right == "left":
                self.textBrowser.append(pages_dict[page])
                self.textBrowser.append(
                    " \n========= Page {} End ======== \n".format(page + 1))
            else:
                self.textBrowser_2.append(pages_dict[page])
                self.textBrowser_2.append(
                    " \n========= Page {} End ======== \n".format(page + 1))

    def make_comparison(self):
        ''' Make Comparison '''
        if is_left_opened and is_right_opened:
            self.textBrowser.clear()
            self.textBrowser_2.clear()

            different_lines = '<span style="color:red;">{}</span>'
            same_lines = '<span style="color:black;">{}</span>'

            for page in pages_dict_right:
                lines_right = pages_dict_right[page].split('\n')
                lines_left = pages_dict_left[page].split('\n')

                for line_right, line_left in zip(lines_right, lines_left):
                    if line_right == line_left:
                        self.textBrowser.append(same_lines.format(line_left))
                        self.textBrowser_2.append(
                            same_lines.format(line_right))
                    else:
                        self.textBrowser.append(
                            different_lines.format(line_left))
                        self.textBrowser_2.append(
                            different_lines.format(line_right))

                self.textBrowser.append(
                    " \n========= Page {} End ======== \n".format(page + 1))
                self.textBrowser_2.append(
                    " \n========= Page {} End ======== \n".format(page + 1))

    def left_file_dialog(self):
        """ Left File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit.setText(file_path)

        global pages_dict_left
        pages_dict_left = self.open_pdf(file_path)
        self.fill_text_browser(pages_dict_left, "left")

        global is_left_opened
        is_left_opened = True

        self.make_comparison()

    def right_file_dialog(self):
        """ Right File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit_2.setText(file_path)

        global pages_dict_right
        pages_dict_right = self.open_pdf(file_path)
        self.fill_text_browser(pages_dict_right, "right")

        global is_right_opened
        is_right_opened = True

        self.make_comparison()


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
