"""A module responsible for serializing data into json.

Internally, all serialization algorithms are based on json. See top-level documentation for usage examples.

See Also
--------
encoder.JSONEncoder : An object-aware JSON encoder.
decoder.JSONDecoder : An object-aware JSON decoder.
"""
from json import load, loads, dump, dumps

from .encoder import JSONEncoder
from .decoder import JSONDecoder
