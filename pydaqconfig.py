#!/usr/bin/env python
import sys
from ui.mainwindow import MainWindow
from PyQt4 import QtGui

qApp = QtGui.QApplication(sys.argv)

window = MainWindow()
window.show()
window.raise_()
qApp.exec_()