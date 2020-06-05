from unittest import TestCase
from copy import deepcopy

from nfb_studio.serial import base

from .example_class import ExampleClass


class TestBaseEncoder(TestCase):
    expected_result = {
        "__class__": {
            "__module__": "tests.serial.example_class",
            "__qualname__": "ExampleClass"
        },
        "nested": {
            "__class__": {
                "__module__": "tests.serial.example_class",
                "__qualname__": "ExampleClass.Nested"
            },
            "int_var": -5,
            "float_var": 0.69,
            "string_var": "string",
            "list_var": [1, 2, 3],
            "tuple_var": [1, 2, 3],
            "dict_var": {1: 1, 2: 2, 3: 3},
            "set_var": [1, 2, 3],
            "bool_var1": True,
            "bool_var2": False,
            "none_var": None
        },
        "list_var": [
            None,
            {
                "__class__": {
                    "__module__": "tests.serial.example_class",
                    "__qualname__": "ExampleClass.Nested"
                },
                "int_var": -5,
                "float_var": 0.69,
                "string_var": "string",
                "list_var": [1, 2, 3],
                "tuple_var": [1, 2, 3],
                "dict_var": {1: 1, 2: 2, 3: 3},
                "set_var": [1, 2, 3],
                "bool_var1": True,
                "bool_var2": False,
                "none_var": None
            },
        ],
        "dict_var": {
            "nested": {
                "__class__": {
                    "__module__": "tests.serial.example_class",
                    "__qualname__": "ExampleClass.Nested"
                },
                "int_var": -5,
                "float_var": 0.69,
                "string_var": "string",
                "list_var": [1, 2, 3],
                "tuple_var": [1, 2, 3],
                "dict_var": {1: 1, 2: 2, 3: 3},
                "set_var": [1, 2, 3],
                "bool_var1": True,
                "bool_var2": False,
                "none_var": None
            },
        }
    }

    maxDiff = None

    def test_encoder(self):
        encoder = base.BaseEncoder()

        obj = ExampleClass()
        self.assertEqual(encoder.encode(obj), self.expected_result)

    def test_encoder_no_metadata(self):
        encoder = base.BaseEncoder(metadata=False)

        # Remove metadata from expected result
        expected_result = deepcopy(self.expected_result)
        expected_result.pop("__class__")
        expected_result["nested"].pop("__class__")
        expected_result["dict_var"]["nested"].pop("__class__")
        expected_result["list_var"][1].pop("__class__")

        obj = ExampleClass()
        self.assertEqual(encoder.encode(obj), expected_result)
    
    def test_encoder_hooks(self):
        def hook(obj):
            result = obj.serialize()
            result["extra"] = None
            return result
        
        encoder = base.BaseEncoder(hooks={ExampleClass.Nested: hook})

        # Add the "extra" field to expected result
        expected_result = deepcopy(self.expected_result)
        expected_result["nested"]["extra"] = None
        expected_result["dict_var"]["nested"]["extra"] = None
        expected_result["list_var"][1]["extra"] = None

        obj = ExampleClass()
        self.assertEqual(encoder.encode(obj), expected_result)
