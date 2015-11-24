#!/usr/bin/env python
#
# This code is based on
# http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel
# (c) 2009, Virgil Dupras

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from treemodel import TreeNode, TreeModel
from daq.daqchannel import DAQChannelBitrateTooHigh

class ChannelNode(TreeNode):
    def __init__(self, channel, parent, row):
        self.channel = channel
        super(ChannelNode, self).__init__(parent, row)

    def data(self, column, role):
        if role == Qt.DisplayRole:
            if column == 0:
                return self.channel.short_name
            elif column == 1:
                return None
            elif column == 2:
                return str(self.channel.datarate)
            elif column == 3:
                # acquisition rate in MiB/h
                return '{0:.1f}'.format(round(self.channel.get_acquisition_rate() / 1048576.0 * 3600,1))
        elif role == Qt.CheckStateRole:
            if column == 0:
                return Qt.Checked if self.channel.enabled else Qt.Unchecked
            elif column == 1:
                return Qt.Checked if self.channel.acquire else Qt.Unchecked
        elif role == Qt.EditRole:
            if column == 2:
                return self.channel.datarate
        elif role == Qt.SizeHintRole and column==2:
            return QSize(50,24)
        return None

    def setData(self, column, value, role):
        if role == Qt.CheckStateRole:
            val = value.toBool()
            if column == 0:
                self.channel.enabled = val
                return True
            elif column == 1:
                self.channel.acquire = val
                return True
        elif role == Qt.EditRole:
            if column == 2:
                try:
                    self.channel.datarate = value
                    
                    # update acquisition rate
                    self.data(3, Qt.DisplayRole)
                    
                    return True
                except DAQChannelBitrateTooHigh as e:
                    self.channel.datarate = e.maxdatarate
                    QMessageBox.critical(None, 'Data Rate Too High',
                        'This model has a maximum data rate of {0} samples/sec.'.format(e.maxdatarate))
                    return True
        return False

    def _getChildren(self):
        return []

class ModelNode(TreeNode):
    def __init__(self, model, parent, row):
        self.model = model
        super(ModelNode, self).__init__(parent, row)

    def data(self, column, role):
        if role == Qt.DisplayRole:
            if column == 0:
                return str(self.model)
            #elif column == 1 and self.model.archived:
            #    return self.model.archive_string
            elif column == 2:
                # show model max data rate
                return str(self.model.datarate)
            elif column == 3:
                # total model acquisition rate in MiB/h
                return '{0:.1f}'.format(round(self.model.get_acquisition_rate() / 1048576.0 * 3600,1))
        return None

    def setData(self, column, value, role):
        return False

    def _getChildren(self):
        return [ChannelNode(chan, self, index)
            for index, chan in enumerate(self.model.channels)]

class ChannelTreeModel(TreeModel):
    def __init__(self, models, parent=None):
        self.models = models
        self.columns = ['Name', 'Acquire', 'Samples/s', 'MiB/h']
        super(ChannelTreeModel, self).__init__(parent)

    def empty(self):
        self.models = []
        self.reset()

    def populate(self, models):
        self.models = models
        self.reset()

    def signal_update(self):
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def _getRootNodes(self):
        return [ModelNode(model, None, index)
            for index, model in enumerate(self.models)]

    def columnCount(self, parent):
        return len(self.columns)
    
    def flags(self, index):
        if index.parent().isValid():
            node = index.internalPointer()
            enabled = node.channel.enabled
            default = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            if not node.channel.archived:
                default |= Qt.ItemIsUserCheckable 
            if index.column() == 0:
                return default
            elif index.column() == 1:
                if enabled:
                    return default
                else:
                    return (default & ~Qt.ItemIsEnabled)
            elif index.column() == 2:
                if node.channel.archived:
                    return Qt.ItemIsSelectable | Qt.ItemIsEnabled
                return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.data(index.column(), role)
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        node = index.internalPointer()
        if node.setData(index.column(), value, role):
            left = index.sibling(index.row(), 0)
            right = index.sibling(index.row(), len(self.columns)-1)
            self.dataChanged.emit(left, right)
            return True
        return False  

class ComboDelegate(QItemDelegate):
    def __init__(self, values, parent):
        super(ComboDelegate, self).__init__(parent)
        self.keys, self.values = zip(*values)
        
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.keys)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo
        
    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        data = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(self.values.index(data))
        editor.blockSignals(False)
        
    def setModelData(self, editor, model, index):
        data = self.values[self.keys.index(str(editor.currentText()))]
        model.setData(index, data)
        
    @pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
