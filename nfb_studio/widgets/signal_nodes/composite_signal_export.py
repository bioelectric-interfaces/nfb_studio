"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode


class CompositeSignalExport(SignalNode):
    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.signal_name = QLineEdit("Signal")
            self.signal_name.editingFinished.connect(self.sync)

            self.expression = QLineEdit()
            self.expression.editingFinished.connect(self.sync)

            layout = QFormLayout()
            self.setLayout(layout)
            layout.addRow("Signal name", self.signal_name)
            layout.addRow("Expression", self.expression)
        
        def sync(self):
            n = self.node()
            if n is None:
                return
            
            n._signal_name = self.signal_name.text()
            n._expression = self.expression.text()
    

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Composite Signal Export")
        i = Input("Input", DataType.Unknown)
        i.setMultiple(True)
        self.addInput(i)

        self._signal_name = "Signal"
        self._expression = ""
        self.sync()

    def signalName(self) -> str:
        return self._signal_name

    def expression(self) -> str:
        return self._expression

    def setSignalName(self, name: str, /):
        self._signal_name = name
        self.sync()
    
    def setExpression(self, eq: str, /):
        self._expression = eq
        self.sync()
    
    def sync(self):
        if not self.hasConfigWidget():
            return
        
        w = self.configWidget()
        w.signal_name.setText(self.signalName())
        w.expression.setText(self.expression())

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["sSignalName"] = self.signalName()
        signal["sExpression"] = self.expression()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["signal_name"] = self.signalName()
        data["expression"] = self.expression()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)
        self.setSignalName(data["signal_name"])
        self.setExpression(data["expression"])
