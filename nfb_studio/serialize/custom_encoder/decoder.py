from json import JSONDecoder
from importlib import import_module
from inspect import isclass

from .encoder import CustomEncoder


def generate_custom_decoder_hook(hooks: dict = None):
    """A metafunction that generates and returns the custom decoder hook for the CustomDecoder."""
    hooks = hooks or {}

    def custom_decoder_hook(data: dict):
        """An object hook for the CustomDecoder.
        This method is used as an object_hook to initialize CustomDecoder. It looks for a special value in the "_metadata"
        field as a marker that the json field should be deserialized as an object. It attempts to default-construct the
        specified class and call its deserialize(data: dict) method to load the json contents into it.

        Raises
        ------
        ImportError
            If no class specified by the encoder exists in the module specified by the encoder.
        TypeError
            If an attribute specified by the encoder exists in the specified module, but it's not a class;
            If the specified class exists but is not default-constructible;
            If the specified class was constructed but its deserialize method accepts something other than an instance
            and a dict.
        KeyError
            If the hooks do not contain a hook for the specified class.
        """
        if "_metadata" not in data or data["_metadata"]["encoder"] != CustomEncoder.__name__:
            return data

        # This looks like json notation of a python object. Create it and deserialize json into it.
        # The following code is adapted from django.utils.module_loading module.
        module_path = data["_metadata"]["__class__"]["__module__"]
        class_name = data["_metadata"]["__class__"]["__name__"]

        module = import_module(module_path)

        # Get the class that needs to be instantiated
        try:
            cls = getattr(module, class_name)
        except AttributeError:
            message = "CustomDecoder: module \"{}\" does not define a \"{}\" class".format(module_path, class_name)
            raise ImportError(message)

        # Verify that cls is in fact a class
        if not isclass(cls):
            raise TypeError("CustomDecoder: {}.{} is not a class".format(module_path, class_name))

        # Verify that a deserialization method exists
        if cls not in hooks:
            message = "CustomDecoder: an instance of {}.{} does not have deserialization hook" \
                .format(module_path, class_name)
            raise KeyError(message)

        # Create an object of that class
        obj = cls()

        return hooks[cls](obj, data)

    return custom_decoder_hook


class CustomDecoder(JSONDecoder):
    def __init__(self, hooks: dict = None, **kwargs):
        """JSON decoder that provides objects with a way to decode themselves.
        After deserializing a dict, this decoder checks if it has a `_metadata` field. If that field exists and it's
        `encoder` member equates to a special value it considers the dict decodable with this decoder. It then attempts
        to create an instance of the specified class with no constructor arguments, and call that instance's deserialize
        method with the data dict.

        See Also
        --------
        ObjectEncoder : JSON Object Encoder
        object_decoder_hook : The function used to decode objects
        """
        hook = generate_custom_decoder_hook(hooks)

        # Check if user also has their own hook
        if "object_hook" in kwargs:
            # Yes: replace their hook with a combination of their hook and our hook
            user_hook = kwargs["object_hook"]

            def combined_hook(data):
                return user_hook(hook(data))

            kwargs["object_hook"] = combined_hook
        else:
            # No: add our hook as the object_hook
            kwargs["object_hook"] = hook

        super().__init__(**kwargs)
