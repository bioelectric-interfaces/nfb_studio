from PySide2.QtCore import Signal
from PySide2.QtWidgets import QStackedWidget


class StackedDictWidget(QStackedWidget):
    """An alternative to QStackedWidget that addresses it's components by key in a dict instead of by index."""
    currentChanged = Signal(object)
    widgetRemoved = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._widgets = {}
    
    def addWidget(self, key, widget):
        self.removeWidget(key)  # Remove old widget

        super().addWidget(widget)
        self._widgets[key] = widget

    def removeWidget(self, key):
        widget = self.widget(key)

        if widget is not None:
            super().removeWidget(widget)
            self._widgets.pop(key)

            self.widgetRemoved.emit(key)
        
        return widget
    
    def widget(self, key):
        return self._widgets.get(key, None)
    
    def keyOf(self, widget):
        for key, value in self._widgets.items():
            if value == widget:
                return key

        return None
    
    def setCurrentKey(self, key):
        self.setCurrentWidget(self.widget(key))
    
    def setCurrentWidget(self, widget):
        assert self.keyOf(widget) is not None

        if widget != self.currentWidget():
            self.currentChanged.emit(self.keyOf(widget))

        super().setCurrentWidget(widget)

    def currentKey(self):
        return self.keyOf(self.currentWidget())
