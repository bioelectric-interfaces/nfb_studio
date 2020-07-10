from PySide2.QtCore import Qt, QPointF, QMimeData, QAbstractListModel, QModelIndex
from PySide2.QtWidgets import QListView
from sortedcontainers import SortedDict

from nfb_studio.serial import mime, hooks

class Toolbox(QAbstractListModel):
    """A list of scheme nodes that can be dragged to the scheme.
    """

    DragMimeType = "application/x-toolbox-drag"
    """Toolbox assumes that all its items have the same MIME type."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._items = SortedDict()

    def getView(self):
        """Get a new QListView suitable for displaying the toolbox."""
        v = QListView()
        v.setModel(self)

        v.setSelectionMode(v.SingleSelection)
        v.setDragEnabled(True)
        v.setDragDropMode(v.DragOnly)

        return v

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i = index.row()

        if role == Qt.DisplayRole:
            return self._items.peekitem(i)[0]
        return None

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            return "Node toolbox"
        return None

    def addItem(self, name, item):
        i = self._items.bisect_right(name)

        self.beginInsertRows(QModelIndex(), i, i)
        self._items[name] = item
        self.endInsertRows()

    def removeItem(self, name):
        """Remove an item with a specified name from a toolbox.
        If an item with such a name does not exist, does nothing.
        """
        if name not in self._items:
            return None
        
        i = self._items.index(name)

        self.beginRemoveRows(QModelIndex(), i, i)
        item = self._items.pop(name)
        self.endRemoveRows()

        return item

    def flags(self, index: QModelIndex):
        default_flags = super().flags(index)

        if index.isValid():
            return default_flags | Qt.ItemIsDragEnabled
        return default_flags

    def mimeTypes(self):
        return [self.DragMimeType]
    
    def mimeData(self, indexes):
        assert len(indexes) == 1
        i = indexes[0].row()

        package = QMimeData()
        mime.dump(self._items.peekitem(i)[1], package, self.DragMimeType, hooks=hooks.qt)

        return package
    
    def schemeDropEvent(self, scheme, event):
        """Event to be executed when an item from this toolbox gets dropped into a scheme.
        This function can be added as a custom drop event for this toolbox's MIME type, which is usually done by the
        SchemeEditor.
        """
        package = event.mimeData()
        node = mime.load(package, self.DragMimeType, hooks=hooks.qt)

        pos = event.scenePos() - QPointF(
            node.boundingRect().size().width()/2,
            node.boundingRect().size().height()/2
        )
        node.setPos(pos)
        scheme.addItem(node)

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        return self._items
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = cls()
        obj._items = data

        return obj
