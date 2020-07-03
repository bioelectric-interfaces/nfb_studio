"""An object-aware JSON decoder."""
import json
from importlib import import_module
from inspect import isclass
from typing import Union

from ..hooks import Hooks


class JSONDecoder(json.JSONDecoder):
    """JSON decoder that provides tools to deserialize custom objects.

    You can add support for deserializing your class in two ways:  
    - By adding a member function to your class: `def deserialize(self, data: dict)`;
    - By adding an external function `def deserialize(obj, data: dict)` and passing it in a dict as the `hooks`
      parameter. (`hooks` is a dict that matches a class to a deserialization function.) This parameter also can accept
      a Hooks object or a tuple of two dicts: a serialization dict and a deserialization dict (the latter is ignored).

    When deserializing an object, this decoder first looks up the metadata field left by the JSONEncoder. If that
    field exists, the decoder default-constructs an instance of a class that was encoded. It then checks if the class
    instance has a function in `hooks` or has a callable `deserialize()` attribute. If that is the case, the dict
    read from json is passed to that function to allow the class instance to load the contents into itself. Functions in
    the `hooks` parameter take precedence over member functions.

    JSONDecoder does not accept an `object_hook` or `object_pairs_hook` parameter from JSONDecoder.

    .. note::
        If the metadata `__class__` field does not exist, the decoder leaves the dictionary as-is. If the field exists
        but was corrupted in some way, an exception will be raised.

    See Also
    --------
    nfb_studio.serialize.encoder.JSONEncoder : An object-aware JSON encoder.
    """
    def __init__(self, *, hooks: Union[dict, tuple, Hooks] = None, parse_float=None, parse_int=None,
                 parse_constant=None, strict=True, **kw):
        """Constructs the JSONDecoder object.
        
        Mostly inherits JSONDecoder parameters from the standard json module, except for `object_hook` and
        `object_pairs_hook`, which are not inherited and are ignored.

        Parameters
        ----------
        hooks : dict, tuple, or Hooks object (default: None)
            A dict, mapping types to functions that can be used to deserialize them in the format
            `def foo(obj, data: dict)`, a tuple containing such dict as its element 1, or a `hooks.Hooks` object;
        parse_float : callable (default: None)
            If specified, will be called with the string of every JSON float to be decoded. By default, this is
            equivalent to float(num_str). This can be used to use another datatype or parser for JSON floats
            (e.g. decimal.Decimal).
        parse_int : callable (default: None)
            If specified, will be called with the string of every JSON int to be decoded. By default, this is equivalent
            to int(num_str). This can be used to use another datatype or parser for JSON integers (e.g. float).
        parse_constant : callable (default: None)
            If specified, will be called with one of the following strings: '-Infinity', 'Infinity', 'NaN'. This can be
            used to raise an exception if invalid JSON numbers are encountered.
        strict : bool (default: True)
            If False, then control characters will be allowed inside strings. Control characters in this context are
            those with character codes in the 0–31 range, including '\t' (tab), '\n', '\r' and '\0'.
        """
        if isinstance(hooks, dict):
            self.hooks = hooks
        elif isinstance(hooks, tuple):  # hooks.Hooks is also a tuple
            self.hooks = hooks[1]  # Only deserialization functions
        else:
            self.hooks = {}

        # Object hook used to handle custom deserialization
        def object_hook(data: dict):
            """An object hook for the JSONDecoder.

            An internal function. This method is used as an object_hook to initialize JSONDecoder. It looks for a meta
            field called `__class__` as a marker that the json field should be deserialized as an object. It attempts to
            default-construct an instance of the specified class and call either a method from the hooks dict or
            instance's own `deserialize(data: dict)` method to load the json contents into it.

            Raises
            ------
            ImportError
                If no class specified by the encoder exists in the module specified by the encoder.
            TypeError
                If an attribute specified by the encoder exists in the specified module, but it's not a class;
                If the specified class exists but is not default-constructible;
                If the specified class was constructed but its deserialize method accepts something other than a single
                dict argument.
            AttributeError
                If the specified class was constructed, but it has no callable deserialize method.
            """
            if "__class__" not in data:
                return data

            # This looks like json notation of a python object. Create it and deserialize json into it.
            # The following code is adapted from django.utils.module_loading module.
            module_path = data["__class__"]["__module__"]
            class_name = data["__class__"]["__qualname__"]

            module = import_module(module_path)

            # Get the class that needs to be instantiated --------------------------------------------------------------
            try:
                cls = getattr(module, class_name)
            except AttributeError:
                message = "module \"{}\" does not define a \"{}\" class".format(module_path, class_name)
                raise ImportError(message)

            # Verify that cls is in fact a class -----------------------------------------------------------------------
            if not isclass(cls):
                raise TypeError("{}.{} is not a class".format(module_path, class_name))

            # Load the json data into the object -----------------------------------------------------------------------
            if cls in self.hooks:
                return self.hooks[cls](data)
            if hasattr(cls, "deserialize") and callable(cls.deserialize):
                return cls.deserialize(data)
            
            message = "an instance of {}.{} does not have a callable \"deserialize\" attribute" \
                .format(module_path, class_name)
            raise AttributeError(message)

        super().__init__(
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            strict=strict
        )
