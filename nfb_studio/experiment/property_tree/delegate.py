from PySide2.QtCore import Qt, QModelIndex, QEvent, QRect, Signal
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QWidget, QStyledItemDelegate, QVBoxLayout, QLineEdit, QLabel, QFrame

from .delegate_editor import PropertyTreeDelegateEditor


class PropertyTreeDelegate(QStyledItemDelegate):
    """A delegate used with sequence items, e.g. blocks and groups."""
    Editor = PropertyTreeDelegateEditor

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option, index: QModelIndex):
        editor = self.Editor(parent)
        editor.setExperiment(index.model().experiment())
        editor.sizeHintChanged.connect(lambda: self.updateEditorGeometry(editor, option, index))
        return editor

    def setEditorData(self, editor, index: QModelIndex):
        editor.setFallbackText(index.data())
        editor.setText(index.data())
        editor.line_edit.selectAll()
    
    def setModelData(self, editor, model, index: QModelIndex):
        item = model.itemFromIndex(index)

        if item.parent() is model.blocks:
            model.renameBlockTriggered.emit(item, editor.text())
        elif item.parent() is model.groups:
            model.renameGroupTriggered.emit(item, editor.text())

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
