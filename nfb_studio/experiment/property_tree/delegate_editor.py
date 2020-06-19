from PySide2.QtCore import Qt, QModelIndex, QEvent, QRect, Signal
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QVBoxLayout, QLineEdit, QLabel, QFrame


class PropertyTreeDelegateEditor(QFrame):
    """A special editor that handles renaming blocks and groups."""
    sizeHintChanged = Signal(object)
    """Emitted when the widget changes sizeHint. Delegate should update it's geometry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)            
        self.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.Panel | QFrame.Plain)

        self._fallback_text = None
        self._experiment = None

        self.line_edit = QLineEdit()
        self.line_edit.setFrame(False)
        self.message_label = QLabel()
        self.message_label.hide()

        # Divider line
        self.divider_line = QFrame()
        self.divider_line.setFrameShape(QFrame.HLine)
        self.divider_line.setFrameShadow(QFrame.Plain)
        self.divider_line.setLineWidth(1)

        layout.addWidget(self.line_edit)
        layout.addWidget(self.divider_line)
        layout.addWidget(self.message_label)

        self.line_edit.textChanged.connect(self._updateMessage)
    
    def experiment(self):
        return self._experiment

    def setExperiment(self, ex):
        self._experiment = ex

    def fallbackText(self):
        return self._fallback_text

    def text(self):
        """Get the current text value of the editor widget.
        If editing has not been finished succesfully, returns fallbackText().
        """
        (text_ok, reason) = self.experiment().checkName(self.line_edit.text())
        if text_ok:
            return self.line_edit.text()
        else:
            return self.fallbackText()
    
    def setFallbackText(self, text):
        """Set the fallback text value to be used if the editing was not succesfully finished.
        The text() method returns this value or the line_edit text.
        """
        self._fallback_text = text

    def setText(self, text):
        """Set currently editable text. Equivalent to self.line_edit.setText."""
        self.line_edit.setText(text)
    
    def _updateMessage(self):
        """Update the displayed message in response to changed text."""
        if self.line_edit.text() == self.fallbackText():
            # Perform no check
            text_ok = True
        else:
            (text_ok, reason) = self.experiment().checkName(self.line_edit.text())
        
        if text_ok:
            self.message_label.hide()
            self.divider_line.hide()
        else:
            self.message_label.setText(reason)
            self.message_label.show()
            self.divider_line.show()
        
        self.sizeHintChanged.emit(self)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.line_edit.setFocus()
