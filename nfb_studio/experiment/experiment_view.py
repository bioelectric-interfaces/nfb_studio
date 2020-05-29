import os

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QAction, QFileDialog, QTreeWidgetItem

from nfb_studio.block import Block, BlockView
from nfb_studio.group import Group, GroupView
from nfb_studio.util import StackedDictWidget
from nfb_studio.widgets.scheme import SchemeEditor
from nfb_studio.widgets.signal_nodes import *
from nfb_studio.widgets.sequence_nodes import *

from .general_view import GeneralView
from .experiment import Experiment
from .property_tree import PropertyTree


class ExperimentView(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._model = None

        # Property tree ------------------------------------------------------------------------------------------------
        self.tree = PropertyTree()
        self.tree.currentItemChanged.connect(self.setCurrentWidget)
        self.tree.addBlockClicked.connect(self.addNewBlock)
        self.tree.addGroupClicked.connect(self.addNewGroup)
        self.tree.removeBlockClicked.connect(lambda item: self.removeBlock(item.text(0)))
        self.tree.removeGroupClicked.connect(lambda item: self.removeGroup(item.text(0)))

        # Property tree dock widget ------------------------------------------------------------------------------------
        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self.tree)
        self.property_tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_tree_dock)

        # Editing widgets ----------------------------------------------------------------------------------------------
        self.general_view = GeneralView()
        
        self.signal_editor = SchemeEditor()
        self.signal_editor.toolbox().addItem("LSL Input", LSLInput())
        self.signal_editor.toolbox().addItem("Spatial Filter", SpatialFilter())
        self.signal_editor.toolbox().addItem("Bandpass Filter", BandpassFilter())
        self.signal_editor.toolbox().addItem("Envelope Detector", EnvelopeDetector())
        self.signal_editor.toolbox().addItem("Standardise", Standardise())
        self.signal_editor.toolbox().addItem("Signal Export", DerivedSignalExport())

        self.blocks = StackedDictWidget()
        self.groups = StackedDictWidget()

        # Sequence editor ----------------------------------------------------------------------------------------------
        self.sequence_editor = SchemeEditor()

        # Central widget -----------------------------------------------------------------------------------------------
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.general_view)
        self.central_widget.addWidget(self.signal_editor)
        self.central_widget.addWidget(self.blocks)
        self.central_widget.addWidget(self.groups)
        self.central_widget.addWidget(self.sequence_editor)

    def model(self):
        return self._model
    
    def setModel(self, model, /):
        self._model = model

        self.signal_editor.setScheme(model.signal_scheme)
        self.sequence_editor.setScheme(model.sequence_scheme)

        model.blocks.itemAdded.connect(self._onBlockAdded)
        model.blocks.itemRemoved.connect(self._onBlockRemoved)
        model.groups.itemAdded.connect(self._onGroupAdded)
        model.groups.itemRemoved.connect(self._onGroupRemoved)

        model._view = self
        model.updateView()

    def updateModel(self):
        ex = self.model()
        if ex is None:
            return
        
        # For each block, write it's data to the experiment
        for name in self.blocks.keys():
            block_view: BlockView = self.blocks.widget(name)
            block_view.updateModel()
        
        # For each group, write its data to the experiment
        for name in self.groups.keys():
            group_view: GroupView = self.groups.widget(name)
            group_view.updateModel()

        # Write general experiment data
        self.general_view.updateModel(ex)

    def addNewBlock(self):
        """Add a new block into the experiment."""
        ex = self.model()
        if ex is None:
            return

        ex.blocks[ex.blocks.getName()] = Block()
    
    def addNewGroup(self):
        ex = self.model()
        if ex is None:
            return

        ex.groups[ex.groups.getName()] = Group()
    
    def removeBlock(self, name):
        ex = self.model()
        if ex is None:
            return
        
        ex.blocks.pop(name)
    
    def removeGroup(self, name):
        ex = self.model()
        if ex is None:
            return
        
        ex.groups.pop(name)

    def setCurrentWidget(self, item):
        """Set central widget in the main window to display config info for item in the property tree."""        
        if item is self.tree.general:
            # General
            self.central_widget.setCurrentWidget(self.general_view)
        elif item is self.tree.signals:
            # Signal editor
            self.central_widget.setCurrentWidget(self.signal_editor)
        elif item.parent() is self.tree.blocks:
            # A block
            self.central_widget.setCurrentWidget(self.blocks)
            self.blocks.setCurrentKey(item.text(0))
        elif item.parent() is self.tree.groups:
            # A group
            self.central_widget.setCurrentWidget(self.groups)
            self.groups.setCurrentKey(item.text(0))
        elif item is self.tree.sequence:
            # Sequence editor
            self.central_widget.setCurrentWidget(self.sequence_editor)

    def _onBlockAdded(self, name):
        """Function that gets called when a new block has been added to the model."""
        # Add an item to the property tree
        tree_item = QTreeWidgetItem()
        tree_item.setText(0, name)
        self.tree.blocks.addChild(tree_item)
        
        # Add a view to the widget stack
        block_view = BlockView()
        block_view.setModel(self.model().blocks[name])
        self.blocks.addWidget(name, block_view)

        # Add a node to draw the sequence
        node = BlockNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)

        # Select this item
        self.tree.setCurrentItem(tree_item)
    
    def _onGroupAdded(self, name):
        """Function that gets called when a new group has been added to the model."""
        # Add an item to the property tree
        tree_item = QTreeWidgetItem()
        tree_item.setText(0, name)
        self.tree.groups.addChild(tree_item)

        # Add a view to the widget stack
        group_view = GroupView()
        group_view.setModel(self.model().groups[name])
        self.groups.addWidget(name, group_view)

        # Add a node to draw the sequence
        node = GroupNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)

        # Select this item
        self.tree.setCurrentItem(tree_item)
    
    def _onBlockRemoved(self, name):
        """Function that gets called when a block has been removed from the model."""
        # Find and remove it from the property tree
        for i in range(self.tree.blocks.childCount()):
            item = self.tree.blocks.child(i)
            if item.text(0) == name:
                self.tree.blocks.takeChild(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        self.blocks.removeWidget(name)
        self.sequence_editor.toolbox().removeItem(name)
    
    def _onGroupRemoved(self, name):
        """Function that gets called when a block has been removed from the model."""
        # Find and remove it from the property tree        
        for i in range(self.tree.groups.childCount()):
            item = self.tree.groups.child(i)
            if item.text(0) == name:
                self.tree.groups.takeChild(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        self.groups.removeWidget(name)
        self.sequence_editor.toolbox().removeItem(name)
