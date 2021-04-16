from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog


class PathEdit(QWidget):
    pathChanged = Signal(str)

    def __init__(self, path="", parent=None):
        super().__init__(parent)

        ly = QHBoxLayout()
        self.setLayout(ly)

        self.setContentsMargins(0, 0, 0, 0)
        ly.setContentsMargins(0, 0, 0, 0)

        self._line_edit = QLineEdit(path)
        self._button = QPushButton("Browse...")
        self._dialog = QFileDialog(self)

        self._line_edit.textChanged.connect(self.pathChanged.emit)

        self._button.clicked.connect(self.browse)

        ly.addWidget(self._line_edit)
        ly.addWidget(self._button)
    
    def text(self):
        return self._line_edit.text()
    
    def buttonText(self):
        return self._button.text()

    def setText(self, text):
        self._line_edit.setText(text)

    def setButtonText(self, text):
        self._button.setText(text)

    def dialog(self):
        return self._dialog
    
    def setDialog(self, dialog):
        self._dialog = dialog
    
    def browse(self):
        if self._dialog.exec_():
            self._line_edit.setText(self._dialog.selectedFiles()[0])
