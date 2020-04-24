from copy import deepcopy
from typing import Union
from importlib import import_module
from inspect import isclass

from ..hooks import Hooks


class BaseDecoder:
    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None, in_place=False, **kw):
        self.hooks = hooks
        self.in_place = in_place

    def decode(self, data):
        # If data is not a dict, it is not an encoded object and is returned as-is -------------------------------------
        if not isinstance(data, dict):
            if self.in_place:
                return data
            return deepcopy(data)
        
        if self.in_place:
            result = data
        else:
            result = {}

        # Regardless of whether data is an encoded object or a plain dict, recursively decode its items ----------------
        for key, value in data:
            result[key] = self.decode(value)
        
        # If data does not have __class__, it is not considered an encoded object and is returned ----------------------
        if "__class__" not in data:
            return data

        # This looks like an encoded python object. Create it and deserialize data into it. ----------------------------
        # The following code is adapted from django.utils.module_loading module.
        module_path = data["__class__"]["__module__"]
        class_name = data["__class__"]["__qualname__"]

        module = import_module(module_path)

        # Get the class that needs to be instantiated ------------------------------------------------------------------
        try:
            cls = getattr(module, class_name)
        except AttributeError:
            message = "module \"{}\" does not define a \"{}\" class".format(module_path, class_name)
            raise ImportError(message)

        # Verify that cls is in fact a class ---------------------------------------------------------------------------
        if not isclass(cls):
            raise TypeError("{}.{} is not a class".format(module_path, class_name))

        # Default-construct an object of that class --------------------------------------------------------------------
        obj = cls()

        # Load the json data into the object ---------------------------------------------------------------------------
        if cls in self.hooks:
            self.hooks[cls](obj, data)
            return obj
        elif hasattr(obj, "deserialize") and callable(obj.deserialize):
            obj.deserialize(data)
            return obj
        else:
            message = "an instance of {}.{} does not have a callable \"deserialize\" attribute" \
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
