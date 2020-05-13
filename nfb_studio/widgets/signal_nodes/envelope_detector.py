"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType


class EnvelopeDetector(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.fSmoothingFactor_label = QLabel("fSmoothingFactor")
            self.fSmoothingFactor_input = QDoubleSpinBox()
            self.fSmoothingFactor_input.setValue(0)
            self.fSmoothingFactor_input.setMinimum(0)
            self.fSmoothingFactor_input.setMaximum(1)
            self.fSmoothingFactor_input.setSingleStep(0.1)

            form = QFormLayout()
            form.addRow(self.fSmoothingFactor_label, self.fSmoothingFactor_input)
            self.setLayout(form)

            # Disallow the widget window from expanding past the form's recommended size
            self.setMaximumHeight(form.sizeHint().height())

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())
