from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDockWidget

from .scheme import Scheme
from .toolbox import Toolbox

class SignalEditor(QMainWindow):
    """Signal editor is the widget responsible for the signal editing experience.  
    As its main components, SignalEditor contains the following widgets:
    - scheme - the canvas for dragging and connecting nodes to form signals;
    - toolbox - a list of draggable nodes to be put on the scheme;
    - (optionally) config widget - a widget for manipulating properties of nodes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scheme = Scheme(self)
        self.toolbox = Toolbox(self)

        self.setCentralWidget(self.scheme.view)

        dock = QDockWidget("Node toolbox", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dock.setWidget(self.toolbox.getView())
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.scheme.view.configRequested.connect(self.showConfigWidget)
    
    def showConfigWidget(self, node):
        dock = QDockWidget("Configuration", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(node.configWidget())
        self.addDockWidget(Qt.RightDockWidgetArea, dock)