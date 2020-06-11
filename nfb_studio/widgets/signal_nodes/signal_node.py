"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType


class SignalNode(Node):
    class Config(QWidget):
        """Config widget displayed for a signal node."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self._node = None

        def setNode(self, node):
            self._node = node
            self._node.sync()
        
        def node(self):
            return self._node
        
        def sync(self):
            """Sync data in this widget to the data in the node.
            "Sync" in this context means one-way copy from self to node. A similarly named function in the
            node copies data the other way. Call one or the other depending on where the data was changed.
            """
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

    def sync(self):
        """Sync data in this node to the data in the config widget.
        "Sync" in this context means one-way copy from self to configWidget. A similarly named function in the
        configWidget copies data the other way. Call one or the other depending on where the data was changed.
        This function is also called automatically when the configWidget is first created.
        """
        pass
