"""Config widget for a single experiment block."""
import itertools
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel


class BlockConfig(QWidget):
    """Config widget for a single experiment block."""
    newid = itertools.count()

    def __init__(self, block, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self.data = block

        self.name = QLabel("Block" + str(next(self.newid)))
        self.data.name = self.name.text()

        layout.addRow("Name", self.name)
