"""Main window of the UI application."""
import os
from typing import Union
from pathlib import Path
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from nfb_studio.experiment import Experiment, ExperimentView, ExportDialog


class MainWindow(QMainWindow):
    """Main window of the UI application.
    Main window contains the toolbars for manipulating experiment files, as well as ExperimentView as its central
    widget.
    """
    def __init__(self):
        super().__init__()

        self._experiment = None
        self._save_path = None

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

        # --------------------------------------------------------------------------------------------------------------
        self.actionNew()

    def projectTitle(self) -> str:
        """Return document title, i.e. name of file """
        if self.savePath():
            return Path(self.savePath()).stem
        return "Untitled"

    def experiment(self):
        return self._experiment

    def savePath(self) -> Union[str, None]:
        """Return path of the file from which the """
        return self._save_path

    def setExperiment(self, experiment):
        self._experiment = experiment
        experiment_view = ExperimentView()
        self._experiment.setView(experiment_view)

        self.setCentralWidget(experiment_view)

    def actionNew(self) -> bool:
        if self.experiment() and not self.promptSaveChanges():
            return False  # Action cancelled during prompt

        self.setExperiment(Experiment())
        self._save_path = None
        self.setWindowTitle(self.projectTitle() + " - NFB Studio")
        return True

    def actionExport(self) -> bool:
        dialog = ExportDialog(self)
        dialog.setSequenceScheme(self.experiment().sequence_scheme)
        dialog.exec_()
        
        self.experiment().view().updateModel()
        data = self.experiment().export()

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
        if self.experiment() and not self.promptSaveChanges():
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
        if self.experiment() and not self.promptSaveChanges():
            return False  # Action cancelled during prompt

        file_path = QFileDialog.getOpenFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return False

        with open(file_path) as file:
            data = file.read()
        
        ex = Experiment.import_xml(data)
        self.setExperiment(ex)
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
        if self.experiment():
            event.setAccepted(self.promptSaveChanges())
        else:
            event.accept()

    def fileOpen(self, path):
        with open(path) as file:
            data = file.read()
        
        ex = Experiment.load(data)
        self.setExperiment(ex)
        self._save_path = path

    def fileSave(self, path):
        self.experiment().view().updateModel()
        data = self.experiment().save()

        with open(path, "w") as file:
            file.write(data)
