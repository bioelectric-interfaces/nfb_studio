"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .spatial_filter import SpatialFilter
from .bandpass_filter import BandpassFilter
from .envelope_detector import EnvelopeDetector
from .standardise import Standardise


class DerivedSignalExport(SignalNode):
    input_type = DataType(107, convertible_from=[
        SpatialFilter.output_type,
        BandpassFilter.output_type,
        EnvelopeDetector.output_type,
        Standardise.output_type,
    ])
    output_type = DataType(108)

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.signal_name = QLineEdit("Signal")
            self.signal_name.editingFinished.connect(self.updateModel)

            layout = QFormLayout()
            self.setLayout(layout)
            layout.addRow("Signal name", self.signal_name)
        
        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            n.setSignalName(self.signal_name.text())
    
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.signal_name.blockSignals(True)
            self.signal_name.setText(n.signalName())
            self.signal_name.blockSignals(False)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Derived Signal Export")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._signal_name = "Signal"
        self._adjust()

    def signalName(self) -> str:
        return self._signal_name

    def setSignalName(self, name: str, /):
        self._signal_name = name
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        self.setDescription(self.signalName())

    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["sSignalName"] = self.signalName()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["signal_name"] = self.signalName()
        return data
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = super().deserialize(data)
        obj.setSignalName(data["signal_name"])

        return obj
