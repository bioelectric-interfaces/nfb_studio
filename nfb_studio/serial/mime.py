"""Serialization support for mime data.

This module assumes that mime data is stored in an object of a Qt class QMimeData (or some other object with the same
interface). There are no encoders. Two functions - dump and load - accept an (optional) encoder from another module.
The string resulting from that encoding is then written as mime data.
Besides an instanse of QMimeData, functions also need a
["MIME type"](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) - a tag that indicates to the
recievers of this data what are the contents. A single instance of QMimeData can hold several objects with different
mime types.
"""
from typing import Union

from .json import JSONEncoder, JSONDecoder
from .hooks import Hooks

_cached_encoder = JSONEncoder(separators=(",", ":"), ensure_ascii=False)
_cached_decoder = JSONDecoder()

def dump(obj, mimedata, mimetype, *, encoder=None, hooks: Union[dict, tuple, Hooks] = None):
    """Encodes `obj`, and places it in `mimedata` with a type `mimetype`.  
    This function mimics the dump function from the json module. In this context, `mimedata` along with a `mimetype` tag
    is equivalent to a file to which you are writing.
    If no keyword arguments are specified, a default JSON encoder will be used to convert `obj` to text format. This
    encoder will print no extra spaces, and non-ASCII characters will be escaped. Specifying hooks will make the encoder
    use them during serialization, or you can provide a custom encoder with the `encoder` parameter.
    """
    if encoder is not None:
        pass
    elif hooks is not None:
        encoder = JSONEncoder(hooks=hooks, separators=(",", ":"), ensure_ascii=False)
    else:
        encoder = _cached_encoder
    
    data = encoder.encode(obj)
    bstr = data.encode("unicode-escape")

    mimedata.setData(mimetype, bstr)

def load(mimedata, mimetype, *, decoder=None, hooks: Union[dict, tuple, Hooks] = None):
    """Decodes an object with the specified `mimetype` from `mimedata`.  
    This function mimics the load function from the json module. In this context, `mimedata` along with a `mimetype` tag
    represent the file to which you are writing.
    If no keyword arguments are specified, a default JSON decoder will be used to convert `obj` to text format. This
    encoder assumes that the data is in ASCII with escaped unicode characters. Specifying hooks will make the decoder
    use them during deserialization, or you can provide a custom decoder with the `decoder` parameter.
    """
    if decoder is not None:
        pass
    elif hooks is not None:
        decoder = JSONDecoder(hooks=hooks)
    else:
        decoder = _cached_decoder
    
    if mimedata.hasFormat(mimetype):
        data = str(mimedata.data(mimetype), "unicode-escape")

        obj = decoder.decode(data)

        return obj
    return None
