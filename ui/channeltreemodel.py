#!/usr/bin/env python
#
# This code is based on
# http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel
# (c) 2009, Virgil Dupras

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from treemodel import TreeNode, TreeModel

class ChannelNode(TreeNode):
    def __init__(self, channel, parent, row):
        self.channel = channel
        super(ChannelNode, self).__init__(parent, row)

    def data(self, column, role):
        if role == Qt.DisplayRole:
            if column == 0:
                return self.channel.name
            elif column == 1:
                return None
            elif column == 2:
                return str(self.channel.datarate)
        elif role == Qt.CheckStateRole:
            if column == 0:
                return Qt.Checked if self.channel.enabled else Qt.Unchecked
            elif column == 1:
                return Qt.Checked if self.channel.acquire else Qt.Unchecked
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
        return False

    def _getChildren(self):
        return []

class ModelNode(TreeNode):
    def __init__(self, model, parent, row):
        self.model = model
        super(ModelNode, self).__init__(parent, row)

    def data(self, column, role):
        if role == Qt.DisplayRole and column == 0:
            return self.model.name
        else:
            return None

    def setData(self, column, value, role):
        return False

    def _getChildren(self):
        return [ChannelNode(chan, self, index)
            for index, chan in enumerate(self.model.channels)]

class ChannelTreeModel(TreeModel):
    def __init__(self, models, parent=None):
        self.models = models
        self.columns = ['Name', 'Acquire', 'Datarate']
        super(ChannelTreeModel, self).__init__(parent)

    def _getRootNodes(self):
        return [ModelNode(model, None, index)
            for index, model in enumerate(self.models)]

    def columnCount(self, parent):
        return len(self.columns)
    
    def flags(self, index):
        if index.parent().isValid():
            node = index.internalPointer()
            enabled = node.channel.enabled
            default = Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
            if index.column() == 0:
                return default | Qt.ItemIsEnabled
            elif index.column() == 1:
                if enabled:
                    return default | Qt.ItemIsEnabled
                else:
                    return default
            else:
                return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        return node.data(index.column(), role)
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        node = index.internalPointer()
        if node.setData(index.column(), value, role):
            left = index.sibling(index.row(), 0)
            right = index.sibling(index.row(), len(self.columns)-1)
            self.dataChanged.emit(left, right)
            return True
        return False  