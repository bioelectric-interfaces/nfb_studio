"""Main window of the UI application."""
import os
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMainWindow, QFileDialog

from nfb_studio.experiment import Experiment, ExperimentView


class MainWindow(QMainWindow):
    """Main window of the UI application.
    Main window contains the toolbars for manipulating experiment files, as well as ExperimentView as its central
    widget.
    """
    def __init__(self):
        super().__init__()

        self._experiment = None
        self.setExperiment(Experiment())

        self._assosiated_file = None

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

    def experiment(self):
        return self._experiment

    def associatedFile(self):
        return self._assosiated_file

    def setExperiment(self, experiment):
        self._experiment = experiment
        experiment_view = ExperimentView()
        self._experiment.setView(experiment_view)

        self.setCentralWidget(experiment_view)

    def actionExport(self):
        self.experiment().view().updateModel()
        data = self.experiment().export()

        file_path = QFileDialog.getSaveFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return

        if os.path.splitext(file_path)[1] == "":  # No extension
            file_path = file_path + ".xml"

        with open(file_path, "w") as file:
            file.write(data)

    def actionSave(self):
        if self.associatedFile() is None:
            self.actionSaveAs()
        
        self.fileSave(self.associatedFile())

    def actionSaveAs(self):        
        path = QFileDialog.getSaveFileName(filter="Experiment Files (*.nfbex)")[0]
        if path == "":
            return

        if os.path.splitext(path)[1] == "":  # No extension
            path = path + ".nfbex"

        self._assosiated_file = path
        self.fileSave(self.associatedFile())

    def actionOpen(self):
        path = QFileDialog.getOpenFileName(filter="Experiment Files (*.nfbex)")[0]
        if path == "":
            return

        self.fileOpen(path)

    def actionImport(self):
        file_path = QFileDialog.getOpenFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return

        with open(file_path) as file:
            data = file.read()
        
        ex = Experiment.import_xml(data)
        self.setExperiment(ex)

    def fileOpen(self, path):
        with open(path) as file:
            data = file.read()
        
        ex = Experiment.load(data)
        self.setExperiment(ex)
        self._assosiated_file = path

    def fileSave(self, path):
        self.experiment().view().updateModel()
        data = self.experiment().save()

        with open(path, "w") as file:
            file.write(data)
