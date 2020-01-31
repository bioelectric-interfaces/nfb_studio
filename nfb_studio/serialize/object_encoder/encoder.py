from json import JSONEncoder
from warnings import warn


class ObjectEncoder(JSONEncoder):
    """JSON encoder that provides objects with a way to encode themselves.
    When serializing an object, this encoder checks if that object has a callable serialize() attribute.
    If that is the case, the resulting dict from calling this attribute will be used as a substitute in json.

    Warnings
    --------
    ObjectEncoder adds a field to the dict, produced by the object, called "_metadata". This field is used in the
    ObjectDecoder to create an instance of the class, where json data is then deserialized.
    Do not write anything in this field yourself - it will be overwritten.

    See Also
    --------
    ObjectDecoder : JSON Object Decoder
    """

    def default(self, obj):
        if hasattr(obj, "serialize") and callable(obj.serialize):
            data = obj.serialize()

            if "_metadata" in data:
                warn(
                    "ObjectEncoder: during serialization of " +
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


