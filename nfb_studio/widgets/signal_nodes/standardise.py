"""NFB main source signal."""
import sys
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..signal import Node, Input, Output, DataType
from ..signal.scheme.data_type import Unknown


class Standardise(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            # Add a new layout
            self.fAverage_label = QLabel("fAverage")
            self.fAverage_input = QDoubleSpinBox()
            self.fAverage_input.setMaximum(sys.float_info.max)

            self.fStdDev_label = QLabel("fStdDev")
            self.fStdDev_input = QDoubleSpinBox()
            self.fStdDev_input.setValue(1)
            self.fStdDev_input.setMaximum(sys.float_info.max)

            form = QFormLayout()
            form.addRow(self.fAverage_label, self.fAverage_input)
            form.addRow(self.fStdDev_label, self.fStdDev_input)
            self.setLayout(form)

            # Disallow the widget window from expanding past the form's recommended size
            self.setMaximumHeight(form.sizeHint().height())

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTitle("Standardise")
        self.addInput(Input("Input", Unknown))
        self.addOutput(Output("Output", Unknown))

        self.setConfigWidget(self.Config())
