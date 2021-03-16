"""Config widget for a group of blocks."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox


class GroupView(QWidget):
    """Config widget for a group of blocks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self._model = None

        self.blocks = QLineEdit()
        self.repeats = QLineEdit()
        self.random_order = QCheckBox()

        layout.addRow("Blocks", self.blocks)
        layout.addRow("Repeats", self.repeats)
        layout.addRow("Random order", self.random_order)

    def model(self):
        return self._model
    
    def setModel(self, group, /):
        self._model = group
        self.updateView()

    def updateModel(self):
        """Copy data from this view to the group model.
        A similarly named function in the group copies data the opposite way. Use one or the other depending on where
        data was changed.
        """
        model = self.model()

        model.random_order = self.random_order.isChecked()
        if self.blocks.text() == "":
            model.blocks = []
            model.repeats = []
        else:
            model.blocks = self.blocks.text().split(" ")
            model.repeats = [int(number) for number in self.repeats.text().split(" ")]

    def updateView(self):
        model = self.model()
        if model is None:
            return
        
        self.blocks.setText(" ".join(model.blocks))
        self.repeats.setText(" ".join([str(x) for x in model.repeats]))
        self.random_order.setChecked(model.random_order)