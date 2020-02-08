"""An object-aware JSON decoder."""
from json import JSONDecoder
from importlib import import_module
from inspect import isclass


class ObjectDecoder(JSONDecoder):
    """JSON decoder that provides tools to deserialize custom objects.

    You can add support for deserializing your class in two ways:

    - By adding a member function to your class: `def deserialize(self, data: dict)`;
    - By adding an external function `def serialize(obj, data: dict)` and passing it in a dict as the `object_hooks`
    parameter. (`object_hooks` is a dict that matches a class to a deserialization function.)

    When deserializing an object, this decoder first looks up the metadata field left by the ObjectEncoder. If that
    field exists, the decoder default-constructs an instance of a class that was encoded. It then checks if the
    class instance has a function in `object_hooks` or has a callable `deserialize()` attribute. If that is the case,
    the dict read from json is passed to that function to allow the class instance to load the contents into itself.
    Functions in the `object_hooks` parameter take precedence over member functions.

    ObjectDecoder does not accept an `object_hook` or `object_pairs_hook` parameter from JSONDecoder.

    .. note::
        If the metadata `__class__` field does not exist, the decoder leaves the dictionary as-is. If the field exists
        but was corrupted in some way, an exception will be raised.

    See Also
    --------
    nfb_studio.serialize.encoder.ObjectEncoder : An object-aware JSON encoder.
    """
    def __init__(self, *, object_hooks: dict = None, parse_float=None, parse_int=None, parse_constant=None,
                 strict=True):
        """"""
        self.object_hooks = object_hooks

        # Object hook used to handle custom deserialization
        def object_hook(data: dict):
            """An object hook for the ObjectDecoder.

            An internal function. This method is used as an object_hook to initialize ObjectDecoder. It looks for a meta
            field called `__class__` as a marker that the json field should be deserialized as an object. It attempts to
            default-construct an instance of the specified class and call either a method from the object_hooks dict or
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
            class_name = data["__class__"]["__name__"]

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

            # Default-construct an object of that class ----------------------------------------------------------------
            obj = cls()

            # Load the json data into the object -----------------------------------------------------------------------
            if cls in self.object_hooks:
                self.object_hooks[cls](obj, data)
                return obj
            elif hasattr(obj, "deserialize") and callable(obj.deserialize):
                obj.deserialize(data)
                return obj
            else:
                message = "an instance of {}.{} does not have a callable \"deserialize\" attribute" \
                    .format(module_path, class_name)
                raise AttributeError(message)

        super().__init__(object_hook=object_hook, parse_float=parse_float, parse_int=parse_int,
                         parse_constant=parse_constant, strict=strict)
