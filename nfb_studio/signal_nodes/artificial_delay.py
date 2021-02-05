"""NFB main source signal."""
from PySide2.QtWidgets import QFormLayout, QSpinBox

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .envelope_detector import EnvelopeDetector


class ArtificialDelay(SignalNode):
    input_type = EnvelopeDetector.output_type
    output_type = DataType(109)

    class Config(SignalNode.Config):
        """Config widget displayed for ArtificialDelay."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.delay = QSpinBox()
            self.delay.setSuffix(" ms")
            self.delay.setMinimum(0)
            self.delay.setMaximum(1000000)
            self.delay.valueChanged.connect(self.updateModel)

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Delay:", self.delay)
        
        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            n.setDelay(self.delay.value())
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.delay.blockSignals(True)
            self.delay.setValue(n.delay())
            self.delay.blockSignals(False)

    default_delay = 1000

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Artificial Delay")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._delay = self.default_delay
        self._adjust()

    def delay(self) -> int:
        return self._delay
    
    def setDelay(self, delay: int, /):
        self._delay = delay
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        self.setDescription(f"{self.delay()} ms")

    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["iDelayMs"] = self.delay()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["delay"] = self.delay()
        return data
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = super().deserialize(data)
        obj.setDelay(data["delay"])

        return obj
