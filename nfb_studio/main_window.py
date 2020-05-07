from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget
from .experiment import Experiment
from .widgets.signal import SignalEditor
from .property_tree import PropertyTree
from .widgets.config import BlockConfig, GroupConfig, ExperimentConfig
from .block import Block
from .group import Group
from nfb_studio.util.qt.tree_model import TreeModelItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.experiment = Experiment()

        # Property tree ------------------------------------------------------------------------------------------------
        self.property_tree = PropertyTree()
        self.property_tree_view = self.property_tree.view()
        self.property_tree_view.clicked.connect(self.setCurrentIndex)

        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self.property_tree_view)
        self.property_tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_tree_dock)

        # Editing widgets ----------------------------------------------------------------------------------------------
        self.experiment_config = ExperimentConfig(self.experiment)
        self.signal_editor = SignalEditor()

        self.block_stack = QStackedWidget()
        self.group_stack = QStackedWidget()

        # Central widget -----------------------------------------------------------------------------------------------
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.experiment_config)
        self.central_widget.addWidget(self.signal_editor)
        self.central_widget.addWidget(self.block_stack)
        self.central_widget.addWidget(self.group_stack)

        # Signals ------------------------------------------------------------------------------------------------------
        self.property_tree_view.blocktree_menu_add_action.triggered.connect(self.addBlock)
        self.property_tree_view.grouptree_menu_add_action.triggered.connect(self.addGroup)

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

    def addBlock(self):
        block = Block()
        block_config = BlockConfig(block)

        self.experiment.blocks.add(block)

        tree_item = TreeModelItem()
        tree_item.setText(block.name)
        self.property_tree.blocks_item.addItem(tree_item)

        self.block_stack.addWidget(block_config)
    
    def addGroup(self):
        group = Group()
        group_config = GroupConfig(group)

        self.experiment.groups.add(group)

        tree_item = TreeModelItem()
        tree_item.setText(group.name)
        self.property_tree.groups_item.addItem(tree_item)

        self.group_stack.addWidget(group_config)
