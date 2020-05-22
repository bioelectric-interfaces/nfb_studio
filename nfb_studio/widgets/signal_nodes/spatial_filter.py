"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode


class SpatialFilter(SignalNode):
    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.matrix_path = QLineEdit()

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Matrix path", self.matrix_path)
        
        def sync(self):
            n = self.node()
            if n is None:
                return
            
            n._matrix_path = self.matrix_path.text()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Spatial Filter")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self._matrix_path = ""
        self.sync()

    def matrixPath(self) -> str:
        return self._matrix_path
    
    def setMatrixPath(self, matrix_path: str, /):
        self._matrix_path = matrix_path
        self.sync()

    def sync(self):
        if not self.hasConfigWidget():
            return
        
        w = self.configWidget()
        w.matrix_path.setText(self.matrixPath())

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["SpatialFilterMatrix"] = self.matrixPath()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["matrix_path"] = self.matrixPath()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.setMatrixPath(data["matrix_path"])
