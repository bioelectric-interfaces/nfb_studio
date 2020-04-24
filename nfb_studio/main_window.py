from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDockWidget
from .project import Project

class MainWindow(QMainWindow):
    def __init__(self, project=None):
        super().__init__()

        self._project = project or Project()

        # Property tree ------------------------------------------------------------------------------------------------
        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self._project.property_tree.view())
        self.property_tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_tree_dock)

        # Central widget -----------------------------------------------------------------------------------------------
        self.setCentralWidget(self._project.signal_editor)

    def setProject(self, project):
        raise NotImplementedError