"""View widget for PropertyTree class."""
from PySide2.QtCore import Qt, QModelIndex, QPoint, Signal
from PySide2.QtWidgets import QTreeView, QMenu

from .delegate import PropertyTreeDelegate


class PropertyTreeView(QTreeView):
    """View widget for PropertyTree class."""
    currentIndexChanged = Signal(object, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setSelectionMode(self.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.setItemDelegate(PropertyTreeDelegate())
        self.clicked.connect(self.setCurrentIndex)

    def currentChanged(self, current: QModelIndex, previous: QModelIndex):
        """The slot that is called when current item is changed.
        Emits currentIndexChanged.
        """
        super().currentChanged(current, previous)
        self.currentIndexChanged.emit(current, previous)

    def showContextMenu(self, point: QPoint):
        model = self.model()
        if model is None:
            return

        global_point = self.viewport().mapToGlobal(point)
        index = self.indexAt(point)
        item = model.itemFromIndex(index)

        if item is model.blocks:
            # Menu for "Blocks" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Block")
            add.triggered.connect(lambda: model.addNewBlock())

            menu.exec_(global_point)
        elif item is model.groups:
            # Menu for "Groups" item -----------------------------------------------------------------------------------
            menu = QMenu()
            add = menu.addAction("New Group")
            add.triggered.connect(lambda: model.addNewGroup())

            menu.exec_(global_point)
        elif item.parent() is model.blocks:
            # Menu for an individual block -----------------------------------------------------------------------------
            menu = QMenu()

            rename = menu.addAction("Rename")
            rename.triggered.connect(lambda: self.edit(index))

            delete = menu.addAction("Delete")
            delete.triggered.connect(lambda: model.removeBlock(item.text()))

            menu.exec_(global_point)
        elif item.parent() is model.groups:
            # Menu for an individual group -----------------------------------------------------------------------------
            menu = QMenu()

            rename = menu.addAction("Rename")
            rename.triggered.connect(lambda: self.edit(index))

            delete = menu.addAction("Delete")
            delete.triggered.connect(lambda: model.removeBlock(item.text()))

            menu.exec_(global_point)
