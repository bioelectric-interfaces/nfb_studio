from json import JSONEncoder


def compound_encoder(encoders):
    """Builds and returns an encoder class that tries to serialize objects with its components in sequence.
    For example: an encoder returned by compound_encoder([ObjectEncoder, CustomEncoder, ExtendedEncoder]) will attempt
    to serialize an object by calling the default() method of ObjectEncoder, then CustomEncoder, then ExtendedEncoder,
    and then JSONEncoder.
    """
    class CompoundEncoder(*encoders, JSONEncoder):
        """A JSON encoder that combines the serialization possibilities of several encoders.
        See Also
        --------
        compound_encoder : The function that produced this class.
        """
        pass

    return CompoundEncoder
