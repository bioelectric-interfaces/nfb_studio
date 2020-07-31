"""View widget for Experiment class and the main window of this application."""
import os
from typing import Optional
from pathlib import Path

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtGui import QStandardItem, QKeySequence
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QFileDialog, QMessageBox

from .experiment import Experiment

from .block import Block, BlockView
from .group import Group, GroupView
from .util import StackedDictWidget
from .general_view import GeneralView
from .property_tree import PropertyTree
from .export_wizard import ExportWizard
from .scheme import SchemeEditor
from .signal_nodes import *
from .sequence_nodes import *


class ExperimentView(QMainWindow):
    """View widget for Experiment class and the main window of this application."""
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._model = None
        self._save_path = None
        """Save path of the experiment that is being edited."""

        # Menu bar -----------------------------------------------------------------------------------------------------
        menubar = self.menuBar()
        filemenu = menubar.addMenu("File")

        action_open = filemenu.addAction("Open")
        action_open.triggered.connect(self.actionOpen)
        action_open.setShortcut(QKeySequence.Open)

        action_save = filemenu.addAction("Save")
        action_save.triggered.connect(self.actionSave)
        action_save.setShortcut(QKeySequence.Save)

        action_save_as = filemenu.addAction("Save As...")
        action_save_as.triggered.connect(self.actionSaveAs)
        action_save_as.setShortcut(QKeySequence.SaveAs)

        action_export = filemenu.addAction("Export...")
        action_export.triggered.connect(self.actionExport)

        action_import = filemenu.addAction("Import")
        action_import.triggered.connect(self.actionImport)

        # Property tree ------------------------------------------------------------------------------------------------
        self.tree = PropertyTree()
        self.tree_view = self.tree.getView()
        self.tree_view.currentIndexChanged.connect(self.displayTreeItem)

        # Property tree dock widget ------------------------------------------------------------------------------------
        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self.tree_view)
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
        self.signal_editor.toolbox().addItem("Composite Signal Export", CompositeSignalExport())

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

        # New experiment view is created with a new experiment ---------------------------------------------------------
        self.actionNew()

    # Get/Set methods ==================================================================================================
    def model(self) -> Optional[Experiment]:
        """Return the experiment, assosiated with this view."""
        return self._model
    
    def projectTitle(self) -> str:
        """Return document title, i.e. name of file this experiment is saved as.
        If no file has been associated with this experiment, returns "Untitled".
        """
        if self.savePath():
            return Path(self.savePath()).stem
        return "Untitled"

    def savePath(self) -> Optional[str]:
        """Return path of the file from which the """
        return self._save_path

    def setModel(self, ex: Experiment, /):
        self._model = ex

        self.tree.setExperiment(ex)
        self.signal_editor.setScheme(ex.signal_scheme)

        self.sequence_editor.setScheme(ex.sequence_scheme)

        ex.blocks.itemAdded.connect(self._onBlockAdded)
        ex.blocks.itemRenamed.connect(self._onBlockRenamed)
        ex.blocks.itemRemoved.connect(self._onBlockRemoved)
        ex.groups.itemAdded.connect(self._onGroupAdded)
        ex.groups.itemRenamed.connect(self._onGroupRenamed)
        ex.groups.itemRemoved.connect(self._onGroupRemoved)

        ex._view = self
        ex.updateView()

    # Experiment syncronization ========================================================================================
    def updateModel(self):
        """Update the experiment when data in the view was changed by the user."""
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

    def _onBlockAdded(self, name):
        """Function that gets called when a new block has been added to the experiment."""
        # Add an item to the property tree
        tree_item = QStandardItem(name)
        tree_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        self.tree.blocks.appendRow(tree_item)
        
        # Add a view to the widget stack
        block_view = BlockView()
        block_view.setModel(self.model().blocks[name])
        self.blocks.addWidget(name, block_view)

        # Add a node to draw the sequence
        node = BlockNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)

        # Select this item
        self.tree_view.setCurrentIndex(self.tree.indexFromItem(tree_item))
    
    def _onGroupAdded(self, name):
        """Function that gets called when a new group has been added to the experiment."""
        # Add an item to the property tree
        tree_item = QStandardItem(name)
        tree_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        self.tree.groups.appendRow(tree_item)

        # Add a view to the widget stack
        group_view = GroupView()
        group_view.setModel(self.model().groups[name])
        self.groups.addWidget(name, group_view)

        # Add a node to draw the sequence
        node = GroupNode()
        node.setTitle(name)
        self.sequence_editor.toolbox().addItem(name, node)

        # Select this item
        self.tree_view.setCurrentIndex(self.tree.indexFromItem(tree_item))
    
    def _onBlockRenamed(self, old_name, new_name):
        """Function that gets called when a block has been renamed."""
        # Rename it in the property tree
        for i in range(self.tree.blocks.rowCount()):
            item = self.tree.blocks.child(i)
            if item.text() == old_name:
                item.setText(new_name)
                break
        
        # Rename in widget stack
        current_key = self.blocks.currentKey()

        w = self.blocks.removeWidget(old_name)
        self.blocks.addWidget(new_name, w)

        if current_key == old_name:
            self.blocks.setCurrentKey(new_name)

        # Rename in the sequence editor
        node = self.sequence_editor.toolbox().removeItem(old_name)
        self.sequence_editor.toolbox().addItem(new_name, node)

        for node in self.sequence_editor.scheme().graph.nodes:
            if node.title() == old_name:
                node.setTitle(new_name)

    def _onGroupRenamed(self, old_name, new_name):
        """Function that gets called when a group has been renamed."""
        # Rename it in the property tree
        for i in range(self.tree.groups.rowCount()):
            item = self.tree.groups.child(i)
            if item.text() == old_name:
                item.setText(new_name)
                break
        
        # Rename in widget stack
        current_key = self.groups.currentKey()

        w = self.groups.removeWidget(old_name)
        self.groups.addWidget(new_name, w)

        if current_key == old_name:
            self.groups.setCurrentKey(new_name)

        # Rename in the sequence editor
        node = self.sequence_editor.toolbox().removeItem(old_name)
        self.sequence_editor.toolbox().addItem(new_name, node)

        for node in self.sequence_editor.scheme().graph.nodes:
            if node.title() == old_name:
                node.setTitle(new_name)

    def _onBlockRemoved(self, name):
        """Function that gets called when a block has been removed from the experiment."""
        # Find and remove it from the property tree
        for i in range(self.tree.blocks.rowCount()):
            item = self.tree.blocks.child(i)
            if item.text() == name:
                self.tree.blocks.removeRow(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        self.blocks.removeWidget(name)
        self.sequence_editor.toolbox().removeItem(name)
    
    def _onGroupRemoved(self, name):
        """Function that gets called when a block has been removed from the experiment."""
        # Find and remove it from the property tree        
        for i in range(self.tree.groups.rowCount()):
            item = self.tree.groups.child(i)
            if item.text() == name:
                self.tree.groups.removeRow(i)
                break
        
        # Remove from widget stack and the sequence editor toolbox
        self.groups.removeWidget(name)
        self.sequence_editor.toolbox().removeItem(name)

    # Property tree syncronization =====================================================================================
    def displayTreeItem(self, index: QModelIndex):
        """Display the widget corresponding to the item in the property tree."""
        item = self.tree.itemFromIndex(index)

        if item is self.tree.general:
            # General
            self.central_widget.setCurrentWidget(self.general_view)
        elif item is self.tree.signals:
            # Signal editor
            self.central_widget.setCurrentWidget(self.signal_editor)
        elif item.parent() is self.tree.blocks:
            # A block
            self.central_widget.setCurrentWidget(self.blocks)
            self.blocks.setCurrentKey(item.text())
        elif item.parent() is self.tree.groups:
            # A group
            self.central_widget.setCurrentWidget(self.groups)
            self.groups.setCurrentKey(item.text())
        elif item is self.tree.sequence:
            # Sequence editor
            self.central_widget.setCurrentWidget(self.sequence_editor)

    # User actions =====================================================================================================
    def actionNew(self) -> bool:
        if self.model() and not self.promptSaveChanges():
            return False  # Action cancelled during prompt

        self.setModel(Experiment())
        self._save_path = None
        self.setWindowTitle(self.projectTitle() + " - NFB Studio")
        return True

    def actionExport(self) -> bool:        
        self.updateModel()
        
        wiz = ExportWizard(self, self.model())
        wiz.exec_()
        
        data = self.model().export()

        file_path = QFileDialog.getSaveFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return False  # Action was cancelled

        if os.path.splitext(file_path)[1] == "":  # No extension
            file_path = file_path + ".xml"

        with open(file_path, "w") as file:
            file.write(data)
        return True

    def actionSave(self) -> bool:
        """User action "Save". Saves file to its location, or promts user if no location exists yet.
        Returns True if file was saved, and False if action was cancelled.
        """
        if self.savePath() is None:
            return self.actionSaveAs()
        
        self.fileSave(self.savePath())
        self.setWindowTitle(self.projectTitle() + " - NFB Studio")
        return True

    def actionSaveAs(self) -> bool:
        """User action "Save As". Promts user to save file as.
        Returns True if file was saved, and False if action was cancelled.
        """
        path = QFileDialog.getSaveFileName(filter="Experiment Files (*.nfbex)")[0]
        if path == "":
            return False  # Action was cancelled

        if os.path.splitext(path)[1] == "":  # No extension
            path = path + ".nfbex"

        self._save_path = path
        self.fileSave(self.savePath())
        self.setWindowTitle(self.projectTitle() + " - NFB Studio")
        return True

    def actionOpen(self) -> bool:
        """User action "Open". Promts user to open a file.
        Returns True if file was opened, and False if action was cancelled.
        """
        if self.model() and not self.promptSaveChanges():
            return False  # Action cancelled during prompt

        path = QFileDialog.getOpenFileName(filter="Experiment Files (*.nfbex)")[0]
        if path == "":
            return False

        self.fileOpen(path)
        self.setWindowTitle(self.projectTitle() + " - NFB Studio")
        return True

    def actionImport(self) -> bool:
        """User action "Import". Promts user to import a file.
        Returns True if file was imported, and False if action was cancelled.
        """
        if self.model() and not self.promptSaveChanges():
            return False  # Action cancelled during prompt

        file_path = QFileDialog.getOpenFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return False

        with open(file_path) as file:
            data = file.read()
        
        ex = Experiment.import_xml(data)
        self.setModel(ex)
        return True

    def promptSaveChanges(self) -> bool:
        """Prompt the user to save changes to current project.
        Display a message box asking the user if they want to save changes. If user selects Save, execute actionSave.
        Returns True if the user decided to discard changes or saved the file, and False if the user cancelled operation
        either during prompt or during save.
        """
        prompt = QMessageBox()
        prompt.setWindowTitle("NFB Studio")
        prompt.setIcon(QMessageBox.Warning)
        prompt.setText("Save changes to \"{}\" before closing?".format(self.projectTitle()))
        prompt.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        prompt.setDefaultButton(QMessageBox.Save)
        
        answer = prompt.exec_()
        if answer == QMessageBox.Cancel:
            return False
        if answer == QMessageBox.Save:
            return self.actionSave()
        return True

    def closeEvent(self, event):
        if self.model():
            event.setAccepted(self.promptSaveChanges())
        else:
            event.accept()

    # File operations ==================================================================================================
    def fileOpen(self, path):
        with open(path) as file:
            data = file.read()
        
        ex = Experiment.load(data)
        self.setModel(ex)
        self._save_path = path

    def fileSave(self, path):
        self.model().view().updateModel()
        data = self.model().save()

        with open(path, "w") as file:
            file.write(data)
