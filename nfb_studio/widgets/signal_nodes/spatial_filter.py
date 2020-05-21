"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType


class SpatialFilter(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.matrix_path = QLineEdit()

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Matrix path", self.matrix_path)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Spatial Filter")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["SpatialFilterMatrix"] = self.configWidget().matrix_path.text()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["matrix_path"] = self.configWidget().matrix_path.text()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.configWidget().matrix_path.setText(data["matrix_path"])
