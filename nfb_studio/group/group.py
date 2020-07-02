"""NFB block group."""
from typing import Union
from collections.abc import MutableSequence

from PySide2.QtCore import QObject


class GroupMetaclass(type(QObject), type(MutableSequence)):
    """Metaclass for Group. Merges QObject and MutableSequence metaclasses."""


class Group(QObject, MutableSequence, metaclass=GroupMetaclass):
    """A group of experiment blocks.
    Experiment consists of a sequence of blocks and block groups that are executed in some order. A group consists of
    a sequence of blocks. Each block can be repeated one or more times, and can be set to execute in random order.

    This class contains two lists that are always the same size: a list of blocks, and a list of repeats each block has
    set. This class also is a MutableSequence, which means you can get and set both values at once with the operator[].
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.blocks = []
        self.repeats = []

        self.random_order = False

        self._view = None

    def view(self):
        """Return the view (config widget) for this group."""
        return self._view
    
    def setView(self, view, /):
        view.setModel(self)
    
    def updateView(self):
        view = self.view()
        if view is None:
            return
        
        view.blocks.setText(" ".join(self.blocks))
        view.repeats.setText(" ".join([str(x) for x in self.repeats]))
        view.random_order.setChecked(self.random_order)

    # MutableSequence method implementations ===========================================================================
    def __getitem__(self, index):
        return (self.blocks[index], self.repeats[index])
    
    def __setitem__(self, index, value):
        del self[index]
        self.insert(index, value)
    
    def __delitem__(self, index):
        del self.blocks[index]
        del self.repeats[index]
    
    def __len__(self):
        assert len(self.blocks) == len(self.repeats)
        return len(self.blocks)
    
    def insert(self, index, value):
        """Insert a new item into the group.
        Value can either be a single block or a tuple(block, repeats).
        """
        if not isinstance(value, tuple):
            value = (value, 1)
        
        self.blocks.insert(index, value[0])
        self.repeats.insert(index, value[1])

    def serialize(self) -> dict:
        return {
            "blocks": self.blocks,
            "repeats": self.repeats,
        }

    def deserialize(self, data: dict):
        self.blocks = data["blocks"]
        self.repeats = data["repeats"]

    # NFB Export =======================================================================================================
    def nfb_export_data(self) -> dict:
        """Export this group into a dict to be encoded as XML for NFBLab.
        Bool items are written as-is. The encoder is responsible for converting them into int format.
        """
        # Build sList and sNumberList ----------------------------------------------------------------------------------
        name_list = []
        repeat_list = []

        for i in range(len(self)):  # FIXME: Change to regular iteration
            item = self[i]
            name_list.append(item[0])
            repeat_list.append(item[1])

        # Export XML data ----------------------------------------------------------------------------------------------
        data = {}

        data["sList"] = " ".join(name_list)
        data["sNumberList"] = " ".join(str(number) for number in repeat_list)
        data["bShuffle"] = self.random_order

        return data
    
    @classmethod
    def nfb_import_data(cls, data: dict):
        """Import this group from a dict from NFBLab."""
        group = cls()

        group.random_order = bool(float(data["bShuffle"]))

        if data["sList"] is not None:
            group.blocks = data["sList"].split(" ")
            group.repeats = [int(number) for number in data["sNumberList"].split(" ")]

        return group
