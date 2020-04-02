from PySide2.QtCore import Qt, QMimeData, QAbstractListModel, QModelIndex
from PySide2.QtWidgets import QListView
from sortedcontainers import SortedDict

from nfb_studio.serial import mime, hooks
from .scheme import Node

class Toolbox(QAbstractListModel):
    """A list of signal nodes that can be dragged to the scheme.
    """

    DragMimeType = "application/x-toolbox-drag"

    def __init__(self, parent):
        super().__init__(parent)

        self._items = SortedDict()

    def getView(self):
        """Get a QListView suitable for displaying the toolbox."""
        view = QListView()
        view.setModel(self)

        view.setSelectionMode(view.SingleSelection)
        view.setDragEnabled(True)
        view.setDragDropMode(view.DragOnly)

        return view

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role = Qt.DisplayRole):
        i = index.row()

        if role == Qt.DisplayRole:
            return self._items.peekitem(i)[0]
        return None

    def headerData(self, section, orientation: Qt.Orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            else:
                return "Node toolbox"
        return None

    def addItem(self, name, item):
        i = self._items.bisect_right(name)

        self.beginInsertRows(QModelIndex(), i, i)
        self._items[name] = item
        self.endInsertRows()

    def flags(self, index: QModelIndex):
        default_flags = super().flags(index)

        if index.isValid():
            return default_flags | Qt.ItemIsDragEnabled
        return default_flags

    def mimeTypes(self):
        return [self.DragMimeType]
    
    def mimeData(self, indexes):
        assert(len(indexes) == 1)
        i = indexes[0].row()

        package = QMimeData()
        mime.dump(self._items.peekitem(i)[1], package, self.DragMimeType, hooks=hooks.qt)

        return package
    
    def serialize(self) -> dict:
        return self._items
    
    def deserialize(self, data: dict):
        self._items = data