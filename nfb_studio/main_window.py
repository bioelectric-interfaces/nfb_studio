"""Main window of the UI application."""
import os

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

        # Menu bar -----------------------------------------------------------------------------------------------------
        menubar = self.menuBar()
        filemenu = menubar.addMenu("File")

        open = filemenu.addAction("Open")
        open.triggered.connect(self.load)

        save = filemenu.addAction("Save As...")
        save.triggered.connect(self.save)

        export = filemenu.addAction("Export")
        export.triggered.connect(self.export)

        import_xml = filemenu.addAction("Import")
        import_xml.triggered.connect(self.import_xml)

    def experiment(self):
        return self._experiment

    def setExperiment(self, experiment):
        self._experiment = experiment
        experiment_view = ExperimentView()
        self._experiment.setView(experiment_view)

        self.setCentralWidget(experiment_view)

    def export(self):
        self.experiment().view().updateModel()
        data = self.experiment().export()

        file_path = QFileDialog.getSaveFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return

        if os.path.splitext(file_path)[1] == "":  # No extension
            file_path = file_path + ".xml"

        with open(file_path, "w") as file:
            file.write(data)

    def save(self):
        self.experiment().view().updateModel()
        data = self.experiment().save()
        
        file_path = QFileDialog.getSaveFileName(filter="Experiment Files (*.nfbex)")[0]
        if file_path == "":
            return

        if os.path.splitext(file_path)[1] == "":  # No extension
            file_path = file_path + ".nfbex"

        with open(file_path, "w") as file:
            file.write(data)

    def load(self):
        file_path = QFileDialog.getOpenFileName(filter="Experiment Files (*.nfbex)")[0]
        if file_path == "":
            return

        with open(file_path) as file:
            data = file.read()
        
        ex = Experiment.load(data)
        self.setExperiment(ex)

    def import_xml(self):
        file_path = QFileDialog.getOpenFileName(filter="XML Files (*.xml)")[0]
        if file_path == "":
            return

        with open(file_path) as file:
            data = file.read()
        
        ex = Experiment.import_xml(data)
        self.setExperiment(ex)
