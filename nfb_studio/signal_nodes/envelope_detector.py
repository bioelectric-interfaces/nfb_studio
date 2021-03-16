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

            self.smoother_type = QComboBox()
            for name in EnvelopeDetector.smoother_name_to_type:
                self.smoother_type.addItem(name)
            self.smoother_type.currentTextChanged.connect(self.updateModel)

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Smoothing factor", self.smoothing_factor)
            layout.addRow("Method", self.method)
            layout.addRow("Smoother type", self.smoother_type)

        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            smoothing_factor = self.smoothing_factor.value()
            method = self.method.currentText()
            smoother_type = n.smoother_name_to_type[self.smoother_type.currentText()]

            n.setSmoothingFactor(smoothing_factor)
            n.setMethod(method)
            n.setSmootherType(smoother_type)
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.smoothing_factor.blockSignals(True)
            self.method.blockSignals(True)
            self.smoother_type.blockSignals(True)

            self.smoothing_factor.setValue(n.smoothingFactor())
            self.method.setCurrentText(n.method())
            self.smoother_type.setCurrentText(n.smoother_type_to_name[n.smootherType()])

            self.smoothing_factor.blockSignals(False)
            self.method.blockSignals(False)
            self.smoother_type.blockSignals(False)

    default_smoothing_factor = 0.0  # TODO: Is this the correct default value?
    default_method = "Rectification"
    default_smoother_type = "exp"

    smoother_type_to_name = {
        "exp": "Exponential",
        "savgol": "Savitzky-Golay"
    }
    smoother_name_to_type = {v: k for k, v in smoother_type_to_name.items()}

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._smoothing_factor = self.default_smoothing_factor
        self._method = self.default_method
        self._smoother_type = self.default_smoother_type
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

    def smootherType(self):
        return self._smoother_type
    
    def setSmootherType(self, value, /):
        self._smoother_type = value
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        self.setDescription(
            f"Smoothing Factor: x{self.smoothingFactor()}\n"
            f"Method: {self.method()}\n"
            f"Smoother type: {self.smoother_type_to_name[self.smootherType()]}"
        )

    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fSmoothingFactor"] = self.smoothingFactor()
        signal["method"] = self.method()
        signal["sTemporalSmootherType"] = self.smootherType()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["smoothing_factor"] = self.smoothingFactor()
        data["method"] = self.method()
        data["smoother_type"] = self.smootherType()
        return data
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = super().deserialize(data)
        obj.setSmoothingFactor(data["smoothing_factor"])
        obj.setMethod(data["method"])
        obj.setSmootherType(data["smoother_type"])

        return obj
