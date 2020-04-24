from PySide2.QtCore import Qt, QObject, QAbstractItemModel, QModelIndex

from .tree_model_item import TreeModelItem

class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._root = TreeModelItem()
        self._root._model = self

    def root(self):
        return self._root

    def setRoot(self, root):
        self.beginResetModel()

        self._root._model = None
        self._root = root
        self._root._model = self

        self.endResetModel()

    def item(self, index: QModelIndex):
        return index.internalPointer()

    # QAbstractItemModel abstract method implementations ---------------------------------------------------------------
    def flags(self, index: QModelIndex):
        return super().flags(index)

    def data(self, index: QModelIndex, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.item(index).text()
        return None

    def rowCount(self, parent: QModelIndex):
        if parent == QModelIndex():
            item = self._root
        else:
            item = self.item(parent)

        return item.childrenCount()
        
    def columnCount(self, parent=QModelIndex()):
        return 1
    
    def index(self, row, column, parent=QModelIndex()):
        if not (0 <= row < self.rowCount(parent)) or column != 0:
            return QModelIndex()

        if parent == QModelIndex():
            item = self._root
        else:
            item = self.item(parent)

        return item.item(row).modelIndex()
    
    def parent(self, index: QModelIndex):
        item = self.item(index)

        if item.parent() is None:
            return QModelIndex()

        return item.parent().modelIndex()
