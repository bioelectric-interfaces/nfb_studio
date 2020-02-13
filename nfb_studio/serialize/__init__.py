"""A module that implements nfb_studio's custom serialization engine.

This module extends the default JSON encoder and decoder with simpler ways to serialize objects.
- `encoder.JSONEncoder`: An encoder that inherits
  [`JSONEncoder`](https://docs.python.org/3/library/json.html#json.JSONEncoder) from python standard library;
- decoder.JSONDecoder : A decoder that inherits
  [`JSONDecoder`](https://docs.python.org/3/library/json.html#json.JSONDecoder) from python standard library.

These classes recognise the serialization interface of classes, as well as accept an `object_hooks` dictionary.
JSONEncoder needs a dictionary with serializing functions, JSONDecoder - with deserializing functions.

- If a class you want serialized is in your control, you can define these two member functions:
```python
def serialize(self) -> dict:
def deserialize(self, data: dict):
```
These functions return/accept a dictionary containing the data that is necessary to save and required to recreate the
object during deserialization.

- If a class is out of your control, such as a class from another module, both JSONEncoder and JSONDecoder accept an
  optional object_hooks parameter. This parameter is a dictionary that maps a class to a method that needs to be used to
  serialize that class. All you need to do is to create these two external methods:
```python
# Names here do not matter (these functions can even be lambdas).
def serialize(obj) -> dict:
def deserialize(obj, data: dict):
```
and put these methods into their dictionaries for the encoder and decoder.

Example
-------
```python
# A class that can be modified in an invasive way.
class MyClass:
    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c

    def serialize(self) -> dict:
        return {
            "a": a
            "b": b
            "c": c
        }

    def deserialize(self, data: dict):
        self.a = data["a"]
        self.b = data["b"]
        self.c = data["c"]

# A class that cannot be modified in an invasive way.
from PySide2.QtCore import QRect
def qrect_serialize(obj: QRect) -> dict:
    return {
        "x": obj.x()
        "y": obj.y()
        "width" = obj.width()
        "height" = obj.height()
    }

def qrect_deserialize(obj: QRect, data: dict):
    obj.setX(data["x"])
    obj.setY(data["y"])
    obj.setWidth(data["width"])
    obj.setHeight(data["height"])

encoder = JSONEncoder(object_hooks={QRect: qrect_serialize})
decoder = JSONDecoder(object_hooks={QRect: qrect_deserialize})
```
In this example, the encoder and decoder will be able to serialize both `MyClass` and `QRect`.

.. tip::
    The dictionaries returned by the serialization functions do not need to be primitive data structures containing only
    dicts, strings, lists, and numbers. The keys should be strings, but values can be instances of any class, as long as
    that class is serializeable.

.. warning::
    In order for the decoder to know which dicts should be deserialized as which class instances, the encoder adds a
    metadata field to the serialized dictionary called `__class__`. Do not write anything to that field - it will be
    overwritten.

See Also
--------
encoder.JSONEncoder : An object-aware JSON encoder.
decoder.JSONDecoder : An object-aware JSON decoder.
"""
from json import load, loads, dump, dumps

from .encoder import JSONEncoder
from .decoder import JSONDecoder

from .mime_data import MimeData

from .qt_hooks import serialize_qt, deserialize_qt
