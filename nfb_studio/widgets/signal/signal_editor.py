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

        self.toolbox_dock = QDockWidget("Node toolbox", self)
        self.toolbox_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.toolbox_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.toolbox_dock.setWidget(self.toolbox.getView())
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox_dock)

        self.config_widget_dock = QDockWidget("Configuration", self)
        self.config_widget_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.config_widget_dock)
        self.config_widget_dock.hide()

        self.scheme.view.configRequested.connect(self.showConfigWidget)
    
    def showConfigWidget(self, node):
        self.config_widget_dock.setWidget(node.configWidget())
        self.config_widget_dock.show()