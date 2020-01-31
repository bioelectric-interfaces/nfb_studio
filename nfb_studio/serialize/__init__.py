"""A module that implements nfb_studio's custom serialization engine.
This module allows for classes to define their own representation in json format. Using this method, supported classes
can appear in the data structures that are dumped into json files and strings, and then loaded back without loss of
information.
To enable support for these functions, classes should define two methods:
```python
def serialize(self) -> dict:
def deserialize(self, data: dict):
```
These methods should convert the object to and from a dictionary, containing all the essential information about the
object. The keys should be strings, but values do not need to be primitive json-like structures, as long as they are
themselves serializable.
"""
from .object_encoder import *
from .compound_encoder import *
