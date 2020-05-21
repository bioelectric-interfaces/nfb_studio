"""NFB main source signal."""
import sys
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType


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
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fAverage"] = self.configWidget().fAverage_input.value()
        signal["fStdDev"] = self.configWidget().fStdDev_input.value()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["average"] = self.configWidget().fAverage_input.value()
        data["standard_deviation"] = self.configWidget().fStdDev_input.value()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.configWidget().fAverage_input.setValue(data["average"])
        self.configWidget().fStdDev_input.setValue(data["standard_deviation"])
