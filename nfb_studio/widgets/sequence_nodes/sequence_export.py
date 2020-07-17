"""NFB main source signal."""
from ..scheme import Node, Input, Output, DataType


class SequenceExport(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Sequence Export")
        self.setDescription("Add this node to the end of\nthe sequence")
        self.addInput(Input("Input", DataType.Unknown))

        #self.setConfigWidget(self.Config())

    def serialize(self) -> dict:
        return super().serialize()
    
    @classmethod
    def deserialize(cls, data: dict):
        return super().deserialize(data)
