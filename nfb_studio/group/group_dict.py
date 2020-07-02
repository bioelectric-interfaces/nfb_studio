"""Internally used dictionary for groups."""
from nfb_studio.item_dict import ItemDict
from .group import Group


class GroupDict(ItemDict):
    """Internally used dictionary for groups."""
    stored_cls = Group
