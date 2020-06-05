"""An object-aware JSON encoder."""
from typing import Union

import xmltodict as xd

from nfb_studio.util import expose_property

from ..base import BaseEncoder
from json import dumps


class XMLEncoder:
    def __init__(self, *, encoding="utf-8", attr_prefix="@", cdata_key="#text", separator="", indent="", **kw):
        kw["unknown_objects"] = "error"
        self.base_encoder = BaseEncoder(**kw)
        
        self.encoding = encoding
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.separator = separator
        self.indent = indent

    def _convert_metadata(self, obj):
        """Convert metadata from dict encoder to a format suitable for putting metadata as xml tags."""
        if isinstance(obj, dict):
            # Replace metadata if it exists
            if "__class__" in obj:
                obj[self.attr_prefix + "__class__.__qualname__"] = obj["__class__"]["__qualname__"]
                obj[self.attr_prefix + "__class__.__module__"] = obj["__class__"]["__module__"]

                obj.pop("__class__")
            
            # Recursively convert metadata of nested objects
            for value in obj.values():
                self._convert_metadata(value)
        elif isinstance(obj, list):
            for item in obj:
                self._convert_metadata(item)

    def _prepare_data(self, obj):
        """Prepare data for conversion by xmltodict. For example, replace all non-string keys with strings, otherwise
        xmltodict dies if in a list there is a dict with non-string keys.
        """
        if isinstance(obj, dict):
            keys = list(obj.keys())

            for key in keys:
                self._prepare_data(obj[key])

                if not isinstance(key, str):
                    obj[str(key)] = obj[key]
                    obj.pop(key)
        elif isinstance(obj, list):
            for item in obj:
                self._prepare_data(item)

    def encode(self, obj):
        data = self.base_encoder.encode(obj)

        if self.metadata:
            self._convert_metadata(data)
        
        self._prepare_data(data)

        data_xml = xd.unparse(
            data, 
            encoding=self.encoding, 
            attr_prefix=self.attr_prefix, 
            cdata_key=self.cdata_key,
            pretty=True,
            newl=self.separator,
            indent=self.indent
        )

        return data_xml

expose_property(XMLEncoder, "base_encoder", "hooks")
expose_property(XMLEncoder, "base_encoder", "metadata")
