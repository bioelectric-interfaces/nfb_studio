"""A module that implements nfb_studio's custom serialization engine.

This module adds classes and methods that can serialize objects to different data formats. Corresponding functions and
classes can be found in nested modules, such as `serial.json`.

- If a class you want serialized is in your control, you can define these two member functions:
```python
def serialize(self) -> dict:

@classmethod
def deserialize(cls, data: dict) -> '''instance''':
```
These functions return/accept a dictionary containing the data that is necessary to save and required to recreate the
object during deserialization.

- If a class is out of your control, such as a class from another module, you will need to create "hooks" - external 
functions and pass them to the encoder you are using.
```python
# Names here do not matter (these functions can even be lambdas).
def serialize(obj) -> dict:
def deserialize(data: dict) -> '''instance''':
```
Put these functions in a dict that maps a type to a serialization function, and pass that dict as an argument to an
encoder.
```python
from serial.json import JSONEncoder

# Create a hook dict and pass it to the constuctor
my_serialization_hooks = {Point: serialize_point, Line: serialize_line}
my_encoder = JSONEncoder(hooks=my_serialization_hooks)
```
For convenience, you can store both serialization and deserialization hooks in one tuple or a `hooks.Hooks` object,
and pass that around instead:
```python
my_hooks = Hooks(my_serialization_hooks, my_deserialization_hooks)  # a plain tuple works too
my_encoder = JSONEncoder(hooks=my_hooks)
```
This module supplies some commonly used hooks in the `serial.hooks` nested module. Hooks supplied manually take
precedence over member functions.

Example
-------
```python
from serial.json import JSONEncoder, JSONDecoder

# A class that can be modified in an invasive way.
class MyClass:
    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c

    def serialize(self) -> dict:
        return {
            "a": self.a
            "b": self.b
            "c": self.c
        }

    @classmethod
    def deserialize(cls, data: dict):
        return cls(data["a"], data["b"], data["c"])

# A class that cannot be modified in an invasive way.
from PySide2.QtCore import QRect
def qrect_serialize(obj: QRect) -> dict:
    return {
        "x": obj.x()
        "y": obj.y()
        "width" = obj.width()
        "height" = obj.height()
    }

def qrect_deserialize(data: dict):
    obj = QRect()
    obj.setX(data["x"])
    obj.setY(data["y"])
    obj.setWidth(data["width"])
    obj.setHeight(data["height"])

    return obj

encoder = JSONEncoder(hooks={QRect: qrect_serialize})
decoder = JSONDecoder(hooks={QRect: qrect_deserialize})
```
In this example, the encoder and decoder will be able to serialize both `MyClass` and `QRect`.

.. tip::
    The dictionaries returned by the serialization functions do not need to be primitive data structures containing only
    dicts, strings, lists, and numbers. The keys should be strings, but values can be instances of any class, as long as
    that class is serializeable.

.. warning::
    In order for the decoder to know which dicts should be deserialized as which class instances, the encoder adds a
    metadata field to the serialized dictionary called `__class__`. Therefore this dict key is reserved.
"""
from .hooks import Hooks
