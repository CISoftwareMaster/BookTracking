#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import QApplication
from classes.bm_main_window import BM_Main_Window


if __name__ == "__main__":
    # initialise this Qt application
    app = QApplication(sys.argv)

    # initialise the main window
    window = BM_Main_Window()
    window.show()

    # enter the main loop
    sys.exit(app.exec_())
