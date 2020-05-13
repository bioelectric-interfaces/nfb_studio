from PySide2.QtCore import Qt, QObject, QAbstractItemModel, QModelIndex, QPoint
from PySide2.QtWidgets import QTreeView, QMenu, QAction

from nfb_studio.util.qt import TreeModel, TreeModelItem

class PropertyTree(TreeModel):

    class View(QTreeView):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setHeaderHidden(True)
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.showContextMenu)

            # Context menu actions -------------------------------------------------------------------------------------
            self.blocktree_menu = QMenu("Block Tree")
            self.blocktree_menu_add_action = QAction("Add")
            self.blocktree_menu.addAction(self.blocktree_menu_add_action)

            self.block_menu = QMenu("Block")
            self.block_menu_delete_action = QAction("Delete")
            self.block_menu.addAction(self.block_menu_delete_action)

            self.grouptree_menu = QMenu("Group Tree")
            self.grouptree_menu_add_action = QAction("Add")
            self.grouptree_menu.addAction(self.grouptree_menu_add_action)

            self.group_menu = QMenu("Group")
            self.group_menu_delete_action = QAction("Delete")
            self.group_menu.addAction(self.group_menu_delete_action)
        
        def setModel(self, model):
            if not isinstance(model, PropertyTree):
                raise TypeError(
                    "PropertyTree.View can only have PropertyTree as it's model, not " + type(model).__name__)

            super().setModel(model)

        def showContextMenu(self, point: QPoint):
            index = self.indexAt(point)
            if not index.isValid():
                return
            
            item = self.model().item(index)

            if item is self.model().blocks_item:
                self.blocktree_menu.exec_(self.viewport().mapToGlobal(point))
            elif item is self.model().groups_item:
                self.grouptree_menu.exec_(self.viewport().mapToGlobal(point))
            elif item.parent() is self.model().blocks_item:
                self.block_menu.exec_(self.viewport().mapToGlobal(point))
            elif item.parent() is self.model().groups_item:
                self.group_menu.exec_(self.viewport().mapToGlobal(point))

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.general_item = TreeModelItem()
        self.general_item.setText("General")
        self.signals_item = TreeModelItem()
        self.signals_item.setText("Signals")
        self.blocks_item = TreeModelItem()
        self.blocks_item.setText("Blocks")
        self.groups_item = TreeModelItem()
        self.groups_item.setText("Block Groups")

        self.root().addItem(self.general_item)
        self.root().addItem(self.signals_item)
        self.root().addItem(self.blocks_item)
        self.root().addItem(self.groups_item)

    def getView(self):
        """Get a new view, suitable for representing data from this property tree."""
        view = self.View()
        view.setModel(self)

        return view

    def headerData(self, section, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section
            else:
                return "Properties"
        return None
