"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType


class SignalNode(Node):
    """A node representing part of the signal in the signal designer.
    In the model-view relationship the config widget is the view, and the node is the model.
    """

    class Config(QWidget):
        """Config widget displayed for a signal node.
        In the model-view relationship the config widget is the view, and the node is the model.
        """
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self._node = None

        def setNode(self, node):
            self._node = node
            self.updateView()
        
        def node(self):
            return self._node
        
        def updateView(self):
            """Update the view (self), based on the model (node) data."""
            pass

        def updateModel(self):
            """Update model (node) data based on the view (self)."""
            pass


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
    def configWidget(self):
        w = super().configWidget()

        if w is not None:
            return w
        
        w = self.Config()
        self.setConfigWidget(w)
        w.setNode(self)
        return w

    def hasConfigWidget(self):
        """Since nodes generate a config widget on demand, this internal function checks if one has already been
        generated.
        """
        return super().configWidget() is not None

    # Model-view interactions ==========================================================================================
    def updateView(self):
        """Update the view (config widget), based on the model (self) data.
        This function checks if the node has a view and calls its update function.
        """
        if self.hasConfigWidget():
            self.configWidget().updateView()

    def updateModel(self):
        """Update model (self) data based on the view (config widget).
        This function checks if the node has a view and calls its update function.
        """
        if self.hasConfigWidget():
            self.configWidget().updateModel()