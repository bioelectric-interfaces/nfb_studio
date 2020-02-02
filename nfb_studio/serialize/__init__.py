"""A module that implements nfb_studio's custom serialization engine.
This module extends the default JSON encoder and decoder with simpler ways to serialize objects.
- If a class you want serialized is in your control, you can define these two member functions:
```python
def serialize(self) -> dict:
def deserialize(self, data: dict):
```
These functions return/accept a dictionary containing the data that is necessary to save and required to recreate the
object during deserialization.
- If a class is out of your control, such as a class from another module, both ObjectEncoder and ObjectDecoder accept an
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

encoder = ObjectEncoder(object_hooks={QRect: qrect_serialize})
decoder = ObjectDecoder(object_hooks={QRect: qrect_deserialize})
```
In this example, the encoder and decoder will be able to serialize both MyClass and QRect.

Notes
-----
The dictionaries returned by the serialization functions do not need to be primitive data structures containing only
dicts, strings, lists, and numbers. The keys should be strings, but values can be instances of any class, as long as
that class is serializeable.

Warnings
--------
In order for the decoder to know which dicts should be deserialized as which class instances, the encoder adds a
metadata field to the serialized dictionary called `__class__`. Do not write anything to that field - it will be
overwritten.

See Also
--------
ObjectEncoder : An object-aware JSON encoder.
ObjectDecoder : An object-aware JSON decoder.
"""
from .encoder import ObjectEncoder
from .decoder import ObjectDecoder
