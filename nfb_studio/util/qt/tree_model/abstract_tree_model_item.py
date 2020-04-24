from PySide2.QtCore import QModelIndex


class AbstractTreeModelItem:
        def __init__(self):
            self._parent = None
            self._model = None
        
        def model(self):
            item = self
            while(item.parent() is not None):
                item = item.parent()

            # Only top level item (root) has self._model not None.
            return item._model

        def parent(self):
            return self._parent

        def item(self, index):
            raise NotImplementedError
        
        def index(self, child_item):
            raise NotImplementedError

        def modelIndex(self):
            if self.parent() is None:
                return QModelIndex()

            return self.model().createIndex(self.parent().index(self), 0, self)

        def addItem(self, item):
            raise NotImplementedError

        def removeItem(self, index):
            raise NotImplementedError
        
        def childrenCount(self):
            raise NotImplementedError

        def _setParent(self, parent):
            self._parent = parent

        @classmethod
        def _fromModelIndex(cls, index: QModelIndex):
            assert(isinstance(index.internalPointer(), cls))
            return index.internalPointer()
