"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType


class GroupNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Group")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        #self.setConfigWidget(self.Config())

    def serialize(self) -> dict:
        return super().serialize()
    
    def deserialize(self, data: dict):
        super().deserialize(data)
