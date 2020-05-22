"""Config widget for a group of blocks."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QCheckBox


class GroupConfig(QWidget):
    """Config widget for a group of blocks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self._model = None

        self.name = QLabel()

        self.blocks = QLineEdit()
        self.repeats = QLineEdit()
        self.random_order = QCheckBox()

        layout.addRow("Name", self.name)
        layout.addRow("Blocks", self.blocks)
        layout.addRow("Repeats", self.repeats)
        layout.addRow("Random order", self.random_order)

    def model(self):
        return self._model
    
    def setModel(self, group, /):
        self._model = group
        group._view = self
        self._model.sync()

    def sync(self):
        """Sync data from this view to the group model.
        "Sync" in this context means one way copy of data from self to model. A similarly named function in the group
        copies data the opposite way. Use one or the other depending on where data was changed.
        """
        group = self.model()

        group.name = self.name.text()
        group.random_order = self.random_order.isChecked()
        if self.blocks.text() == "":
            group.blocks = []
            group.repeats = []
        else:
            group.blocks = self.blocks.text().split(" ")
            group.repeats = [int(number) for number in self.repeats.text().split(" ")]