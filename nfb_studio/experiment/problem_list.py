import os
from PySide2.QtCore import Qt, QPointF, QMimeData, QAbstractListModel, QModelIndex
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QListView
from sortedcontainers import SortedList

import nfb_studio
from nfb_studio.serial import mime, hooks


class Message:
    Info = 2
    Warning = 1
    Error = 0

    InfoIcon = QIcon(nfb_studio.icons + "/info.svg")
    WarningIcon = QIcon(nfb_studio.icons + "/warning.svg")
    ErrorIcon = QIcon(nfb_studio.icons + "/error.svg")

    def __init__(self, severity, text):
        self.severity = severity
        self.text = text
    
    @property
    def icon(self):
        if self.severity == self.Info:
            return self.InfoIcon
        if self.severity == self.Warning:
            return self.WarningIcon
        if self.severity == self.Error:
            return self.ErrorIcon
        return None

    def __lt__(self, other):
        return self.severity < other.severity

    @classmethod
    def error(cls, text):
        return cls(cls.Error, text)
    
    @classmethod
    def warning(cls, text):
        return cls(cls.Warning, text)
    
    @classmethod
    def info(cls, text):
        return cls(cls.Info, text)


class ProblemList(QAbstractListModel):
    """A list of errors in the current project. All errors must be fixed before exporting."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._items = SortedList()
        self._items.add(Message.error("No elements in sequence"))
        self._items.add(Message.warning("Composite Signal \"Signal1\" missing inputs"))

    def getView(self):
        """Get a new QListView suitable for displaying the toolbox."""
        v = QListView()
        v.setModel(self)

        v.setSelectionMode(v.SingleSelection)
        return v

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i = index.row()

        if role == Qt.DisplayRole:
            return self._items[i].text
        if role == Qt.DecorationRole:
            return self._items[i].icon
        return None

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            return "Problems"
        return None

    def addItem(self, item):
        i = self._items.bisect_right(item)

        self.beginInsertRows(QModelIndex(), i, i)
        self._items.add(item)
        self.endInsertRows()

    def removeItem(self, item):
        """Remove an item with a specified name from a toolbox.
        If an item with such a name does not exist, does nothing.
        """
        if item not in self._items:
            return
        
        i = self._items.index(item)

        self.beginRemoveRows(QModelIndex(), i, i)
        self._items.remove(item)
        self.endRemoveRows()

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        return self._items
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = cls()
        obj._items = data

        return obj
