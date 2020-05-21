"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType


class BandpassFilter(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            # Upper bound ----------------------------------------------------------------------------------------------
            self.lower_bound_enable = QCheckBox()
            self.lower_bound_enable.setChecked(True)
            self.lower_bound_enable.stateChanged.connect(self.adjust)

            self.lower_bound = QDoubleSpinBox()
            self.lower_bound.valueChanged.connect(self.adjust)
            self.lower_bound.setMinimum(0)
            self.lower_bound.setMaximum(250)
            self.lower_bound.setValue(0)

            layout = QHBoxLayout()
            lower_bound_widget = QWidget()
            lower_bound_widget.setLayout(layout)
            layout.addWidget(self.lower_bound_enable)
            layout.addWidget(self.lower_bound)

            # Lower bound ----------------------------------------------------------------------------------------------
            self.upper_bound_enable = QCheckBox()
            self.upper_bound_enable.setChecked(True)
            self.upper_bound_enable.stateChanged.connect(self.adjust)

            self.upper_bound = QDoubleSpinBox()
            self.upper_bound.valueChanged.connect(self.adjust)
            self.upper_bound.setMaximum(250)
            self.upper_bound.setValue(0)

            layout = QHBoxLayout()
            upper_bound_widget = QWidget()
            upper_bound_widget.setLayout(layout)
            layout.addWidget(self.upper_bound_enable)
            layout.addWidget(self.upper_bound)

            # ----------------------------------------------------------------------------------------------------------
            layout = QFormLayout()
            layout.addRow("Lower bound", lower_bound_widget)
            layout.addRow("Upper bound", upper_bound_widget)
            self.setLayout(layout)

        def bounds(self) -> tuple:
            """Return both lower and upper bounds as a tuple.  
            If a bound is disabled, tuple will contain None instead of that bound.
            """
            if self.lower_bound_enable.isChecked():
                lower_bound_value = self.lower_bound.value()
            else:
                lower_bound_value = None
            
            if self.upper_bound_enable.isChecked():
                upper_bound_value = self.upper_bound.value()
            else:
                upper_bound_value = None
            
            return (lower_bound_value, upper_bound_value)

        def adjust(self):
            """Adjust displayed values and limits in response to changes."""
            
            # Enable spinbox widgets based on their checkbox
            self.lower_bound.setEnabled(self.lower_bound_enable.isChecked())
            self.upper_bound.setEnabled(self.upper_bound_enable.isChecked())

            # Adjust min and max so that lower_bound is never higher than upper_bound
            if self.lower_bound_enable.isChecked():
                self.upper_bound.setMinimum(self.lower_bound.value())
            else:
                self.upper_bound.setMinimum(0)
            
            if self.upper_bound_enable.isChecked():
                self.lower_bound.setMinimum(self.upper_bound.value())
            else:
                self.lower_bound.setMaximum(250)


    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Bandpass Filter")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())

    def bounds(self) -> tuple:
        """Return both lower and upper bounds as a tuple.  
        If a bound is disabled, tuple will contain None instead of that bound.
        """
        return self.configWidget().bounds()
