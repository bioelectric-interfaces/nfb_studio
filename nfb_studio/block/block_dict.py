"""Internally used dictionary for blocks."""
from nfb_studio.item_dict import ItemDict
from .block import Block


class BlockDict(ItemDict):
    """Internally used dictionary for blocks."""
    stored_cls = Block
