"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType


class BlockNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Block")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        #self.setConfigWidget(self.Config())
