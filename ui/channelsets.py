from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import glob

from daq import utils


class ChannelSet(object):
    def __init__(self, name, channels=[]):
        self.name = name
        self.channels = channels
        
    def __iter__(self):
        return iter(self.channels)

    @staticmethod
    def from_file(name, fp):
        channels = []
        for line in fp:
            if not line.startswith('#'):
                channels.append(line.strip())
        return ChannelSet(name, channels)


CHANSET_ACTIVATE = QDialog.Accepted + 1
CHANSET_DEACTIVATE = CHANSET_ACTIVATE + 1

class ChannelSetsDialog(QDialog):
    def __init__(self, parent, directory):
        super(ChannelSetsDialog, self).__init__(parent)
        uic.loadUi('ui/channelsets.ui', self)
        
        self._channelsets = []
        self.load_sets(directory)
        self.update_set_list()

    def load_sets(self, directory):
        for fn in glob.glob(directory+'/*.set'):
            print 'Loading {0}...'.format(fn)
            with open(fn, 'r') as fp:
                self._channelsets.append(
                    ChannelSet.from_file(utils.get_filename_without_ext(fn), fp)
                )

    def update_set_list(self):
        self.lstChanSets.addItems([s.name for s in self._channelsets])
        self.lstChanSets.setCurrentRow(0)

    def get_channel_set(self):
        row = self.lstChanSets.currentRow()
        if row < 0:
            return []
        else:
            return self._channelsets[row]

    @pyqtSlot()
    def on_btnActivate_clicked(self):
        self.done(CHANSET_ACTIVATE)

    @pyqtSlot()
    def on_btnDeactivate_clicked(self):
        self.done(CHANSET_DEACTIVATE)
