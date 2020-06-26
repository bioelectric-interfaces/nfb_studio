"""NFB main source signal."""
import sys
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .spatial_filter import SpatialFilter
from .bandpass_filter import BandpassFilter
from .envelope_detector import EnvelopeDetector


class Standardise(SignalNode):
    input_type = DataType(105, convertible_from=[
        SpatialFilter.output_type,
        BandpassFilter.output_type,
        EnvelopeDetector.output_type,
    ])
    output_type = DataType(106)

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            # Add a new layout
            self.average = QDoubleSpinBox()
            self.average.setMaximum(sys.float_info.max)  # TODO: proper max

            self.standard_deviation = QDoubleSpinBox()
            self.standard_deviation.setMaximum(sys.float_info.max)  # TODO: proper max

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Average", self.average)
            layout.addRow("Std. Deviation", self.standard_deviation)
        
        def updateModel(self):
            n = self.node()
            if n is None:
                return

            n._average = self.average.value()
            n._standard_deviation = self.standard_deviation.value()
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.average.setValue(n.average())
            self.standard_deviation.setValue(n.standardDeviation())

    default_average = 0
    default_standard_deviation = 1

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.setTitle("Standardise")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._average = self.default_average
        self._standard_deviation = self.default_standard_deviation
        self.updateView()
    
    def average(self):
        return self._average
    
    def standardDeviation(self):
        return self._standard_deviation
    
    def setAverage(self, value, /):
        self._average = value
        self.updateView()
    
    def setStandardDeviation(self, value, /):
        self._standard_deviation = value
        self.updateView()

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fAverage"] = self.average()
        signal["fStdDev"] = self.standardDeviation()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["average"] = self.average()
        data["standard_deviation"] = self.standardDeviation()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.setAverage(data["average"])
        self.setStandardDeviation(data["standard_deviation"])
