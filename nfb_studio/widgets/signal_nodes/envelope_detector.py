"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode


class EnvelopeDetector(SignalNode):
    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.smoothing_factor = QDoubleSpinBox()
            self.smoothing_factor.setMinimum(0)
            self.smoothing_factor.setMaximum(1)
            self.smoothing_factor.setSingleStep(0.1)
            self.smoothing_factor.setPrefix("x")

            self.method = QComboBox()
            self.method.addItem("Rectification")
            self.method.addItem("Fourier Transform")
            self.method.addItem("Hilbert Transform")
            self.method.addItem("cFIR")

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Smoothing factor", self._smoothing_factor)
            layout.addRow("Method", self._method)

        def sync(self):
            n = self.node()
            if n is None:
                return
            
            n._smoothing_factor = self.smoothing_factor.value()
            n._method = self.method.currentText()


    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self._smoothing_factor = 0  # TODO: Is this the correct default value?
        self._method = "Rectification"

    def smoothingFactor(self) -> float:
        return self._smoothing_factor
    
    def setSmoothingFactor(self, factor: float, /):
        self._smoothing_factor = factor
        self.sync()
    
    def method(self) -> str:
        return self._method
    
    def setMethod(self, method: str, /):
        self._method = method
        self.sync()
    
    def sync(self):
        if not self.hasConfigWidget():
            return
        
        w = self.configWidget()
        w.smoothing_factor.setValue(self.smoothingFactor())
        w.method.setCurrentText(self.method())

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
