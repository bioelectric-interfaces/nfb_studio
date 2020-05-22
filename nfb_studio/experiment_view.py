import os

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QAction, QFileDialog

from nfb_studio.util.qt.tree_model import TreeModelItem

from .experiment import Experiment
from .widgets.scheme import SchemeEditor
from .property_tree import PropertyTree
from .widgets.config import BlockConfig, GroupConfig, GeneralConfig
from .block import Block
from .group import Group
from .widgets.signal_nodes import *
from .widgets.sequence_nodes import *


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
        self.general_config = GeneralConfig()
        
        self.signal_editor = SchemeEditor()
        self.signal_editor.toolbox().addItem("LSL Input", LSLInput())
        self.signal_editor.toolbox().addItem("Spatial Filter", SpatialFilter())
        self.signal_editor.toolbox().addItem("Bandpass Filter", BandpassFilter())
        self.signal_editor.toolbox().addItem("Envelope Detector", EnvelopeDetector())
        self.signal_editor.toolbox().addItem("Standardise", Standardise())
        self.signal_editor.toolbox().addItem("Signal Export", DerivedSignalExport())

        self.block_stack = QStackedWidget()
        self.group_stack = QStackedWidget()

        # Sequence editor ----------------------------------------------------------------------------------------------
        self.sequence_editor = SchemeEditor()

        # Central widget -----------------------------------------------------------------------------------------------
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.general_config)
        self.central_widget.addWidget(self.signal_editor)
        self.central_widget.addWidget(self.block_stack)
        self.central_widget.addWidget(self.group_stack)
        self.central_widget.addWidget(self.sequence_editor)

        # Signals ------------------------------------------------------------------------------------------------------
        #self.property_tree_view.blocktree_menu_add_action.triggered.connect(lambda: self.addBlock(Block))
        #self.property_tree_view.grouptree_menu_add_action.triggered.connect(self.addGroup)

    def model(self):
        return self._model
    
    def setModel(self, model, /):
        self._model = model
        self.signal_editor.setScheme(model.signal_scheme)
        self.sequence_editor.setScheme(model.sequence_scheme)

        model._view = self
        model.sync()

    def sync(self):
        ex = self.model()
        if ex is None:
            return
        
        # For each block, write it's data to the experiment
        for i in range(self.block_stack.count()):
            block_config: BlockConfig = self.block_stack.widget(i)
            block_config.sync()
        
        # For each group, write its data to the experiment
        for i in range(self.group_stack.count()):
            group_config: GroupConfig = self.group_stack.widget(i)
            group_config.sync()

        # Write general experiment data
        self.general_config.sync()

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
            self.block_stack.setCurrentIndex(index.row())
        elif item.parent() is self.property_tree.groups_item:
            self.central_widget.setCurrentIndex(3)
            self.group_stack.setCurrentIndex(index.row())
        elif item is self.property_tree.sequence_item:
            self.central_widget.setCurrentIndex(4)

    def addBlock(self, block):
        block_config = BlockConfig()
        block.setView(block_config)

        self.model().blocks.add(block)

        tree_item = TreeModelItem()
        tree_item.setText(block.name)
        self.property_tree.blocks_item.addItem(tree_item)

        self.block_stack.addWidget(block_config)

        block_node = BlockNode()
        block_node.setTitle(block.name)
        self.sequence_editor.toolbox().addItem(block.name, block_node)
    
    def addGroup(self, group):
        group_config = GroupConfig()
        group.setView(group_config)

        self.model().groups.add(group)

        tree_item = TreeModelItem()
        tree_item.setText(group.name)
        self.property_tree.groups_item.addItem(tree_item)

        self.group_stack.addWidget(group_config)

        group_node = GroupNode()
        group_node.setTitle(group.name)
        self.sequence_editor.toolbox().addItem(group.name, group_node)
