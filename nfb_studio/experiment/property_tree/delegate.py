from PySide2.QtCore import Qt, QModelIndex, QEvent, QRect, Signal
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QVBoxLayout, QLineEdit, QLabel, QFrame

class SequenceItemDelegeate(QStyledItemDelegate):
    """A delegate used with sequence items, e.g. blocks and groups."""
    class Editor(QFrame):
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

            self.line_edit = QLineEdit()
            self.line_edit.setFrame(False)
            self.message_label = QLabel()
            self.message_label.hide()

            # Divi line
            self.divider_line = QFrame()
            self.divider_line.setFrameShape(QFrame.HLine)
            self.divider_line.setFrameShadow(QFrame.Plain)
            self.divider_line.setLineWidth(1)

            layout.addWidget(self.line_edit)
            layout.addWidget(self.divider_line)
            layout.addWidget(self.message_label)

            self.line_edit.textChanged.connect(self._updateMessage)
        
        def fallbackText(self):
            return self._fallback_text

        def text(self):
            """Get the current text value of the editor widget.
            If editing has not been finished succesfully, returns fallbackText().
            """
            view = self.parent().parent()
            (text_ok, reason) = view.experiment().checkName(self.line_edit.text())
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
                view = self.parent().parent()
                (text_ok, reason) = view.experiment().checkName(self.line_edit.text())
            
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

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option, index: QModelIndex):
        editor = self.Editor(parent)
        editor.sizeHintChanged.connect(lambda: self.updateEditorGeometry(editor, option, index))
        return editor

    def setEditorData(self, editor, index: QModelIndex):
        editor.setFallbackText(index.data())
        editor.setText(index.data())
        editor.line_edit.selectAll()
    
    def setModelData(self, editor, model, index: QModelIndex):
        view = editor.parent().parent()
        item = view.itemFromIndex(index)

        if item.parent() is view.blocks:
            view.renameBlockTriggered.emit(item, editor.text())
        elif item.parent() is view.groups:
            view.renameGroupTriggered.emit(item, editor.text())

    def updateEditorGeometry(self, editor, option, index):
        # This is an undocumented property. Why?
        # Probably also accessible as editor.parent().parent()
        view = option.widget

        item_rect = view.visualRect(index)
        hint = editor.sizeHint()
        editor.setGeometry(
            item_rect.topLeft().x(),
            item_rect.topLeft().y(),
            item_rect.width(),
            hint.height()
        )

    def eventFilter(self, editor, event: QEvent):
        if (isinstance(event, QKeyEvent)
            and (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return)
            and editor.text() != editor.line_edit.text()):
            # Current text not accepted
            return False
        
        return super().eventFilter(editor, event)
