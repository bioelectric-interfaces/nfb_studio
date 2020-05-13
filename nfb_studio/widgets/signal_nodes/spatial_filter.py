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
