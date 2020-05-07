"""Config widget for a group of blocks."""
import itertools
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QCheckBox


class GroupConfig(QWidget):
    """Config widget for a group of blocks."""
    newid = itertools.count()

    def __init__(self, group, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self.data = group

        self.name = QLabel("Group" + str(next(self.newid)))
        self.data.name = self.name.text()

        self.blocks = QLineEdit()
        self.repeats = QLineEdit()
        self.random_order = QCheckBox()

        layout.addRow("Name", self.name)
        layout.addRow("Blocks", self.blocks)
        layout.addRow("Repeats", self.repeats)
        layout.addRow("Random order", self.random_order)
