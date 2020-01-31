from json import JSONDecoder
from ..fsequence import fsequence


def compound_decoder_hook(object_hooks):
    """Builds and returns a JSONDecoder hook that tries to deserialize objects with its components in sequence.
    This function accepts a list of object hooks that are normally used to build a JSONDecoder, and creates a hook that
    automatically calls all these hooks in sequence to every deserialized dict.
    This is a complimentary function to compound_decoder. While compound_decoder produces a full-blown decoder, this
    function only makes a hook for other decoders to use.

    Warnings
    --------
    Unlike compound_encoder that accepts classes derived from JSONEncoder, this function accepts object hooks. You can
    find object hooks for JSON Decoders of this module with their similar name: ObjectDecoder has a hook named
    object_decoder_hook.

    See Also
    --------
    compound_decoder : A similar function that produces an object decoder.
    """
    return fsequence(object_hooks)


def compound_decoder(object_hooks):
    """Builds and returns a JSONDecoder that tries to deserialize objects with its components in sequence.
    This function accepts a list of object hooks that are normally used to build a JSONDecoder, and creates a class,
    derived from JSONDecoder, that automatically applies all these hooks in sequence to every deserialized dict.
    For example: an decoder returned by compound_decoder([object_decoder_hook, custom_hook, other_hook]) will, after
    object deserialization into a dict, call object_decoder_hook, then custom_hook, then other_hook.
    Returned value is a class, and a user can specify all normal arguments during construction, including an additional
    object_hook and object_pairs_hook.
    A complimentary function compound_decoder_hook exists, that produces an object hook instead of a full-blown decoder.

    Warnings
    --------
    Unlike compound_encoder that accepts classes derived from JSONEncoder, this function accepts object hooks. You can
    find object hooks for JSON Decoders of this module with their similar name: ObjectDecoder has a hook named
    object_decoder_hook.

    See Also
    --------
    compound_decoder_hook : A similar function that produces an object hook.
    """
    hook = compound_decoder_hook(object_hooks)

    class CompoundDecoder(JSONDecoder):
        def __init__(self, **kwargs):
            """A JSON decoder that combines the deserialization possibilities of several object hooks.
            See Also
            --------
            compound_decoder : The function that produced this class.
            """
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

    return CompoundDecoder

