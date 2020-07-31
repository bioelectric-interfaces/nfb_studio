"""A widget for selecting a file or directory, akin to QFileDialog."""
from PySide2.QtWidgets import QWidget, QLineEdit, QFileDialog, QPushButton, QHBoxLayout


class FileSelect(QWidget):
    """A widget for selecting a file or directory, akin to QFileDialog."""
    def __init__(self, parent=None, dialog=None):
        super().__init__(parent)

        self._input = QLineEdit()
        self._button = QPushButton("Browse...")
        self._dialog = dialog or QFileDialog(self)
        self._appended_extension = None

        self._button.clicked.connect(self._dialog.exec_)
        self._dialog.fileSelected.connect(self._input.setText)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self._input)
        layout.addWidget(self._button)
    
    def text(self):
        return self.input().text()

    def input(self):
        return self._input
    
    def button(self):
        return self._button
    
    def dialog(self):
        return self._dialog
    
    def setDialog(self, dialog):
        self._dialog = dialog
        
        self._button.clicked.disconnect()
        self._button.clicked.connect(self._dialog.exec_)
        self._dialog.fileSelected.connect(self._input.setText)
