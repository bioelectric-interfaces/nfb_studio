from PySide2.QtCore import Qt, QMimeData, QAbstractListModel, QModelIndex

from nfb_studio.serial import mime, hooks
from .scheme.node import Node

class NodeToolboxModel(QAbstractListModel):
    def __init__(self, parent):
        super().__init__(parent)

        self.example_node = Node()

    def rowCount(self, parent=QModelIndex()):
        return 3

    def data(self, index: QModelIndex, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return "Node" + str(index.row())
        return None

    def flags(self, index: QModelIndex):
        default_flags = super().flags(index)

        if index.isValid():
            return default_flags | Qt.ItemIsDragEnabled
        return default_flags

    def mimeTypes(self):
        return ["application/x-toolbox-node"]
    
    def mimeData(self, indexes):
        assert(len(indexes) == 1)

        self.example_node.setTitle("Node " + str(indexes[0].row()))

        package = QMimeData()
        mime.dump(self.example_node, package, "application/x-toolbox-node", hooks=hooks.qt)

        return package