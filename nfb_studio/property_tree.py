from PySide2.QtCore import Qt, QObject, QAbstractItemModel, QModelIndex
from PySide2.QtWidgets import QTreeView

from nfb_studio.util.qt import TreeModel, TreeModelItem

class PropertyTree(TreeModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        general_item = TreeModelItem()
        general_item.setText("General")
        signals_item = TreeModelItem()
        signals_item.setText("Signals")
        blocks_item = TreeModelItem()
        blocks_item.setText("Blocks")
        groups_item = TreeModelItem()
        groups_item.setText("Block Groups")

        self.root().addItem(general_item)
        self.root().addItem(signals_item)
        self.root().addItem(blocks_item)
        self.root().addItem(groups_item)
        self.root().setSortingEnabled(True)

        test_item = TreeModelItem()
        test_item.setText("Derived signal 1")

        signals_item.addItem(test_item)

    def view(self):
        view = QTreeView()
        view.setModel(self)

        view.setHeaderHidden(True)

        return view

    def headerData(self, section, orientation: Qt.Orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            else:
                return "Properties"
        return None
