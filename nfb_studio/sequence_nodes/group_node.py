"""NFB main source signal."""
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
    
    @classmethod
    def deserialize(cls, data: dict):
        return super().deserialize(data)
