__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys
import os
import pdfplumber

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from PyQt6.uic import loadUi

pages_dict_right = {}
pages_dict_left = {}


class SharedObjects():
    """ Shared Objects """

    def __init__(self,
                 left_pdf_opened=False,
                 right_pdf_opened=False,
                 left_pdf_is_image=False,
                 right_pdf_is_image=False,
                 imported_left_pdf={},
                 imported_right_pdf={}):
        """ Clear """
        self.is_left_pdf_opened = left_pdf_opened
        self.is_right_pdf_opened = right_pdf_opened
        self.is_left_pdf_is_image = left_pdf_is_image
        self.is_right_pdf_is_image = right_pdf_is_image
        self.imported_left_pdf = imported_left_pdf
        self.imported_right_pdf = imported_right_pdf

    is_left_pdf_opened = False
    is_right_pdf_opened = False
    is_left_pdf_is_image = False
    is_right_pdf_is_image = False
    imported_left_pdf = {}
    imported_right_pdf = {}


class MainWindow(QMainWindow):
    """ Main Window Class """

    def __init__(self):
        # Call the inherited classes __init__ method
        super(MainWindow, self).__init__()
        loadUi('ui.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        self.pushButton.clicked.connect(self.left_file_dialog)
        self.pushButton_2.clicked.connect(self.right_file_dialog)
        self.clearButton.clicked.connect(self.clear_all)

    def clear_all(self):
        """ Clear All """
        self.textBrowser.clear()
        self.textBrowser_2.clear()
        self.lineEdit.clear()
        self.lineEdit_2.clear()

        # Init the SharedObjects
        SharedObjects(False, False, False, False, {}, {})

        # delete tmp folder
        for filename in os.listdir("tmp"):
            file_path = os.path.join("tmp", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def open_file_dialog(self):
        """ Open File Dialog """
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "QFileDialog.getOpenFileName()",
                                                   "",
                                                   "PDF Files (*.pdf)")
        if file_path:
            return file_path

    def save_images(self, file_path):
        """ Get Images """
        if file_path:
            pdf = pdfplumber.open(file_path)
            for page in pdf.pages:
                images_in_page = page.images
                page_height = page.height
                # assuming images_in_page has at least one element, only for understanding purpose.
                image = images_in_page[0]
                image_bbox = (
                    image['x0'], page_height - image['y1'], image['x1'], page_height - image['y0'])
                cropped_page = page.crop(image_bbox)
                image_obj = cropped_page.to_image(resolution=75)
                image_obj.save(f"tmp/tmp_{page.page_number}.jpeg")

    def get_images(self):
        """ Get Images from disk """
        images = []
        for filename in os.listdir("tmp"):
            if filename.endswith(".jpeg"):
                images.append("tmp/" + filename)
        return images

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

    def fill_left_side_with_images(self):
        """ Fill Left Side With Images """
        self.save_images(self.lineEdit.text())
        images = self.get_images()
        for image in images:
            self.textBrowser.append(f'<img src="{image}">')

        SharedObjects.is_left_pdf_is_image = True

    def fill_right_side_with_images(self):
        """ Fill Right Side With Images """
        self.save_images(self.lineEdit_2.text())
        images = self.get_images()
        for image in images:
            self.textBrowser_2.append(f'<img src="{image}">')

        SharedObjects.is_right_pdf_is_image = True

    def fill_left_side_with_text(self, pages_dict):
        """ Fill Left Side With Text """
        for page in pages_dict:
            self.textBrowser.append(pages_dict[page])

        SharedObjects.is_left_pdf_is_image = False

    def fill_right_side_with_text(self, pages_dict):
        """ Fill Right Side With Text """
        for page in pages_dict:
            self.textBrowser_2.append(pages_dict[page])

        SharedObjects.is_left_pdf_is_image = False

    def fill_text_browser(self, pages_dict, is_left):
        ''' Fill Text Browser '''
        for page in pages_dict:
            if is_left:
                if pages_dict[page] == "" or pages_dict[page] is None:
                    self.fill_left_side_with_images()
                else:
                    self.fill_left_side_with_text(pages_dict)

                self.textBrowser.append(
                    f" \n========= Page {page + 1} End ======== \n")
            else:
                if pages_dict[page] == "" or pages_dict[page] is None:
                    self.fill_right_side_with_images()
                else:
                    self.fill_right_side_with_text(pages_dict)

                self.textBrowser_2.append(
                    f" \n========= Page {page + 1} End ======== \n")

    def paint_the_different_lines(self):
        ''' Paint the Different Lines '''
        is_line_different = False

        different_lines = '<span style="color:red;">{}</span>'
        same_lines = '<span style="color:black;">{}</span>'

        is_left_pdf_longer = False
        checking_len = len(SharedObjects.imported_left_pdf)
        if len(SharedObjects.imported_right_pdf) < checking_len:
            is_left_pdf_longer = True
            checking_len = len(SharedObjects.imported_right_pdf)

        rest_pages = abs(len(SharedObjects.imported_left_pdf) -
                         len(SharedObjects.imported_right_pdf))

        for page in range(checking_len):
            try:
                lines_right = SharedObjects.imported_right_pdf[page].split(
                    '\n')
                lines_left = SharedObjects.imported_left_pdf[page].split('\n')

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
                        is_line_different = True
                self.textBrowser.append(
                    f" \n========= Page {page + 1} End ======== \n")
                self.textBrowser_2.append(
                    f" \n========= Page {page + 1} End ======== \n")
            except KeyError:
                print("KeyError!")

        # create for loop starting from checking_len till the end of the pages
        for page in range(checking_len, checking_len + rest_pages):
            try:
                if is_left_pdf_longer:
                    lines_left = SharedObjects.imported_left_pdf[page].split(
                        '\n')
                else:
                    lines_right = SharedObjects.imported_right_pdf[page].split(
                        '\n')

                for line_right, line_left in zip(lines_right, lines_left):
                    if is_left_pdf_longer:
                        self.textBrowser.append(
                            different_lines.format(line_left))
                    else:
                        self.textBrowser_2.append(
                            different_lines.format(line_right))

                if is_left_pdf_longer:
                    self.textBrowser.append(
                        f" \n========= Page {page + 1} End ======== \n")
                else:
                    self.textBrowser_2.append(
                        f" \n========= Page {page + 1} End ======== \n")
            except KeyError:
                print("KeyError!")

        return is_line_different

    def make_comparison(self):
        ''' Make Comparison '''
        if SharedObjects.is_left_pdf_opened and SharedObjects.is_right_pdf_opened:
            self.textBrowser.clear()
            self.textBrowser_2.clear()

            is_line_different = self.paint_the_different_lines()

            if SharedObjects.is_left_pdf_is_image is False and SharedObjects.is_right_pdf_is_image is False:
                if is_line_different is False:
                    if SharedObjects.imported_left_pdf == SharedObjects.imported_right_pdf:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Information)
                        msg.setWindowTitle("Compare Result")
                        msg.setText("These files are Binary Same!")
                        x = msg.exec()

    def left_file_dialog(self):
        """ Left File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit.setText(file_path)

        SharedObjects.imported_left_pdf = self.open_pdf(file_path)
        self.fill_text_browser(SharedObjects.imported_left_pdf, is_left=True)

        SharedObjects.is_left_pdf_opened = True
        self.make_comparison()

    def right_file_dialog(self):
        """ Right File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit_2.setText(file_path)

        SharedObjects.imported_right_pdf = self.open_pdf(file_path)
        self.fill_text_browser(SharedObjects.imported_right_pdf, is_left=False)

        SharedObjects.is_right_pdf_opened = True
        self.make_comparison()


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
