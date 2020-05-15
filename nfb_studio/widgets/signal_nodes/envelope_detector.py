"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType


class EnvelopeDetector(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.smoothing_factor = QDoubleSpinBox()
            self.smoothing_factor.setValue(0)
            self.smoothing_factor.setMinimum(0)
            self.smoothing_factor.setMaximum(1)
            self.smoothing_factor.setSingleStep(0.1)

            self.method = QComboBox()
            self.method.addItem("Rectification")
            self.method.addItem("Fourier Transform")
            self.method.addItem("Hilbert Transform")
            self.method.addItem("cFIR")

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Smoothing factor", self.smoothing_factor)
            layout.addRow("Method", self.method)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())
