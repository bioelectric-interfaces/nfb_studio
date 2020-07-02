"""Property tree model class, containing the data structure."""
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem

from .view import PropertyTreeView


class PropertyTree(QStandardItemModel):
    """An item model displaying experiment properties inside the ExperimentView.
    Both this class and PropertyTreeView (the view widget)
    """
    addBlockTriggered = Signal()
    addGroupTriggered = Signal()
    renameBlockTriggered = Signal(QStandardItem, str)
    renameGroupTriggered = Signal(QStandardItem, str)
    removeBlockTriggered = Signal(QStandardItem)
    removeGroupTriggered = Signal(QStandardItem)

    View = PropertyTreeView

    def __init__(self, parent=None):
        super().__init__(parent)
        self._experiment = None

        self.general = QStandardItem("General")
        self.signals = QStandardItem("Signals")
        self.blocks = QStandardItem("Blocks")
        self.groups = QStandardItem("Block Groups")
        self.sequence = QStandardItem("Sequence")

        self.general.setFlags(self.general.flags() | Qt.ItemNeverHasChildren)
        self.signals.setFlags(self.signals.flags() | Qt.ItemNeverHasChildren)
        self.sequence.setFlags(self.sequence.flags() | Qt.ItemNeverHasChildren)

        self.appendRow(self.general)
        self.appendRow(self.signals)
        self.appendRow(self.blocks)
        self.appendRow(self.groups)
        self.appendRow(self.sequence)

    def experiment(self):
        """Get the experiment assosiated with this property tree."""
        return self._experiment
    
    def setExperiment(self, ex):
        self._experiment = ex

    def getView(self):
        """Get a new QTreeView widget configured for displaying the data."""
        v = self.View()
        v.setModel(self)

        return v
