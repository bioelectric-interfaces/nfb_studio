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

    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None, skipkeys=False, ensure_ascii=False, 
                 check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, **kw):
        """Constructs the JSONEncoder object.
        
        Constructs the object from the following arguments:  
        - hooks - a dict, mapping types to functions that can be used to serialize them in the format
          `def foo(obj) -> dict`, a tuple containing such dict as it's element 0, or a `hooks.Hooks` object;
        - other arguments inherited from JSONEncoder, except for `default`, which is not inherited and is ignored.
        """
        super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                         allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators)
        
        if isinstance(hooks, dict):
            self.hooks = hooks
        elif isinstance(hooks, tuple):  # hooks.Hooks is also a tuple
            self.hooks = hooks[0]  # Only serialization functions
        else:
            self.hooks = {}

    def default(self, obj):
        """Implementation of `JSONEncoder`'s `default` method that enables the serialization logic."""
        if type(obj) in self.hooks:
            data = self.hooks[type(obj)](obj)
            _write_metadata(obj, data)
            return data

        elif hasattr(obj, "serialize") and callable(obj.serialize):
            data = obj.serialize()
            _write_metadata(obj, data)
            return data

        else:
            return super().default(obj)
