"""Base class for BlockDict and GroupDict."""
from itertools import count
from collections.abc import MutableMapping

from PySide2.QtCore import QObject, Signal


class ItemDictMetaclass(type(QObject), type(MutableMapping)):
    pass


class ItemDict(QObject, MutableMapping, metaclass=ItemDictMetaclass):
    """Internally used dictionary superclass for blocks and groups.
    This dictionary also contains some logic related to naming new items.
    """
    stored_cls = object

    itemAdded = Signal(str)
    itemRemoved = Signal(str)
    itemRenamed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self._experiment = None
        self._data = {}

    def experiment(self):
        return self._experiment
    
    def setExperiment(self, ex):
        self._experiment = ex

    def getName(self):
        """Get an unused name that can be used as a placeholder, such as "Block1"."""
        for i in count(1):
            name = self.stored_cls.__qualname__ + str(i)
            if self.isAcceptedName(name):
                return name
    
    def isAcceptedName(self, key):
        """Returns True if a name can be used for a new block."""
        return not key in self

    def __getitem__(self, key: str):
        return self._data.__getitem__(key)
    
    def __setitem__(self, key: str, value):
        if not isinstance(key, str):
            raise TypeError("Item name must be of type \"str\", not \"" + type(key) + "\"")

        if not isinstance(value, self.stored_cls):
            raise TypeError(
                "Dict value must be of type \""
                + self.stored_cls.__qualname__
                + "\", not \""
                + type(value).__qualname__
                + "\""
            )

        self._data.__setitem__(key, value)
        self.itemAdded.emit(key)
        self.updateView(key)
    
    def __delitem__(self, key: str):
        self._data.__delitem__(key)
        self.itemRemoved.emit(key)
        self.updateView(key)
    
    def rename(self, old_key, new_key):
        """Rename an item in the dict, changing the key. Emits itemRenamed signal."""
        if old_key not in self:
            raise KeyError("No key \"" + old_key + "\" in dict")

        self.blockSignals(True)
        self[new_key] = self.pop(old_key)
        self.blockSignals(False)

        self.itemRenamed.emit(old_key, new_key)

    def __iter__(self):
        return self._data.__iter__()
    
    def __len__(self):
        return self._data.__len__()

    def updateView(self, key):
        pass

    def serialize(self) -> dict:
        data = {
            "data": self._data
        }
        
        return data
    
    def deserialize(self, data: dict):
        self._data = data["data"]
        