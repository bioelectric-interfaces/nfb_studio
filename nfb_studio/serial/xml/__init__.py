"""Serialization support for xml data."""
from typing import Union

import xmltodict as xd

from ..hooks import Hooks
from .encoder import XMLEncoder
from .decoder import XMLDecoder

_cached_encoder = XMLEncoder()
_cached_decoder = XMLDecoder()

def dumps(obj, *, encoder=None, hooks: Union[dict, tuple, Hooks] = None):
    if encoder is not None:
        pass
    elif hooks is not None:
        encoder = XMLEncoder(hooks=hooks)
    else:
        encoder = _cached_encoder
    
    return encoder.encode(obj)

def loads(s, *, decoder=None, hooks: Union[dict, tuple, Hooks] = None):
    if decoder is not None:
        pass
    elif hooks is not None:
        decoder = XMLDecoder(hooks=hooks)
    else:
        decoder = _cached_decoder
    
    return decoder.decode(s)
