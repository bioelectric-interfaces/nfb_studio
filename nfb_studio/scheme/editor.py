from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QDockWidget, QWidget

from .scheme import Scheme
from .toolbox import Toolbox

class SchemeEditor(QMainWindow):
    """Scheme editor is the widget responsible for the scheme editing experience.  
    As its main components, SchemeEditor contains the following widgets:
    - scheme - the canvas for dragging and connecting nodes to form signals;
    - toolbox - a list of draggable nodes to be put on the scheme;
    - (optionally) config widget - a widget for manipulating properties of nodes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scheme = None
        self._scheme_view = Scheme.View()
        self._toolbox = None

        self.setCentralWidget(self._scheme_view)

        self.toolbox_dock = QDockWidget("Node Toolbox", self)
        self.toolbox_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.toolbox_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox_dock)
        self.setToolbox(Toolbox(self))

        self.config_widget_dock = QDockWidget("Configuration", self)
        self.config_widget_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.config_widget_dock)
        self.config_widget_dock.hide()

    def scheme(self):
        return self._scheme

    def toolbox(self):
        return self._toolbox

    def schemeView(self):
        return self._scheme_view
    
    def toolboxView(self):
        return self.toolbox_dock.widget()

    def setScheme(self, scheme: Scheme):
        if self._scheme is not None:
            self._scheme_view.configRequested.disconnect(self.showConfigWidget)
            self._scheme.setCustomDropEvent(self.toolbox().DragMimeType, None)

        self._scheme = scheme

        if self._scheme is not None:
            self._scheme_view.setScene(self._scheme)

            # Conect the signal for config widget
            self._scheme_view.configRequested.connect(self.showConfigWidget)

            # Add a custom drop event for the scheme from the toolbox
            self._scheme.setCustomDropEvent(self.toolbox().DragMimeType, self.toolbox().schemeDropEvent)

    def setToolbox(self, toolbox):
        self._toolbox = toolbox

        self.toolbox_dock.setWidget(self._toolbox.getView())

    def showConfigWidget(self, node):
        """Show config widget for a node.
        This function is automatically connected as a slot to the scheme view's configRequested signal.
        """
        self.config_widget_dock.setWidget(node.configWidget())
        self.config_widget_dock.show()
