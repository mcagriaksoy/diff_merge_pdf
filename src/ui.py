__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys
import os
import pdfplumber
import ocrmypdf

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog, QGraphicsScene
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import fitz

from PyQt6.uic import loadUi


class SharedObjects():
    """ Shared Objects """

    def __init__(self):
        """ Clear """
        self.current_file = ""
        self.imported_left_pdf = {}
        self.imported_right_pdf = {}

    current_file = ""
    imported_left_pdf = {}
    imported_right_pdf = {}


class OcrThread(QThread):
    ''' Ocr Thread '''
    finished = pyqtSignal(str)

    def __init__(self, input_file_path, output_file_path, language):
        super().__init__()
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.language = language

    def run(self):
        ''' Run '''
        retval = ocrmypdf.ExitCode.ctrl_c
        while retval == ocrmypdf.ExitCode.ctrl_c:
            try:
                retval = ocrmypdf.ocr(self.input_file_path,
                                      self.output_file_path, language=self.language)
            except:
                retval = ocrmypdf.ExitCode.pdfa_conversion_failed
                break

        if retval != ocrmypdf.ExitCode.ok:
            # Use the input file path
            self.finished.emit(self.input_file_path)
        elif not os.path.exists(self.output_file_path):
            # Use the input file path
            self.finished.emit(self.input_file_path)
        else:
            # Use the output file path (success case!)
            self.finished.emit(self.output_file_path)

        return


