import os
from unittest import TestCase
from nfb_studio.serial import xml
from .example_class import ExampleClass

this_dir = os.path.dirname(__file__)


class TestXMLEncoder(TestCase):
    maxDiff = None

    def test_decoder(self):
        with open(this_dir+"/expected_results/xml_test.xml", "r") as f:
            source_data = f.read()

        decoder = xml.XMLDecoder()

        self.assertEqual(
            decoder.decode(source_data), 
            {"root": ExampleClass()}
        )

    def test_encoder_no_metadata(self):
        with open(this_dir+"/expected_results/xml_test_no_metadata.xml", "r") as f:
            expected_result = f.read()

        encoder = xml.XMLEncoder(separator="\n", indent="\t", metadata=False)

        obj = {"root": ExampleClass()}
        self.assertEqual(encoder.encode(obj), expected_result)
