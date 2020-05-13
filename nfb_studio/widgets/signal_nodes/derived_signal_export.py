"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType


class DerivedSignalExport(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.signalName_input = QLineEdit()

            form = QFormLayout()
            form.addRow("Signal name", self.signalName_input)
            self.setLayout(form)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Derived Signal Export")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())
