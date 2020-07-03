"""Backend class managing decoding raw dicts of objects to proper dicts of objects."""
from typing import Union
from importlib import import_module
from inspect import isclass
from functools import reduce

from ..hooks import Hooks


def deepgetattr(obj, attr):
    """Recurses through an attribute chain to get the ultimate value."""
    return reduce(getattr, attr.split('.'), obj)


class BaseDecoder:
    """Backend class managing decoding raw dicts of objects to proper dicts of objects."""

    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None):
        self.hooks = hooks

    def decode(self, data):
        if isinstance(data, dict):
            return self.decode_dict(data)
        if isinstance(data, list):
            return self.decode_list(data)

        return data       
    
    def decode_list(self, data):
        result = []
        for item in data:
            result.append(self.decode(item))
        return result
    
    def decode_dict(self, data):
        """Decode a dict object.
        If dict has metadata, this function will call decode_custom after decoding the internal values.
        """
        result = {}
        for key, value in data.items():
            result[key] = self.decode(value)
        
        if "__class__" in result:
            # Decode custom object
            result = self.decode_custom(result)
        
        return result

    def decode_custom(self, data):
        # The following code is adapted from django.utils.module_loading module.
        module_path = data["__class__"]["__module__"]
        class_name = data["__class__"]["__qualname__"]

        module = import_module(module_path)

        # Get the class that needs to be instantiated
        try:
            cls = deepgetattr(module, class_name)
        except AttributeError:
            message = "module \"{}\" does not define a \"{}\" class".format(module_path, class_name)
            raise ImportError(message)

        # Verify that cls is in fact a class
        if not isclass(cls):
            raise TypeError("{}.{} is not a class".format(module_path, class_name))

        # Load the json data into the object
        if cls in self.hooks:
            return self.hooks[cls](data)
        if hasattr(cls, "deserialize") and callable(cls.deserialize):
            return cls.deserialize(data)
        
        message = "{}.{} does not have a callable \"deserialize\" attribute" \
            .format(module_path, class_name)
        raise AttributeError(message)

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
