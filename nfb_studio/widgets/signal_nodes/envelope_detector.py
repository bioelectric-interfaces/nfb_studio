"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox

from ..scheme import Node, Input, Output, DataType


class EnvelopeDetector(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self._smoothing_factor = QDoubleSpinBox()
            self._smoothing_factor.setValue(0)  # TODO: Is this the correct default value?
            self._smoothing_factor.setMinimum(0)
            self._smoothing_factor.setMaximum(1)
            self._smoothing_factor.setSingleStep(0.1)
            self._smoothing_factor.setPrefix("x")

            self._method = QComboBox()
            self._method.addItem("Rectification")
            self._method.addItem("Fourier Transform")
            self._method.addItem("Hilbert Transform")
            self._method.addItem("cFIR")

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Smoothing factor", self._smoothing_factor)
            layout.addRow("Method", self._method)

        def smoothingFactor(self) -> float:
            return self._smoothing_factor.value()
        
        def setSmoothingFactor(self, factor: float):
            self._smoothing_factor.setValue(factor)
        
        def method(self) -> str:
            return self._method.currentText()
        
        def setMethod(self, method: str):
            self._method.setCurrentText(method)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Envelope Detector")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())

    def smoothingFactor(self) -> float:
        return self.configWidget().smoothingFactor()
    
    def setSmoothingFactor(self, factor: float):
        self.configWidget().setSmoothingFactor(factor)
    
    def method(self) -> str:
        return self.configWidget().method()
    
    def setMethod(self, method: str):
        self.configWidget().setMethod(method)

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
