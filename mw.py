#!/usr/bin/env python

import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic

MW_Ui, MW_Base = uic.loadUiType('agak.ui')

class MainWindow(MW_Base, MW_Ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.show()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
