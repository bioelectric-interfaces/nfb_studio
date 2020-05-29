from PySide2.QtCore import Qt, QObject, QAbstractItemModel, QModelIndex, QPoint, Signal
from PySide2.QtWidgets import QTreeView, QMenu, QAction, QTreeWidget, QTreeWidgetItem


class PropertyTree(QTreeWidget):
    """A tree widget displaying experiment properties inside the ExperimentView.
    Since this widget is entirely contained in the view model, there is no need for model-view separation.
    """
    addBlockClicked = Signal()
    addGroupClicked = Signal()
    renameBlockClicked = Signal()
    renameGroupClicked = Signal()
    removeBlockClicked = Signal(QTreeWidgetItem)
    removeGroupClicked = Signal(QTreeWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.general = QTreeWidgetItem()
        self.signals = QTreeWidgetItem()
        self.blocks = QTreeWidgetItem()
        self.groups = QTreeWidgetItem()
        self.sequence = QTreeWidgetItem()

        self.general.setText(0, "General")
        self.signals.setText(0, "Signals")
        self.blocks.setText(0, "Blocks")
        self.groups.setText(0, "Block Groups")
        self.sequence.setText(0, "Sequence")

        self.addTopLevelItem(self.general)
        self.addTopLevelItem(self.signals)
        self.addTopLevelItem(self.blocks)
        self.addTopLevelItem(self.groups)
        self.addTopLevelItem(self.sequence)
    
    def showContextMenu(self, point: QPoint):
        global_point = self.viewport().mapToGlobal(point)
        item = self.itemAt(point)

        if item is self.blocks:
            # Menu for "Blocks" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Block")
            add.triggered.connect(lambda: self.addBlockClicked.emit())

            menu.exec_(global_point)
        elif item is self.groups:
            # Menu for "Groups" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Group")
            add.triggered.connect(lambda: self.addGroupClicked.emit())

            menu.exec_(global_point)
        elif item.parent() is self.blocks:
            # Menu for an individual block -----------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("Delete")
            add.triggered.connect(lambda: self.removeBlockClicked.emit(item))

            menu.exec_(global_point)
        elif item.parent() is self.groups:
            # Menu for an individual group -----------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("Delete")
            add.triggered.connect(lambda: self.removeGroupClicked.emit(item))

            menu.exec_(global_point)
