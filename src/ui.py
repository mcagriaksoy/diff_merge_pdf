__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'
__version__ = '0.0.2'
__date__ = '2023 January 14'

import sys
import os
import subprocess

try:
    import pdfplumber
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", 'pdfplumber'])
    import pdfplumber

try:
    import ocrmypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'ocrmypdf'])
    import ocrmypdf

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog, QGraphicsScene, QGraphicsPixmapItem
    from PyQt6.QtCore import QThread, pyqtSignal
    from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'PyQt6'])
    from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QInputDialog, QGraphicsScene, QGraphicsPixmapItem
    from PyQt6.QtCore import QThread, pyqtSignal
    from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter

try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'PyMuPDF'])
    import fitz

try:
    from PyQt6.uic import loadUi
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", 'pyqt6-tools'])
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
    started = pyqtSignal()
    finished = pyqtSignal(str)
    msg = None

    def __init__(self, input_file_path, output_file_path, language):
        super().__init__()
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.language = language

    def run(self):
        ''' Run '''
        self.started.emit()
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

        self.popup = QMessageBox(self)
        # set the title
        self.popup.setWindowTitle("Please wait!")
        self.popup.setText("PDF is still processing...")
        self.popup.setStandardButtons(QMessageBox.StandardButton.NoButton)

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
                self.label_6.setText("Failed to delete tmp folder!")

    def open_file_dialog(self):
        """ Open File Dialog """
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   "QFileDialog.getOpenFileName()",
                                                   "",
                                                   "PDF Files (*.pdf)")
        if file_path:
            return file_path

        self.label_6.setText("Please select a PDF file to continue!")
        return None

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

        # Open all pages
        scene = QGraphicsScene()
        y_offset = 0
        for page in doc:
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height,
                         QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)

            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setPos(0, y_offset)
            scene.addItem(pixmap_item)

            y_offset += pixmap.height() + 10  # Add 10 for spacing between pages

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

    def get_color_from_combobox(self, combobox):
        ''' Get Color From Combobox '''
        color = combobox.currentText()
        return color

    def paint_the_different_lines(self):
        """ Paint the Different Lines """
        is_line_different = False
        pdf_equal = False

        different_lines = '<span style="color:{};">{}</span>'.format(
            self.get_color_from_combobox(self.comboBox), '{}')

        same_lines = '<span style="color:{};">{}</span>'.format(
            self.get_color_from_combobox(self.comboBox_2), '{}')

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
                self.label_6.setText("PDF Parsing Error!")

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
                self.label_6.setText("PDF Parsing Error!")

        return is_line_different

    def make_text_comparison(self):
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

    def show_popup(self):
        ''' Show Popup '''
        self.popup.show()

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
            self.label_6.setText("Comparison mode is activated!")
            self.make_text_comparison()
            self.make_visual_comparison()

        self.popup.hide()

    def subtract_img(self, img_l, img_r):
        """ Subtract Images """
        if img_l.size() != img_r.size():
            print("Image sizes are not equal!")
            self.label_6.setText("Image sizes are not equal!")
            return

        result_image = QImage(img_l.size(), QImage.Format.Format_RGB888)

        for x in range(img_l.width()):
            for y in range(img_l.height()):
                color1 = QColor(img_l.pixel(x, y))
                color2 = QColor(img_r.pixel(x, y))

                red = abs(color1.red() - color2.red())
                green = abs(color1.green() - color2.green())
                blue = abs(color1.blue() - color2.blue())
                alpha = abs(color1.alpha() - color2.alpha())

                result_image.setPixelColor(
                    x, y, QColor(red, green, blue, alpha))

        return QPixmap.fromImage(result_image)

    def add_pixmap_to_scene(self, pixmap, scene):
        ''' Create a pixmap item with the diff pixmap '''
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setPos(0, 0)
        # Add the pixmap item to the scene
        scene.addItem(pixmap_item)

    def invert_colors(self, pixmap):
        ''' Invert Colors '''
        image = pixmap.toImage()

        for x in range(image.width()):
            for y in range(image.height()):
                # if pixel is black alpha value is 0
                # else alpha value is 255
                if QColor(image.pixel(x, y)).red() == 0 and QColor(image.pixel(x, y)).green() == 0 and QColor(image.pixel(x, y)).blue() == 0:
                    image.setPixelColor(x, y, QColor(0, 0, 0, 0))
                else:
                    image.setPixelColor(x, y, QColor(255, 255, 255, 255))

                old_color = QColor(image.pixel(x, y))
                new_color = QColor(255 - old_color.red(), 255 - old_color.green(),
                                   255 - old_color.blue(), old_color.alpha())
                image.setPixelColor(x, y, new_color)

        return QPixmap.fromImage(image)

    def make_visual_comparison(self):
        ''' Make Visual Comparison '''
        # compare scenes
        scene_left = self.graphicsView.scene()
        scene_right = self.graphicsView_2.scene()

        # save left scenes as image
        img_l = QImage(scene_left.sceneRect().size().toSize(),
                       QImage.Format.Format_RGB888)
        painter = QPainter(img_l)
        scene_left.render(painter)
        painter.end()
        img_l.save("./tmp/l.png")

        # save right scenes as image
        img_r = QImage(scene_right.sceneRect().size().toSize(),
                       QImage.Format.Format_RGB888)
        painter = QPainter(img_r)
        scene_right.render(painter)
        painter.end()
        img_r.save("./tmp/r.png")

        # make difference between images
        diff = self.subtract_img(img_l, img_r)

        if diff is None:
            return
        # invert colors
        diff2 = self.invert_colors(diff)
        diff2.save("./tmp/diff.png")

        # add diff to scene
        scene = QGraphicsScene()
        self.graphicsView_3.setScene(scene)
        self.add_pixmap_to_scene(diff2, scene)

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
        self.ocr_thread.started.connect(self.show_popup)
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
            "eng", "fra", "deu", "spa", "tur", "ita", "por",
            "nld", "rus", "jpn", "chi_sim", "chi_tra", "kor"
        ], 0, False)

        # If user click OK and select a language return the language
        if languages and ok:
            return languages

        self.label_6.setText("Please select a PDF language to continue!")
        return None

    def clear_if_finished(self):
        ''' Clear If Finished '''
        if "Left" in SharedObjects.current_file and "Right" in SharedObjects.current_file:
            self.clear_all()

    def left_file_dialog(self):
        """ Left File Dialog """
        self.clear_if_finished()
        file_path = self.open_file_dialog()
        if file_path:
            self.lineEdit.setText(file_path)
            lang = self.select_pdf_language()
            if lang:
                SharedObjects.current_file += "Left"
                self.make_ocr(file_path, lang)

    def right_file_dialog(self):
        """ Right File Dialog """
        self.clear_if_finished()
        file_path = self.open_file_dialog()
        if file_path:
            self.lineEdit_2.setText(file_path)
            lang = self.select_pdf_language()
            if lang:
                SharedObjects.current_file += "Right"
                self.make_ocr(file_path, lang)


def start_ui_design():
    """ Start the UI Design """
    app = QApplication(sys.argv)  # Create an instance
    window = MainWindow()  # Create an instance of our class
    app.exec()  # Start the application