class MainWindow(QMainWindow):
    """ Main Window Class """

    def __init__(self):
        # Call the inherited classes __init__ method
        super(MainWindow, self).__init__()
        loadUi('ui.ui', self)  # Load the .ui file
        self.show()  # Show the GUI
        self.msg = None

        self.pushButton.clicked.connect(self.left_file_dialog)
        self.pushButton_2.clicked.connect(self.right_file_dialog)
        self.clearButton.clicked.connect(self.clear_all)

    def clear_all(self):
        """ Clear All """
        self.textBrowser.clear()
        self.textBrowser_2.clear()
        self.lineEdit.clear()
        self.lineEdit_2.clear()

        self.graphicsView.setScene(None)
        self.graphicsView_2.setScene(None)

        # Init the SharedObjects
        SharedObjects.current_file = ""
        SharedObjects.imported_left_pdf = {}
        SharedObjects.imported_right_pdf = {}

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

    def fill_left_side_with_text(self, pages_dict):
        """ Fill Left Side With Text """
        for page in pages_dict:
            self.textBrowser.append(pages_dict[page])

    def fill_right_side_with_text(self, pages_dict):
        """ Fill Right Side With Text """
        for page in pages_dict:
            self.textBrowser_2.append(pages_dict[page])

    def fill_graphic_browser(self, file_path, is_left):
        """ Fill Graphic Browser """
        doc = fitz.open(file_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = QImage(pix.samples, pix.width, pix.height,
                     QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        if is_left:
            self.graphicsView.setScene(scene)
        else:
            self.graphicsView_2.setScene(scene)

    def fill_text_browser(self, pages_dict, is_left):
        """ Fill Text Browser """
        for page in pages_dict:
            if is_left:
                self.fill_left_side_with_text(pages_dict)

                self.textBrowser.append(
                    f" \n========= Page {page + 1} End ======== \n")
            else:
                self.fill_right_side_with_text(pages_dict)

                self.textBrowser_2.append(
                    f" \n========= Page {page + 1} End ======== \n")

    def paint_the_different_lines(self):
        """ Paint the Different Lines """
        is_line_different = False
        pdf_equal = False

        different_lines = '<span style="color:red;">{}</span>'
        same_lines = '<span style="color:black;">{}</span>'

        is_left_pdf_longer = False
        checking_len = len(SharedObjects.imported_left_pdf)
        if len(SharedObjects.imported_right_pdf) < checking_len:
            is_left_pdf_longer = True
            checking_len = len(SharedObjects.imported_right_pdf)

        elif len(SharedObjects.imported_right_pdf) == checking_len:
            pdf_equal = True

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

        if pdf_equal:
            return is_line_different

        # create for loop starting from checking_len till the end of the pages
        for page in range(checking_len, checking_len + rest_pages):
            try:
                if is_left_pdf_longer:
                    rest_lines = SharedObjects.imported_left_pdf[page].split(
                        '\n')
                else:
                    rest_lines = SharedObjects.imported_right_pdf[page].split(
                        '\n')

                for rest_left in zip(rest_lines):
                    if is_left_pdf_longer:
                        self.textBrowser.append(
                            different_lines.format(rest_left))
                    else:
                        self.textBrowser_2.append(
                            different_lines.format(rest_left))

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
        self.textBrowser.clear()
        self.textBrowser_2.clear()

        is_line_different = self.paint_the_different_lines()
        if is_line_different is False:
            if SharedObjects.imported_left_pdf == SharedObjects.imported_right_pdf:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Compare Result")
                msg.setText("These files are Binary Same!")
                x = msg.exec()
                return

    def close_popup(self, msg):
        ''' Close Popup '''
        msg.close()

    def on_ocr_finished(self, output_file_path):
        ''' On OCR Finished '''
        if "Left" == SharedObjects.current_file or "RightLeft" == SharedObjects.current_file:
            SharedObjects.imported_left_pdf = self.open_pdf(output_file_path)
            self.fill_text_browser(
                SharedObjects.imported_left_pdf, is_left=True)

            self.fill_graphic_browser(output_file_path, is_left=True)

        if "Right" == SharedObjects.current_file or "LeftRight" == SharedObjects.current_file:
            SharedObjects.imported_right_pdf = self.open_pdf(output_file_path)
            self.fill_text_browser(
                SharedObjects.imported_right_pdf, is_left=False)
            self.fill_graphic_browser(output_file_path, is_left=False)

        if "Left" in SharedObjects.current_file and "Right" in SharedObjects.current_file:
            print("Both files are selected!")
            self.make_comparison()

    def make_ocr(self, input_file_path, language):
        ''' Make OCR '''
        # make a copy of the input file on tmp folder
        # and make ocr on the tmp folder
        base_name = os.path.basename(input_file_path)

        name, ext = os.path.splitext(base_name)
        output_file_name = f"{name}_ocr{ext}"

        # create tmp folder if not exists
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')

        output_file_path = os.path.join('./', 'tmp', output_file_name)

        self.ocr_thread = OcrThread(
            input_file_path, output_file_path, language)
        self.ocr_thread.finished.connect(self.on_ocr_finished)
        self.ocr_thread.start()
        # if output path does not exist return input file path
        # else return output file path

        # it happens when the pdf does not occur any image that for ocr!
        if not os.path.exists(output_file_path):
            return input_file_path

        return output_file_path

    def select_pdf_language(self):
        ''' Select PDF Language '''
        # Create a popup for language selection
        languages, ok = QInputDialog.getItem(self, "Select The Pdf Language", "Language:", [
            "eng", "fra", "deu", "spa", "tur", "ita", "por", "nld", "rus", "jpn", "chi_sim", "chi_tra", "kor"
        ], 0, False)
        return languages

    def clear_if_finished(self):
        ''' Clear If Finished '''
        if "Left" in SharedObjects.current_file and "Right" in SharedObjects.current_file:
            self.clear_all()

    def left_file_dialog(self):
        """ Left File Dialog """
        self.clear_if_finished()
        file_path = self.open_file_dialog()
        self.lineEdit.setText(file_path)

        SharedObjects.current_file += "Left"
        self.make_ocr(file_path, self.select_pdf_language())

    def right_file_dialog(self):
        """ Right File Dialog """
        self.clear_if_finished()
        file_path = self.open_file_dialog()
        self.lineEdit_2.setText(file_path)

        SharedObjects.current_file += "Right"
        self.make_ocr(file_path, self.select_pdf_language())


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
