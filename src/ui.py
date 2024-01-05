__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys
import os
import pdfplumber

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from PyQt6.uic import loadUi

IS_LEFT_OPEN = False
IS_RIGHT_OPEN = False

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
        self.clearButton.clicked.connect(self.clear_all)

    def clear_all(self):
        """ Clear All """
        self.textBrowser.clear()
        self.textBrowser_2.clear()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        # delete tmp folder
        for filename in os.listdir("tmp"):
            file_path = os.path.join("tmp", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' %
                      (file_path, e))

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
                image_obj.save("tmp/tmp_{}.jpeg".format(page.page_number))

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

    def fill_text_browser(self, pages_dict, left_or_right):
        ''' Fill Text Browser '''
        for page in pages_dict:
            if left_or_right == "left":
                if pages_dict[page] == "" or pages_dict[page] is None:
                    self.save_images(self.lineEdit.text())
                    images = self.get_images()
                    self.textBrowser.append(
                        '<img src="{}">'.format(images[page]))
                else:
                    self.textBrowser.append(pages_dict[page])

                self.textBrowser.append(
                    f" \n========= Page {page + 1} End ======== \n")
            else:
                if pages_dict[page] == "" or pages_dict[page] is None:
                    self.save_images(self.lineEdit_2.text())
                    images = self.get_images()
                    self.textBrowser_2.append(
                        '<img src="{}">'.format(images[page]))
                else:
                    self.textBrowser_2.append(pages_dict[page])
                self.textBrowser_2.append(
                    f" \n========= Page {page + 1} End ======== \n")

    def make_comparison(self):
        ''' Make Comparison '''
        if IS_LEFT_OPEN and IS_RIGHT_OPEN:
            different_lines = '<span style="color:red;">{}</span>'
            same_lines = '<span style="color:black;">{}</span>'

            lines_are_different = False

            # get page count
            checking_len = len(pages_dict_left)
            if len(pages_dict_right) > checking_len:
                checking_len = len(pages_dict_right)

            for page in range(checking_len):
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
                        lines_are_different = True

                self.textBrowser.append(
                    f" \n========= Page {page + 1} End ======== \n")
                self.textBrowser_2.append(
                    f" \n========= Page {page + 1} End ======== \n")

            if lines_are_different is False:
                if pages_dict_left == pages_dict_right:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setWindowTitle("Compare Result")
                    msg.setText("These files are Binary Same!")
                    x = msg.exec()

    def left_file_dialog(self):
        """ Left File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit.setText(file_path)

        global pages_dict_left
        pages_dict_left = self.open_pdf(file_path)
        self.fill_text_browser(pages_dict_left, "left")

        global IS_LEFT_OPEN
        IS_LEFT_OPEN = True

        self.make_comparison()

    def right_file_dialog(self):
        """ Right File Dialog """
        file_path = self.open_file_dialog()
        self.lineEdit_2.setText(file_path)

        global pages_dict_right
        pages_dict_right = self.open_pdf(file_path)
        self.fill_text_browser(pages_dict_right, "right")

        global IS_RIGHT_OPEN
        IS_RIGHT_OPEN = True

        self.make_comparison()


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
