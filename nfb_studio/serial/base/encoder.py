from typing import Union
from warnings import warn
from copy import deepcopy

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


class BaseEncoder:
    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None, metadata=True, in_place=False, **kw):
        self.hooks = hooks        
        self.metadata = metadata
        self.in_place = in_place
    
    def encode_function(self, obj, /):
        """Find a custom encode function for obj, or return None if that function does not exist."""
        if type(obj) in self.hooks:
            return self.hooks[type(obj)]
        
        if hasattr(obj, "serialize") and callable(obj.serialize):
            return type(obj).serialize
        
        return None

    def encode(self, obj, /):
        # Get encode function for this object
        func = self.encode_function(obj)

        if func is not None:
            # If the function exists, encode this object
            result = func(obj)

            # Encode resulting dict in-place (to encode nested custom objects)
            in_place_saved = self.in_place
            self.in_place = True
            self.encode(result)
            self.in_place = in_place_saved
            
            # Write metadata about the object
            if self.metadata:
                _write_metadata(obj, result)
            
            return result
        
        if isinstance(obj, dict):
            # If the object is not custom encodable, but is a dict, encode its elements
            if self.in_place:
                result = obj  # In-place encoder replaces custom objects with their encodings
            else:
                result = {}  # Non-in-place encoder creates a new dict
            
            for key, value in obj.items():
                # For each item, encode it
                encoded = self.encode(value)
                if encoded is value and not self.in_place:
                    # If item could not be encoded and not in place, deepcopy it
                    result[key] = deepcopy(value)
                else:
                    result[key] = encoded
        
            return result
        
        if isinstance(obj, list) or isinstance(obj, tuple):
            if self.in_place:
                result = obj  # In-place encoder replaces custom objects with their encodings
            else:
                result = [None] * len(obj)  # Non-in-place encoder creates a new list
            
            for i in range(len(obj)):
                # For each item, encode it
                value = obj[i]
                encoded = self.encode(value)
                if encoded is value and not self.in_place:
                    # If item could not be encoded and not in place, deepcopy it
                    result[i] = deepcopy(value)
                else:
                    result[i] = encoded
            
            return result

        return obj

    @property
    def hooks(self):
        return self._hooks
    
    @hooks.setter
    def hooks(self, value: Union[dict, tuple, Hooks] = None):
        if isinstance(value, dict):
            self._hooks = value
        elif isinstance(value, tuple):  # hooks.Hooks is also a tuple
            self._hooks = value[0]  # Only serialization functions
        else:
            self._hooks = {}
