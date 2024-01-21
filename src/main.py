# -*- coding: utf-8 -*-
__author__ = "Mehmet Cagri Aksoy - github.com/mcagriaksoy"
__copyright__ = "Copyright 2024, The PDF diff and merge tool"
__credits__ = ["Mehmet Cagri Aksoy"]
__version__ = "0.0.3"
__maintainer__ = "Mehmet Cagri Aksoy"
__status__ = "Pre-alpha"

from ui import start_ui_design
import subprocess
import sys


def install_tesseract():
    ''' Install Tesseract '''
    try:
        # Try to run the "tesseract" command
        subprocess.run(["tesseract"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        # If the command failed, Tesseract is not installed
        print("Tesseract is not installed. Installing now...")

        if sys.platform.startswith('win32'):
            print("Please download the installer from https://github.com/UB-Mannheim/tesseract/wiki and install it manually.")
        elif sys.platform.startswith('linux'):
            # Install Tesseract on Linux
            subprocess.run(["sudo", "apt-get", "install",
                           "tesseract-ocr"], check=True)
        elif sys.platform.startswith('darwin'):
            # Install Tesseract on macOS
            subprocess.run(["brew", "install", "tesseract"], check=True)


if __name__ == "__main__":
    install_tesseract()
    start_ui_design()
