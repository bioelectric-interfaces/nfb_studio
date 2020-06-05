from unittest import TestCase

from nfb_studio.serial import base

from .example_class import ExampleClass


class TestBaseDecoder(TestCase):
    source_data = {
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

    def test_decoder(self):
        decoder = base.BaseDecoder()

        expected_result = ExampleClass()
        self.assertEqual(decoder.decode(self.source_data), expected_result)
    
    def test_decoder_hooks(self):
        def hook(obj, data):
            obj.deserialize(data)
            obj.list_var.append('x')
        
        decoder = base.BaseDecoder(hooks={ExampleClass.Nested: hook})

        # Add the "extra" field to expected result
        expected_result = ExampleClass()
        expected_result.nested.list_var.append('x')

        self.assertEqual(decoder.decode(self.source_data), expected_result)
