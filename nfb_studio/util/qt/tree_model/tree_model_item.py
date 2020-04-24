from sortedcontainers import SortedKeyList

from .abstract_tree_model_item import AbstractTreeModelItem

class TreeModelItem(AbstractTreeModelItem):
    def __init__(self):
        super().__init__()
        self._text = "Item"
        
        self._children = []
        self._sorting_enabled = False
        self._sorting_key = lambda item: item.text()

    def isSortingEnabled(self):
        return self._sorting_enabled
    
    def setSortingEnabled(self, enable):
        # No change if state is the same
        if self._sorting_enabled == enable:
            return
        
        self._sorting_enabled = enable

        # If not in model, quickly swap containers ---------------------------------------------------------------------
        if self.model() is None:
            if self._sorting_enabled:
                self._children = SortedKeyList(self._children, self._sorting_key)
            else:
                self._children = list(self._children)
            return
        
        # Remove unsorted items ----------------------------------------------------------------------------------------
        self.model().beginRemoveRows(self.modelIndex(), 0, self.childrenCount()-1)

        old_children = self._children
        if self._sorting_enabled:
            self._children = SortedKeyList(key=self._sorting_key)
        else:
            self._children = []

        self.model().endRemoveRows()

        # Add sorted items ---------------------------------------------------------------------------------------------
        self.model().beginInsertRows(self.modelIndex(), 0, len(old_children)-1)
        
        if self._sorting_enabled:
            self._children.update(old_children)
        else:
            self._children.extend(old_children)

        self.model().endInsertRows()
    
    def sortingKey(self):
        return self._sorting_key

    def setSortingKey(self, key):
        self._sorting_key = key

        if self.isSortingEnabled():
            if self.model() is not None:
                self.model().beginResetModel()
        
            self._children = SortedKeyList(self._children, self._sorting_key)
            
            if self.model() is not None:
                self.model().endResetModel()

    def text(self) -> str:
        return self._text

    def setText(self, text: str):
        self._text = text

    def item(self, index):
        return self._children[index]
    
    def index(self, item):
        return self._children.index(item)
    
    def addItem(self, item):
        self.insertItem(self.childrenCount(), item)
    
    def insertItem(self, index, item):
        if item.parent() is not None:
            item.parent().removeItem(item.parent().index(item))

        if self.isSortingEnabled():
            # If sorting is enabled, index parameter is ignored
            if self.model() is not None:
                self.model().beginInsertRows(
                    self.modelIndex(), 
                    self._children.bisect_right(item), 
                    self._children.bisect_right(item)
                )
            
            item._setParent(self)
            self._children.add(item)
        else:
            if self.model() is not None:
                self.model().beginInsertRows(self.modelIndex(), index, index)
            
            item._setParent(self)
            self._children.insert(index, item)

        if self.model() is not None:
            self.model().endInsertRows()
    
    def removeItem(self, index):
        if self.model() is not None:
            self.model().beginRemoveRows(self.modelIndex(), index, index)
        
        item = self.item(index)
        self._children.pop(index)
        item._setParent(None)

        if self.model() is not None:
            self.model().endRemoveRows()
        
        return item
    
    def children(self):
        return iter(self._children)

    def childrenCount(self):
        return len(self._children)
