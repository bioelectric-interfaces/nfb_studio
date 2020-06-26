"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode


class DerivedSignalExport(SignalNode):
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
            
            n._signal_name = self.signal_name.text()
    
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.signal_name.setText(n.signalName())

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Derived Signal Export")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self._signal_name = "Signal"
        self.updateView()

    def signalName(self) -> str:
        return self._signal_name

    def setSignalName(self, name: str, /):
        self._signal_name = name
        self.updateView()

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["sSignalName"] = self.signalName()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["signal_name"] = self.signalName()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)
        self.setSignalName(data["signal_name"])
