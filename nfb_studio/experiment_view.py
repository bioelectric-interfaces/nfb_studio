"""View widget for Experiment class and the main window of this application."""
import os
import subprocess
from datetime import datetime
from typing import Optional
from pathlib import Path

from PySide2.QtCore import Qt, QModelIndex, QDir
from PySide2.QtGui import QStandardItem, QKeySequence
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QFileDialog, QMessageBox, QScrollArea

import nfb_studio

from .experiment import Experiment
from .block import BlockView
from .group import GroupView
from .util import StackedDictWidget
from .general_view import GeneralView
from .property_tree import PropertyTree
from .scheme import SchemeEditor
from .sequence_editor import SequenceEditor
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

        runmenu = menubar.addMenu("Run")

        action_start_ex = runmenu.addAction("Start Experiment")
        action_start_ex.triggered.connect(self.actionStartExperiment)
        action_start_ex.setShortcut("F9")

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
        self.sequence_editor = SequenceEditor()

        # Central widget -----------------------------------------------------------------------------------------------
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        scrollarea = QScrollArea()
        scrollarea.setWidget(self.general_view)
        self.central_widget.addWidget(scrollarea)
        self.central_widget.addWidget(self.signal_editor)
        self.central_widget.addWidget(self.blocks)
        self.central_widget.addWidget(self.groups)
        self.central_widget.addWidget(self.sequence_editor)

        # New experiment view is created with a new experiment ---------------------------------------------------------
        self.actionNew()

        #self.sequence_editor.schemeView().setWidget(QLabel("Hello!"))

    # Get/Set methods ==================================================================================================
    def model(self) -> Optional[Experiment]:
        """Return the experiment assosiated with this view."""
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

        self.updateView()

    # Experiment syncronization ========================================================================================
    def updateModel(self):
        """Update the experiment when data in the view was changed by the user."""
        ex = self.model()
        if ex is None:
            return
        
        # For each block, write it's data to the experiment
        for name in self.blocks.keys():
            block_view: BlockView = self.blocks.widget(name).widget()
            block_view.updateModel()
        
        # For each group, write its data to the experiment
        for name in self.groups.keys():
            group_view: GroupView = self.groups.widget(name).widget()
            group_view.updateModel()

        # Write general experiment data
        self.general_view.updateModel(ex)

        # Write the selected sequence
        ex.sequence = [node.title() for node in self.sequence_editor.selectedSequence()[1]]

    def updateView(self):
        ex = self.model()
        if ex is None:
            return

        # General properties -------------------------------------------------------------------------------------------
        general = self.general_view
        
        general.name.setText(ex.name)
        general.inlet_type.setCurrentText(general.inlet_type_import_values[ex.inlet])
        general.lsl_stream_name.setCurrentText(ex.lsl_stream_name)
        general.lsl_filename.setText(ex.raw_data_path)
        general.hostname_port.setText(ex.hostname_port)
        general.dc.setChecked(ex.dc)

        if ex.prefilter_band[0] is None:
            general.prefilter_lower_bound_enable.setChecked(False)
            general.prefilter_lower_bound.setValue(0)
        else:
            general.prefilter_lower_bound_enable.setChecked(True)
            general.prefilter_lower_bound.setValue(ex.prefilter_band[0])
        
        if ex.prefilter_band[1] is None:
            general.prefilter_upper_bound_enable.setChecked(False)
            general.prefilter_upper_bound.setValue(0)
        else:
            general.prefilter_upper_bound_enable.setChecked(True)
            general.prefilter_upper_bound.setValue(ex.prefilter_band[1])
        
        general.plot_raw.setChecked(ex.plot_raw)
        general.plot_signals.setChecked(ex.plot_signals)
        general.show_subject_window.setChecked(ex.show_subject_window)
        general.discard_channels.setText(ex.discard_channels)
        general.reference_sub.setText(ex.reference_sub)
        general.show_proto_rectangle.setChecked(ex.show_proto_rectangle)
        general.show_notch_filters.setChecked(ex.show_notch_filters)

        # Blocks and groups --------------------------------------------------------------------------------------------
        while self.tree.blocks.rowCount() > 0:
            name = self.tree.blocks.child(0).text()
            self.tree.blocks.takeChild(0)
            self.blocks.removeWidget(name)
            self.sequence_editor.toolbox().removeItem(name)
        
        while self.tree.groups.rowCount() > 0:
            name = self.tree.groups.child(0).text()
            self.tree.groups.takeChild(0)
            self.groups.removeWidget(name)
            self.sequence_editor.toolbox().removeItem(name)

        for name in ex.blocks:
            ex.blocks.itemAdded.emit(name)
        
        for name in ex.groups:
            ex.groups.itemAdded.emit(name)
        
        # Sequence -----------------------------------------------------------------------------------------------------
        for sgraph, slist, button in self.sequence_editor.sequences():
            if ex.sequence == [node.title() for node in slist]:
                button.setChecked(True)
                break

    def _onBlockAdded(self, name):
        """Function that gets called when a new block has been added to the experiment."""
        # Add an item to the property tree
        tree_item = QStandardItem(name)
        tree_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        self.tree.blocks.appendRow(tree_item)
        
        # Add a view to the widget stack
        block_view = BlockView()
        block_view.setModel(self.model().blocks[name])
        scrollarea = QScrollArea()
        scrollarea.setWidget(block_view)
        self.blocks.addWidget(name, scrollarea)

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
        scrollarea = QScrollArea()
        scrollarea.setWidget(group_view)
        self.groups.addWidget(name, scrollarea)

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
        node.setTitle(new_name)
        self.sequence_editor.toolbox().addItem(new_name, node)

        for node in self.sequence_editor.scheme().graph.nodes:
            if node.title() == old_name:
                node.setTitle(new_name)
        
        # Rename it in the sequence editor's current sequence widget
        for _1, _2, button in self.sequence_editor.sequences():
            label = button.text()
            new_label = " → ".join([new_name if x == old_name else x for x in label.split(" → ")])
            button.setText(new_label)

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
        node.setTitle(new_name)
        self.sequence_editor.toolbox().addItem(new_name, node)

        for node in self.sequence_editor.scheme().graph.nodes:
            if node.title() == old_name:
                node.setTitle(new_name)
        
        # Rename it in the sequence editor's current sequence widget
        for _1, _2, button in self.sequence_editor.sequences():
            label = button.text()
            new_label = " → ".join([new_name if x == old_name else x for x in label.split(" → ")])
            button.setText(new_label)

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
            scrollarea = self.general_view.parent().parent()
            assert type(scrollarea) == QScrollArea
            self.central_widget.setCurrentWidget(scrollarea)
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
        
        if (len(self.model().sequence_scheme.graph.nodes) == 0):
            # No nodes in sequence scheme, cancel operation
            # TODO: A better way to signal to the user that he needs to create a sequence?
            self.central_widget.setCurrentWidget(self.sequence_editor)
            return False

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

    def actionStartExperiment(self):
        self.updateModel()
        
        if (len(self.model().sequence_scheme.graph.nodes) == 0):
            # No nodes in sequence scheme, cancel operation
            # TODO: A better way to signal to the user that he needs to create a sequence?
            self.central_widget.setCurrentWidget(self.sequence_editor)
            return

        results_path = QFileDialog.getExistingDirectory(
            caption="Select a folder to save experiment results",
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if results_path == "":
            return False  # Action was cancelled

        data = self.model().export()

        temp_dir = QDir.tempPath() + "/nfb_studio"
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = datetime.now()
        file_path = "{}/experiment ({:04d}-{:02d}-{:02d} {:02d}-{:02d}-{:02d}).xml".format(
            temp_dir,
            timestamp.year,
            timestamp.month,
            timestamp.day,
            timestamp.hour,
            timestamp.minute,
            timestamp.second
        )

        with open(file_path, "w") as file:
            file.write(data)
        
        subprocess.run(["pynfb", "-x", file_path], cwd=results_path)

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
        self.updateModel()
        data = self.model().save()

        with open(path, "w") as file:
            file.write(data)
