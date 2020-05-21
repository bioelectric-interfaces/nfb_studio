"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType


class DerivedSignalExport(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.signal_name = QLineEdit("Signal")

            layout = QFormLayout()
            self.setLayout(layout)
            layout.addRow("Signal name", self.signal_name)
        
        def signalName(self) -> str:
            return self.signal_name.text()
        
        def setSignalName(self, name: str):
            self.signal_name.setText(name)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Derived Signal Export")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())
    
    def signalName(self) -> str:
        return self.configWidget().signalName()

    def setSignalName(self, name: str):
        self.configWidget().setSignalName(name)

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["sSignalName"] = self.signalName()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["signal_name"] = self.signalName()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)
        self.configWidget().setSignalName(data["signal_name"])
