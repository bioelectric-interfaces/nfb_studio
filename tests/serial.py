from unittest import TestCase
from copy import deepcopy

from nfb_studio.serial import base, xml

class ExampleClass1:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3
    
    def serialize(self):
        return {
            "a": self.a,
            "b": self.b,
            "c": self.c
        }
    
    def deserialize(self, data):
        self.a = data["a"]
        self.b = data["b"]
        self.c = data["c"]

class ExampleClass2:
    def __init__(self):
        self.cls1 = ExampleClass1()
        self.x = "foo"
        self.y = 0.69

    def serialize(self):
        return {
            "cls1": self.cls1,
            "arr": [self.cls1],
            "x": self.x,
            "y": self.y
        }
    
    def deserialize(self, data):
        self.cls1 = data["cls1"]
        self.x = data["x"]
        self.y = data["y"]


class SerialBaseTest(TestCase):
    expected_result = {
        "__class__": {
            "__module__": "tests.serial",
            "__qualname__": "ExampleClass2"
        },
        "x": "foo",
        "y": 0.69,
        "cls1": {
            "__class__": {
                "__module__": "tests.serial",
                "__qualname__": "ExampleClass1"
            },
            "a": 1,
            "b": 2,
            "c": 3
        },
        "arr": [
            {
                "__class__": {
                    "__module__": "tests.serial",
                    "__qualname__": "ExampleClass1"
                },
                "a": 1,
                "b": 2,
                "c": 3
            },
        ]
    }

    maxDiff = None

    def test_encoder(self):
        encoder = base.BaseEncoder()

        obj = ExampleClass2()
        self.assertEqual(encoder.encode(obj), self.expected_result)

    def test_encoder_no_metadata(self):
        encoder = base.BaseEncoder(metadata=False)

        # Remove metadata from expected result
        expected_result = deepcopy(self.expected_result)
        expected_result.pop("__class__")
        expected_result["cls1"].pop("__class__")
        expected_result["arr"][0].pop("__class__")

        obj = ExampleClass2()
        self.assertEqual(encoder.encode(obj), expected_result)
    
    def test_encoder_hooks(self):
        def hook(obj):
            result = obj.serialize()
            result["extra"] = None
            return result
        
        encoder = base.BaseEncoder(hooks={ExampleClass1: hook})

        # Add the "extra" field to expected result
        expected_result = deepcopy(self.expected_result)
        expected_result["cls1"]["extra"] = None
        expected_result["arr"][0]["extra"] = None

        obj = ExampleClass2()
        self.assertEqual(encoder.encode(obj), expected_result)


class SerialXMLTest(TestCase):
    expected_result = '<?xml version="1.0" encoding="utf-8"?>\n<root __class__.__qualname__="ExampleClass2" __class__.__module__="tests.serial"><cls1 __class__.__qualname__="ExampleClass1" __class__.__module__="tests.serial"><a>1</a><b>2</b><c>3</c></cls1><arr><a>1</a><b>2</b><c>3</c><__class__><__module__>tests.serial</__module__><__qualname__>ExampleClass1</__qualname__></__class__></arr><x>foo</x><y>0.69</y></root>'

    maxDiff = None

    def test_encoder(self):
        encoder = xml.XMLEncoder()

        obj = {"root": ExampleClass2()}
        self.assertEqual(encoder.encode(obj), self.expected_result)
