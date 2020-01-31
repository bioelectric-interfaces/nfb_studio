from json import JSONDecoder
from importlib import import_module
from inspect import isclass

from .encoder import ObjectEncoder


def object_decoder_hook(data: dict):
    """An object hook for the ObjectDecoder.
    This method is used as an object_hook to initialize ObjectDecoder. It looks for a special value in the "_metadata"
    field as a marker that the json field should be deserialized as an object. It attempts to default-construct the
    specified class and call its deserialize(data: dict) method to load the json contents into it.

    Raises
    ------
    ImportError
        If no class specified by the encoder exists in the module specified by the encoder.
    TypeError
        If an attribute specified by the encoder exists in the specified module, but it's not a class;
        If the specified class exists but is not default-constructible;
        If the specified class was constructed but its deserialize method accepts something other than a single dict
        argument.
    AttributeError
        If the specified class was constructed, but it has no callable deserialize method.
    """
    if "_metadata" not in data or data["_metadata"]["encoder"] != ObjectEncoder.__name__:
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
        message = "ObjectDecoder: module \"{}\" does not define a \"{}\" class".format(module_path, class_name)
        raise ImportError(message)

    # Verify that cls is in fact a class
    if not isclass(cls):
        raise TypeError("ObjectDecoder: {}.{} is not a class".format(module_path, class_name))

    # Create an object of that class
    obj = cls()

    # Load the json data into the object
    if hasattr(obj, "deserialize") and callable(obj.deserialize):
        obj.deserialize(data)
        return obj
    else:
        message = "ObjectDecoder: an instance of {}.{} does not have a callable \"deserialize\" attribute" \
            .format(module_path, class_name)
        raise AttributeError(message)


class ObjectDecoder(JSONDecoder):
    def __init__(self, **kwargs):
        """JSON decoder that provides objects with a way to decode themselves.
        After deserializing a dict, this decoder checks if it has a "__class__" field. If so, it considers the dict a
        representation of a python object. It then attempts to create an instance of the specified class with no
        constructor arguments, and call that instance's deserialize method with the data dict.

        See Also
        --------
        ObjectEncoder : JSON Object Encoder
        object_decoder_hook : The function used to decode objects
        """
        # Object hook used to handle custom deserialization
        my_hook = object_decoder_hook

        # Check if user also has their own hook
        if "object_hook" in kwargs:
            # Yes: replace their hook with a combination of their hook and our hook
            user_hook = kwargs["object_hook"]

            def combined_hook(data):
                return user_hook(my_hook(data))

            kwargs["object_hook"] = combined_hook
        else:
            # No: add our hook as the object_hook
            kwargs["object_hook"] = my_hook

        super().__init__(**kwargs)
