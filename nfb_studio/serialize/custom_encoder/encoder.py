from json import JSONEncoder
from warnings import warn


class CustomEncoder(JSONEncoder):
    """JSON encoder that provides the user with a way to extend the set of objects that can be serialized.
    On construction, this encoder accepts an additional keyword argument: a dict called "hooks". This dictionary maps
    a type to a callable that can be used to serialize that type. This callable should accept a single argument - an
    instance of a type in question - and return a dict containing all the information this type wants to export.

    Warnings
    --------
    CustomEncoder adds a field to the dict, produced by the hook function, called "_metadata". This field is used in the
    CustomDecoder to create an instance of the class, where json data is then deserialized.
    Do not write anything in this field yourself - it will be overwritten.

    See Also
    --------
    CustomDecoder : JSON Custom Decoder
    """
    def __init__(self, hooks: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.hooks = hooks or {}

    def default(self, obj):
        if type(obj) in self.hooks:
            data = obj.serialize()

            if "_metadata" in data:
                warn(
                    "CustomEncoder: during serialization of " +
                    str(obj) +
                    " an \"_metadata\" field is being overwritten"
                )

            # Add meta information necessary to decode the object later
            data["_metadata"] = {
                "encoder": self.__class__.__name__,
                "__class__": {
                    "__module__": obj.__class__.__module__,
                    "__name__": obj.__class__.__name__
                }
            }

            return data
        else:
            return super().default(obj)


