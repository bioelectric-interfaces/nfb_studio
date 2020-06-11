"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode


class BandpassFilter(SignalNode):
    class Config(SignalNode.Config):
        """Config widget displayed for BandpassFilter."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            # Upper bound ----------------------------------------------------------------------------------------------
            self.lower_bound_enable = QCheckBox()
            self.lower_bound_enable.setChecked(True)
            self.lower_bound_enable.stateChanged.connect(self.adjust)

            self.lower_bound = QDoubleSpinBox()
            self.lower_bound.valueChanged.connect(self.adjust)
            self.lower_bound.setMinimum(0)
            self.lower_bound.setMaximum(250)
            self.lower_bound.setSuffix("Hz")

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
            self.lower_bound.setMinimum(0)
            self.upper_bound.setMaximum(250)
            self.upper_bound.setSuffix("Hz")

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

        def sync(self):
            n = self.node()
            if n is None:
                return
            
            if self.lower_bound_enable.isChecked():
                # Value is set direcly to a private field to prevent n.sync() from being called.
                n._lower_bound = self.lower_bound.value()
            else:
                n._lower_bound = None
            
            if self.upper_bound_enable.isChecked():
                n._upper_bound = self.upper_bound.value()
            else:
                n._upper_bound = None

        def adjust(self):
            """Adjust displayed values and limits in response to changes."""
            # Propagate changes to the node
            self.sync()
            
            # Enable spinbox widgets based on their checkbox
            self.lower_bound.setEnabled(self.lower_bound_enable.isChecked())
            self.upper_bound.setEnabled(self.upper_bound_enable.isChecked())

            # Adjust min and max so that lower_bound is never higher than upper_bound
            if self.lower_bound_enable.isChecked():
                self.upper_bound.setMinimum(self.lower_bound.value())
            else:
                self.upper_bound.setMinimum(0)
            
            if self.upper_bound_enable.isChecked():
                self.lower_bound.setMaximum(self.upper_bound.value())
            else:
                self.lower_bound.setMaximum(250)

    default_lower_bound = 0
    default_upper_bound = 250

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Bandpass Filter")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self._lower_bound = self.default_lower_bound
        self._upper_bound = self.default_upper_bound
        self.sync()
    
    def lowerBound(self):
        return self._lower_bound
    
    def upperBound(self):
        return self._upper_bound
    
    def setLowerBound(self, value, /):
        self._lower_bound = value
        self.sync()
    
    def setUpperBound(self, value, /):
        self._upper_bound = value
        self.sync()
    
    def sync(self):
        # Nodes create their config widget on demand. To not create a config widget just for syncing to it, a check is
        # performed.
        if not self.hasConfigWidget():
            return
        
        w = self.configWidget()
        
        # Prevent view fields from emitting signals while they are updated
        w.lower_bound.blockSignals(True)
        w.upper_bound.blockSignals(True)

        if self.upperBound() is None:
            w.upper_bound_enable.setChecked(False)
        else:
            w.upper_bound_enable.setChecked(True)
            w.upper_bound.setValue(self.upperBound())
        
        if self.lowerBound() is None:
            w.lower_bound_enable.setChecked(False)
        else:
            w.lower_bound_enable.setChecked(True)
            w.lower_bound.setValue(self.lowerBound())
        
        # Release the block and call adjust
        w.lower_bound.blockSignals(False)
        w.upper_bound.blockSignals(False)
        w.adjust()

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fBandpassLowHz"] = self.lowerBound()
        signal["fBandpassHighHz"] = self.upperBound()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["lower_bound"] = self.lowerBound()
        data["upper_bound"] = self.upperBound()

        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)
        
        self.setLowerBound(data["lower_bound"])
        self.setUpperBound(data["upper_bound"])
