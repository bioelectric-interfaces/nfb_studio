"""
QDictWidget is the same as QStackedWidget, but the items are addressed by dict keys rather than by indexes.
"""
from PySide2 import QtCore, QtWidgets


class DictWidget(QtWidgets.QStackedWidget):
    currentChanged = QtCore.Signal(object)
    widgetRemoved = QtCore.Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.widgets = {}
        self.current_key = None

    def current(self):
        return self.current_key

    def keyOf(self, widget):
        for key, item in self.widgets.items():
            if item is widget:
                return key

        return None

    def setCurrent(self, key):
        widget = self.widgets[key]
        self.current_key = key

        super().setCurrentWidget(widget)
        self.currentChanged.emit(key)

    def setCurrentWidget(self, widget):
        self.setCurrent(self.keyOf(widget))

    def changeKey(self, key, new_key):
        widget = self.widgets[key]

        self.widgets.pop(key)
        self.widgets[new_key] = widget

        if self.current_key == key:
            self.setCurrent(new_key)

    def remove(self, key):
        widget = self.widgets[key]

        self.widgets.pop(key)
        super().removeWidget(widget)

        if self.current_key == key:
            if len(self) == 0:
                self.current_key = None
            else:
                self.current_key = self.keyOf(self.currentWidget())
            self.currentChanged.emit(self.current_key)

        self.widgetRemoved.emit(key)

    def removeWidget(self, widget):
        self.remove(self.keyOf(widget))

    def __setitem__(self, key, widget):
        self.addWidget(widget)

        if key in self.widgets:
            is_current = (self.current_key == key)

            old_widget = self.widgets[key]
            self.removeWidget(old_widget)

            self.widgets[key] = widget
            if is_current:
                self.setCurrentWidget(widget)
        else:
            self.widgets[key] = widget

    def __getitem__(self, key):
        return self.widgets[key]

    def __len__(self):
        return self.count()
