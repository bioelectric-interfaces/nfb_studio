from typing import Union

from ..hooks import Hooks


class BaseEncoder:
    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None, metadata=True, unknown_objects="error"):
        self.hooks = hooks        
        self.metadata = metadata
        self.unknown_objects = unknown_objects

    def encode(self, obj, /):
        # Encode known objects
        if self.encode_function(obj) is not None:
            # If an object has an encode function, prioritize this encoding function above all
            return self.encode_custom(obj)
        if type(obj) in {int, float, str, bool, type(None)}:
            return obj
        if type(obj) in {list, tuple, set}:
            return self.encode_list_like(obj)
        if type(obj) == dict:
            return self.encode_dict_like(obj)
        
        # If the object could not be encoded, do as indicated in self.unknown_objects
        if self.unknown_objects == "as-is":
            return obj
        if self.unknown_objects == "error":
            raise TypeError("object of type \"{}\" cannot be encoded".format(type(obj).__qualname__))

    def encode_list_like(self, obj: Union[list, tuple, set]):
        result = []

        for item in obj:
            result.append(self.encode(item))
        
        return result
    
    def encode_dict_like(self, obj: dict):
        result = {}

        for key, value in obj.items():
            result[self.encode(key)] = self.encode(value)
        
        return result

    def encode_custom(self, obj):
        # Get encode function for this object
        func = self.encode_function(obj)
        assert func is not None
        
        result = func(obj)
        result = self.encode(result)
        
        if self.metadata and not isinstance(result, dict):
            # If custom function did not return a dict and metadata is enabled, raise ValueError because this metadata
            # has nowhere to be written
            raise ValueError(
                "serialized value of type \"{}\" is not a dict, metadata cannot be written".format(
                    type(obj).__qualname__
                )
            )

        # Write metadata about the object
        if self.metadata:
            self.write_metadata(obj, result)
        
        return result
    
    def encode_function(self, obj, /):
        """Find a custom encode function for obj, or return None if that function does not exist."""
        if type(obj) in self.hooks:
            return self.hooks[type(obj)]
        
        if hasattr(obj, "serialize") and callable(obj.serialize):
            return type(obj).serialize
        
        return None

    def write_metadata(self, obj, data: dict) -> dict:
        """Write metadata that is required to reassemble the object, encoded by BaseEncoder.

        An internal function that adds the `__class__` metadata field to the serialized data.

        Returns
        -------
        data : dict
            The `data` parameter.
        """
        if "__class__" in data:
            raise ValueError(
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

    @property
    def unknown_objects(self):
        return self._unknown_objects
    
    @unknown_objects.setter
    def unknown_objects(self, value: str):
        unknown_objects_values = {"as-is", "error"}
        if value not in unknown_objects_values:
            raise ValueError(
                "value \""
                + value
                + "\" of unknown_objects not one of "
                + str(unknown_objects_values)
            )
        
        self._unknown_objects = value
