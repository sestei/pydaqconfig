from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic


class ChannelSetsDialog(QDialog):
    def __init__(self, directory, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('ui/channelsets.ui', self)

        self.load_sets(directory)

    def self.load_sets(self, directory):
        pass
