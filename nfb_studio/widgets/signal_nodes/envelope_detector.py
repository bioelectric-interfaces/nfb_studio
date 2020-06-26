"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .spatial_filter import SpatialFilter
from .bandpass_filter import BandpassFilter


class EnvelopeDetector(SignalNode):
    input_type = DataType(103, convertible_from=[SpatialFilter.output_type, BandpassFilter.output_type])
    output_type = DataType(104)

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.smoothing_factor = QDoubleSpinBox()
            self.smoothing_factor.setMinimum(0)
            self.smoothing_factor.setMaximum(1)
            self.smoothing_factor.setSingleStep(0.1)
            self.smoothing_factor.setPrefix("x")
            self.smoothing_factor.valueChanged.connect(self.updateModel)

            self.method = QComboBox()
            self.method.addItem("Rectification")
            self.method.addItem("Fourier Transform")
            self.method.addItem("Hilbert Transform")
            self.method.addItem("cFIR")
            self.method.currentTextChanged.connect(self.updateModel)

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Smoothing factor", self.smoothing_factor)
            layout.addRow("Method", self.method)

        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            smoothing_factor = self.smoothing_factor.value()
            method = self.method.currentText()

            n.setSmoothingFactor(smoothing_factor)
            n.setMethod(method)
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.smoothing_factor.blockSignals(True)
            self.method.blockSignals(True)

            self.smoothing_factor.setValue(n.smoothingFactor())
            self.method.setCurrentText(n.method())

            self.smoothing_factor.blockSignals(False)
            self.method.blockSignals(False)

    default_smoothing_factor = 0.0  # TODO: Is this the correct default value?
    default_method = "Rectification"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._smoothing_factor = self.default_smoothing_factor
        self._method = self.default_method
        self._adjust()

    def smoothingFactor(self) -> float:
        return self._smoothing_factor
    
    def setSmoothingFactor(self, factor: float, /):
        self._smoothing_factor = factor
        self._adjust()
    
    def method(self) -> str:
        return self._method
    
    def setMethod(self, method: str, /):
        self._method = method
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        self.setDescription(
            "Smoothing Factor: x{}\nMethod: {}".format(
                self.smoothingFactor(),
                self.method()
            )
        )

    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fSmoothingFactor"] = self.smoothingFactor()
        signal["method"] = self.method()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["smoothing_factor"] = self.smoothingFactor()
        data["method"] = self.method()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.setSmoothingFactor(data["smoothing_factor"])
        self.setMethod(data["method"])
