"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout

from ..scheme import Node, Output, DataType


class LSLDataSource:
    def __init__(self, name=None, channel_count=None, frequency=None):
        self.name = name
        self.channel_count = channel_count
        self.frequency = frequency


class LSLInput(Node):
    """NFB main source signal."""
    data_sources = [
        LSLDataSource("NVX136_Data", 32, 500),
        LSLDataSource("Mitsar", 30, 250),
    ]

    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            self.input = QComboBox()
            for data_source in LSLInput.data_sources:
                self.input.addItem(data_source.name)
            self.input.currentTextChanged.connect(self.adjust)

            self.channel_count = QLabel()
            self.frequency = QLabel()

            layout = QFormLayout()
            self.setLayout(layout)

            layout.addRow("Data source:", self.input)
            layout.addRow("Channel count:", self.channel_count)
            layout.addRow("Frequency:", self.frequency)

            self.adjust()

        def adjust(self):
            """Adjust displayed values after a change."""
            # Find the data_source with the selected name
            for data_source in LSLInput.data_sources:
                if data_source.name == self.input.currentText():
                    break
            else:
                data_source = None
            
            # Update displays to show new information
            self.channel_count.setText(str(data_source.channel_count))
            self.frequency.setText(str(data_source.frequency))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("LSL Input")
        self.addOutput(Output("LSL data stream", DataType.Unknown))
        self.setConfigWidget(self.Config())
