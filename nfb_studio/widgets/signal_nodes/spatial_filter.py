"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .lsl_input import LSLInput


class SpatialFilter(SignalNode):
    input_type = LSLInput.output_type
    output_type = DataType(101)

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.matrix_path = QLineEdit()
            self.matrix_path.editingFinished.connect(self.updateModel)

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Matrix path", self.matrix_path)
        
        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            n.setMatrixPath(self.matrix_path.text())
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.matrix_path.blockSignals(True)
            self.matrix_path.setText(n.matrixPath())
            self.matrix_path.blockSignals(False)

    default_matrix_path = ""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Spatial Filter")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._matrix_path = self.default_matrix_path
        self._adjust()

    def matrixPath(self) -> str:
        return self._matrix_path
    
    def setMatrixPath(self, matrix_path: str, /):
        self._matrix_path = matrix_path
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        if self.matrixPath() == "":
            self.setDescription("No Matrix")
        else:
            self.setDescription(self.matrixPath())

    # Serialization ====================================================================================================
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
