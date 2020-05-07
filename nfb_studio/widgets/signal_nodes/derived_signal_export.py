"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit

from ..signal import Node, Input, Output, DataType
from ..signal.scheme.data_type import Unknown


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
        self.addInput(Input("Input", Unknown))
        self.addOutput(Output("Output", Unknown))

        self.setConfigWidget(self.Config())
