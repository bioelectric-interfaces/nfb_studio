from PySide2.QtCore import Qt, QObject, QAbstractItemModel, QModelIndex, QPoint, Signal
from PySide2.QtWidgets import QTreeView, QMenu, QAction, QTreeWidget, QTreeWidgetItem

from .delegate import SequenceItemDelegeate

class PropertyTree(QTreeWidget):
    """A tree widget displaying experiment properties inside the ExperimentView.
    Since this widget is entirely contained in the view model, there is no need for model-view separation.
    """
    addBlockTriggered = Signal()
    addGroupTriggered = Signal()
    renameBlockTriggered = Signal(QTreeWidgetItem, str)
    renameGroupTriggered = Signal(QTreeWidgetItem, str)
    removeBlockTriggered = Signal(QTreeWidgetItem)
    removeGroupTriggered = Signal(QTreeWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setItemDelegate(SequenceItemDelegeate())
        self.itemDoubleClicked.connect(self.editItem)

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

        self.general.setFlags(self.general.flags() | Qt.ItemNeverHasChildren)
        self.signals.setFlags(self.signals.flags() | Qt.ItemNeverHasChildren)
        self.sequence.setFlags(self.sequence.flags() | Qt.ItemNeverHasChildren)

        self.addTopLevelItem(self.general)
        self.addTopLevelItem(self.signals)
        self.addTopLevelItem(self.blocks)
        self.addTopLevelItem(self.groups)
        self.addTopLevelItem(self.sequence)
    
    def experiment(self):
        """Get the experiment assosiated with this property tree.
        This function takes the experiment from the ExperimentView, which should be this widget's parent.
        Used in the custom item delegate to check block name validity.
        """
        if self.parent() is None:
            raise ValueError("could not get the experiment because parent is None (should be ExperimentView)")
            
        return self.parent().parent().model()

    def editItem(self, item, column):
        """Called when by some action user wants to edit the item.
        Reimplements base class function to silence the warning when double-clicking non-editable items.
        """
        if item.flags() & Qt.ItemIsEditable:
            super().editItem(item, column)

    def showContextMenu(self, point: QPoint):
        global_point = self.viewport().mapToGlobal(point)
        item = self.itemAt(point)

        if item is self.blocks:
            # Menu for "Blocks" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Block")
            add.triggered.connect(lambda: self.addBlockTriggered.emit())

            menu.exec_(global_point)
        elif item is self.groups:
            # Menu for "Groups" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Group")
            add.triggered.connect(lambda: self.addGroupTriggered.emit())

            menu.exec_(global_point)
        elif item.parent() is self.blocks:
            # Menu for an individual block -----------------------------------------------------------------------------
            menu = QMenu()
            delete = menu.addAction("Delete")
            delete.triggered.connect(lambda: self.removeBlockTriggered.emit(item))

            menu.exec_(global_point)
        elif item.parent() is self.groups:
            # Menu for an individual group -----------------------------------------------------------------------------
            menu = QMenu()
            delete = menu.addAction("Delete")
            delete.triggered.connect(lambda: self.removeGroupTriggered.emit(item))

            menu.exec_(global_point)
