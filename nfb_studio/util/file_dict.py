from pathlib import Path


class FileDict(dict):
    """A dict of some items, whose keys are absolute filenames.

    When an item is requested, a `create_item` function is called with an path argument. The result of this function is
    written as the value to that key. If the item existed before, it is returned.
    """

    def __init__(self, create_item):
        """Constructs a `FileDict` with a `create_item` parameter - a function to call each time a new filename is 
        supplied.
        """
        super().__init__()
        self.create_item = create_item

    def __setitem__(self, key, value):
        """Override a written value with something else. Key is still converted to full path."""
        path = Path(key).resolve()

        super().__setitem__(path, value)

    def __getitem__(self, key):
        """Returns an item with some path.

        This item is automatically created by calling create_item() if it does not exist.
        """
        path = Path(key).resolve()

        if path not in self:
            super().__setitem__(path, self.create_item(str(path)))

        return super().__getitem__(path)

    def __contains__(self, key):
        """True if the dictionary has the specified key, else False."""
        path = Path(key).resolve()
        return super().__contains__(path)

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary, else `default`."""
        path = Path(key).resolve()
        return super().get(path)

    def pop(self, key, default=None):
        """Remove specified key and return the corresponding value.

        If key is not found, `default` is returned if given, otherwise `KeyError` is raised.
        """
        path = Path(key).resolve()
        return super().pop(path, default)

    def __delitem__(self, key):
        """Delete self[key]."""
        path = Path(key).resolve()
        super().__delitem__(path)
