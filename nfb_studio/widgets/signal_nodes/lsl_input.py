"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout

from ..scheme import Node, Output, DataType
from .signal_node import SignalNode


class LSLDataSource:
    def __init__(self, name=None, channel_count=None, frequency=None):
        self.name = name
        self.channel_count = channel_count
        self.frequency = frequency


class LSLInput(SignalNode):
    """NFB main source signal."""
    data_sources = [
        LSLDataSource("NVX136_Data", 32, 500),
        LSLDataSource("Mitsar", 30, 250),
    ]

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            self.data_source = QComboBox()
            for source in LSLInput.data_sources:
                self.input.addItem(source.name)
            self.data_source.currentTextChanged.connect(self.adjust)

            self.channel_count = QLabel()
            self.channel_count.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
            self.channel_count.setAlignment(QtCore.Qt.AlignCenter)
            self.channel_count.setMargin(5)

            self.frequency = QLabel()
            self.frequency.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
            self.frequency.setAlignment(QtCore.Qt.AlignCenter)
            self.frequency.setMargin(5)

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Data source:", self.data_source)
            layout.addRow("Channel count:", self.channel_count)
            layout.addRow("Frequency:", self.frequency)

            self.adjust()

        def adjust(self):
            """Adjust displayed values after a change."""
            # Sync changes with the node
            self.sync()

            # Find the data_source with the selected name
            for data_source in LSLInput.data_sources:
                if data_source.name == self.input.currentText():
                    break
            else:
                data_source = None
            
            # Update displays to show new information
            self.channel_count.setText(str(data_source.channel_count))
            self.frequency.setText(str(data_source.frequency))

        def sync(self):
            n = self.node()
            if n is None:
                return
            
            n._data_source = self.data_source.currentText()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("LSL Input")
        self.addOutput(Output("LSL data stream", DataType.Unknown))
        
        self._data_source = self.data_sources[0].name
        self.sync()

    def dataSource(self):
        return self._data_source
    
    def setDataSource(self, source: str, /):
        # TODO: Perform a check that this data source exists
        self._data_source = source
        self.sync()

    def sync(self):
        if not self.hasConfigWidget():
            return
        
        w = self.configWidget()
        w.data_source.setCurrentText(self.dataSource())

    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        pass
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["data_source"] = self.dataSource()
        return data
    
    def deserialize(self, data: dict):
        super().deserialize(data)

        self.setDataSource(data["data_source"])
