"""Property tree model class, containing the data structure."""
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem

from ..block import Block
from ..group import Group

from .view import PropertyTreeView


class PropertyTree(QStandardItemModel):
    """An item model displaying experiment properties inside the ExperimentView.
    Both this class and PropertyTreeView (the view widget)
    """
    View = PropertyTreeView

    def __init__(self, parent=None):
        super().__init__(parent)
        self._experiment = None

        self.general = QStandardItem("General")
        self.signals = QStandardItem("Signals")
        self.blocks = QStandardItem("Blocks")
        self.groups = QStandardItem("Block Groups")
        self.sequence = QStandardItem("Sequence")

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        self.general.setFlags(flags | Qt.ItemNeverHasChildren)
        self.signals.setFlags(flags | Qt.ItemNeverHasChildren)
        self.blocks.setFlags(flags)
        self.groups.setFlags(flags)
        self.sequence.setFlags(flags | Qt.ItemNeverHasChildren)

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
    
    def addNewBlock(self):
        """Add a new block into the experiment."""
        ex = self.experiment()
        if ex is None:
            return

        ex.blocks[ex.blocks.getName()] = Block()
    
    def addNewGroup(self):
        ex = self.experiment()
        if ex is None:
            return

        ex.groups[ex.groups.getName()] = Group()
    
    def renameBlock(self, old_name, new_name):
        ex = self.experiment()
        if ex is None:
            return
        
        ex.blocks.rename(old_name, new_name)
    
    def renameGroup(self, old_name, new_name):
        ex = self.experiment()
        if ex is None:
            return
        
        ex.groups.rename(old_name, new_name)

    def removeBlock(self, name):
        ex = self.experiment()
        if ex is None:
            return
        
        ex.blocks.pop(name)
    
    def removeGroup(self, name):
        ex = self.experiment()
        if ex is None:
            return
        
        ex.groups.pop(name)
