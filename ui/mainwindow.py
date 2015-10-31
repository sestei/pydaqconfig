from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

from daq import daqmodel, utils
from channeltreemodel import ChannelTreeModel

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('ui/mainwindow.ui', self)
        self._models = self.load_models()
        self.load_models()

        self._tvmodel = ChannelTreeModel(self._models, parent=self)
        self.twChannels.setModel(self._tvmodel)
        self.twChannels.expanded.connect(self.resize_columns)

    def load_models(self):
        #TODO: automatically load these, based on ENV variable or so
        filename = 'examples/G2SSM.ini'
        ini = open(filename, 'rb')
        dm = daqmodel.DAQModel.from_ini(utils.get_model_name(filename), ini)

        return [dm]

    @pyqtSlot()
    def resize_columns(self):
        for col in range(self.twChannels.model().columnCount(None)):
            self.twChannels.resizeColumnToContents(col)
