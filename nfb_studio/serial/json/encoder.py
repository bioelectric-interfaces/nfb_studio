"""An object-aware JSON encoder."""
import json
from warnings import warn
from typing import Union

from ..hooks import Hooks


def _write_metadata(obj, data: dict) -> dict:
    """Write metadata that is required to reassemble the object, encoded by JSONEncoder.

    An internal function that adds the `__class__` metadata field to the serialized data.

    Returns
    -------
    data : dict
        The `data` parameter.
    """
    if "__class__" in data:
        warn(
            "during serialization of " +
            str(obj) +
            " a \"__class__\" field is being overwritten"
        )

    # Add meta information necessary to decode the object later
    data["__class__"] = {
        "__module__": obj.__class__.__module__,
        "__qualname__": obj.__class__.__qualname__
    }

    return data


class JSONEncoder(json.JSONEncoder):
    """JSON encoder that provides tools to serialize custom objects.

    You can add support for serializing your class in two ways:  
    - By adding a member function to your class: `def serialize(self) -> dict`;
    - By adding an external function `def serialize(obj) -> dict` and passing it in a dict as the `hooks`
      parameter. (`hooks` is a dict that matches a class to a serialization function.). This parameter also can accept a
      Hooks object or a tuple of two dicts: a serialization dict and a deserialization dict (the latter is ignored).

    When serializing an object, this encoder checks if that object's class has a function in `hooks` or has a
    callable serialize() attribute. If that is the case, the resulting dict from calling the function will be used in
    that object's place in json.
    Functions in the `hooks` parameter take precedence over member functions.

    .. warning::
        JSONEncoder adds a field to the dict, produced from the object, called `__class__`. This field is used in the
        JSONDecoder to create an instance of the class, where json data is then deserialized.
        Do not write anything in this field yourself - it will be overwritten.

    See Also
    --------
    nfb_studio.serialize.decoder.JSONDecoder : An object-aware JSON decoder.
    """

    def __init__(self, *,
                 hooks: Union[dict, tuple, Hooks] = None,
                 metadata=True,
                 skipkeys=False,
                 ensure_ascii=False,
                 check_circular=True,
                 allow_nan=True,
                 sort_keys=False,
                 indent=None,
                 separators=None,
                 **kw):
        """Constructs the JSONEncoder object.
        
        Mostly inherits JSONEncoder parameters from the standard json module, except for `default`, which is not
        inherited and is ignored.

        Parameters
        ----------
        hooks : dict, tuple, or Hooks object (default: None)
            A dict, mapping types to functions that can be used to serialize them in the format `def foo(obj) -> dict`,
            a tuple containing such dict as it's element 0, or a `hooks.Hooks` object;
        metadata : bool (default: True)
            If True, each custom object is serialized with an additional metadata field called `__class__`. This field
            is used in the JSONDecoder to create an instance of the class, where json data is then deserialized. If
            False, this field is skipped, but the decoder will not be able to deserialize custom objects.
        skipkeys : bool (default: False)
            If False, then it is a TypeError to attempt encoding of keys that are not str, int, float or None. If
            skipkeys is True, such items are simply skipped.
        ensure_ascii : bool (default: False)
            If True, the output is guaranteed to have all incoming non-ASCII characters escaped. If ensure_ascii is
            False, these characters will be output as-is.
        check_circular : bool (default: True)
            If check_circular is True, then lists, dicts, and custom encoded objects will be checked for circular
            references during encoding to prevent an infinite recursion (which would cause an OverflowError). Otherwise,
            no such check takes place.
        allow_nan : bool (default: True)
            If True, then NaN, Infinity, and -Infinity will be encoded as such. This behavior is not JSON specification
            compliant, but is consistent with most JavaScript based encoders and decoders. Otherwise, it will be a
            ValueError to encode such floats.
        sort_keys : bool (default: False)
            If True, then the output of dictionaries will be sorted by key; this is useful for regression tests to
            ensure that JSON serializations can be compared on a day-to-day basis.
        indent : int, str, or None (default: None)
            If indent is a non-negative integer or string, then JSON array elements and object members will be
            pretty-printed with that indent level. An indent level of 0, negative, or "" will only insert newlines. None
            (the default) selects the most compact representation. Using a positive integer indent indents that many
            spaces per level. If indent is a string (such as `"\t"`), that string is used to indent each level.
        separators : tuple (default: None)
            If specified, separators should be an (item_separator, key_separator) tuple. The default is (', ', ': ') if
            indent is None and (',', ': ') otherwise. To get the most compact JSON representation, you should specify
            (',', ':') to eliminate whitespace.
        """
        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators
        )
        
        if isinstance(hooks, dict):
            self.hooks = hooks
        elif isinstance(hooks, tuple):  # hooks.Hooks is also a tuple
            self.hooks = hooks[0]  # Only serialization functions
        else:
            self.hooks = {}
        
        self.metadata = metadata

    def default(self, o):
        """Implementation of `JSONEncoder`'s `default` method that enables the serialization logic."""
        if type(o) in self.hooks:
            data = self.hooks[type(o)](o)
            if self.metadata:
                _write_metadata(o, data)
            return data

        if hasattr(o, "serialize") and callable(o.serialize):
            data = o.serialize()
            if self.metadata:
                _write_metadata(o, data)
            return data

        return super().default(o)
