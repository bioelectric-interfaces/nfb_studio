"""NFB block group."""
from typing import Union
from collections.abc import MutableSequence

from PySide2.QtCore import QObject

from .block import Block


class GroupMetaclass(type(QObject), type(MutableSequence)):
    pass


class Group(QObject, MutableSequence, metaclass=GroupMetaclass):
    """A group of experiment blocks.
    Experiment consists of a sequence of blocks and block groups that are executed in some order. A group consists of
    a sequence of blocks. Each block can be repeated one or more times, and can be set to execute in random order.

    This class contains two lists that are always the same size: a list of blocks, and a list of repeats each block has
    set. This class also is a MutableSequence, which means you can get and set both values at once with the operator[].
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.name = "Group"
        self.blocks = []
        self.repeats = []

        self.random_order = False

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
    
    def insert(self, index, value: Union[Block, tuple]):
        """Insert a new item into the group.
        Value can either be a single block or a tuple(block, repeats).
        """
        if isinstance(value, Block):
            value = (value, 1)
        
        self.blocks.insert(index, value[0])
        self.repeats.insert(index, value[1])

    # NFB Export =======================================================================================================
    def nfb_export_data(self) -> dict:
        """Export this group into a dict to be encoded as XML for NFBLab.
        Bool items are written as-is. The encoder is responsible for converting them into int format.
        """
        # Build sList and sNumberList ----------------------------------------------------------------------------------
        name_list = []
        repeat_list = []

        for item in self:
            name_list.append(item[0].name)
            repeat_list.append(item[1])

        # Export XML data ----------------------------------------------------------------------------------------------
        data = {}

        data["sName"] = self.name
        data["sList"] = " ".join(name_list)
        data["sNumberList"] = " ".join(str(number) for number in repeat_list)
        data["bShuffle"] = self.random_order

        return data
    
    def nfb_import_data(self, data: dict):
        """Import this group from a dict from NFBLab.
        Note that since self.blocks needs to contain references to other decoded objects, this function leaves the group
        in an invalid state. The caller method is responsible for converting self.blocks from a list of names to a list
        of actual blocks.
        """
        self.name = data["sName"]
        self.random_order = bool(int(data["bShuffle"]))

        if data["sList"] is not None:
            self.blocks = data["sList"].split(" ")
            self.repeats = [int(number) for number in data["sNumberList"].split(" ")]
