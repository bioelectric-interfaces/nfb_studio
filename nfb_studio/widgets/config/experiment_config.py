"""Config widget for general properties of an experiment."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit


class ExperimentConfig(QWidget):
    """Config widget for general properties of an experiment."""
    def __init__(self, experiment, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self.data = experiment

        self.name = QLineEdit()

        layout.addRow("Name", self.name)
