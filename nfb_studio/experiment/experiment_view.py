import os

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QAction, QFileDialog

from nfb_studio.block import Block, BlockView
from nfb_studio.group import Group, GroupView
from nfb_studio.util.qt import StackedDictWidget
from nfb_studio.util.qt.tree_model import TreeModelItem
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
        self.property_tree = PropertyTree()
        self.property_tree_view = self.property_tree.getView()
        self.property_tree_view.clicked.connect(self.setCurrentIndex)

        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self.property_tree_view)
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

        # Signals ------------------------------------------------------------------------------------------------------
        def add_new_block():
            ex = self.model()
            ex.blocks[ex.blocks.getName()] = Block()
        
        def add_new_group():
            ex = self.model()
            ex.groups[ex.groups.getName()] = Group()

        self.property_tree_view.blocktree_menu_add_action.triggered.connect(add_new_block)
        self.property_tree_view.grouptree_menu_add_action.triggered.connect(add_new_group)

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

    def setCurrentIndex(self, index: QModelIndex):
        """Set central widget in the main window to display config info for item at `index` in the property tree."""
        self.property_tree_view.setCurrentIndex(index)

        item = self.property_tree.item(index)
        
        if item is self.property_tree.general_item:
            self.central_widget.setCurrentIndex(0)
        if item is self.property_tree.signals_item:
            self.central_widget.setCurrentIndex(1)
        elif item.parent() is self.property_tree.blocks_item:
            self.central_widget.setCurrentIndex(2)
            self.blocks.setCurrentIndex(index.row())
        elif item.parent() is self.property_tree.groups_item:
            self.central_widget.setCurrentIndex(3)
            self.groups.setCurrentIndex(index.row())
        elif item is self.property_tree.sequence_item:
            self.central_widget.setCurrentIndex(4)

    def _onBlockAdded(self, name):
        """Function that gets called when a new block has been added to the model."""
        # Add an item to the property tree
        tree_item = TreeModelItem()
        tree_item.setText(name)
        self.property_tree.blocks_item.addItem(tree_item)
        
        # Add a view to the widget stack
        block_view = BlockView()
        block_view.setModel(self.model().blocks[name])
        self.blocks.addWidget(name, block_view)

        # Add a node to draw the sequence
        node = BlockNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)
    
    def _onGroupAdded(self, name):
        """Function that gets called when a new group has been added to the model."""
        # Add an item to the property tree
        tree_item = TreeModelItem()
        tree_item.setText(name)
        self.property_tree.groups_item.addItem(tree_item)

        # Add a view to the widget stack
        group_view = GroupView()
        group_view.setModel(self.model().groups[name])
        self.groups.addWidget(name, group_view)

        # Add a node to draw the sequence
        node = GroupNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)
    
    def _onBlockRemoved(self, name):
        """Function that gets called when a block has been removed from the model."""
        # Find and remove it from the property tree
        for i in range(view.property_tree.blocks_item.childrenCount()):
            item = view.property_tree.blocks_item.item(i)
            if item.text() == key:
                view.property_tree.blocks_item.removeItem(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        view.blocks.removeWidget(key)
        view.sequence_editor.toolbox().removeItem(key)
    
    def _onGroupRemoved(self, name):
        """Function that gets called when a block has been removed from the model."""
        # Find and remove it from the property tree        
        for i in range(view.property_tree.groups_item.childrenCount()):
            item = view.property_tree.groups_item.item(i)
            if item.text() == key:
                view.property_tree.groups_item.removeItem(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        view.groups.removeWidget(key)
        view.sequence_editor.toolbox().removeItem(key)
