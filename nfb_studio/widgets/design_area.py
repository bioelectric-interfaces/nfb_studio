from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDockWidget

from .scheme import Scheme, Toolbox

class DesignArea(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scheme = Scheme(self)
        self.toolbox = Toolbox(self)

        self.setCentralWidget(self.scheme.view)

        dock = QDockWidget("Node toolbox", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(self.toolbox.getView())
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.scheme.view.configRequested.connect(self.showConfigWidget)
    
    def showConfigWidget(self, node):
        dock = QDockWidget("Configuration", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(node.configWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, dock)