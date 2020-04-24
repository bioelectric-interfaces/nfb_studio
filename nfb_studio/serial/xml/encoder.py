"""An object-aware JSON encoder."""
from typing import Union

import xmltodict as xd

from nfb_studio.util import expose_property

from ..base import BaseEncoder


class XMLEncoder:
    def __init__(self, *, encoding="utf-8", attr_prefix="@", cdata_key="#text", separator="", indent="", **kw):        
        self.base_encoder = BaseEncoder(**kw)
        
        self.encoding = encoding
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.separator = separator
        self.indent = indent

    def _convert_metadata(self, obj: dict):
        """Convert metadata from dict encoder to a format suitable for putting metadata as xml tags."""
        if "__class__" in obj:
            obj[self.attr_prefix + "__class__.__qualname__"] = obj["__class__"]["__qualname__"]
            obj[self.attr_prefix + "__class__.__module__"] = obj["__class__"]["__module__"]

            obj.pop("__class__")
        
        for key, value in obj.items():
            if isinstance(value, dict):
                self._convert_metadata(value)

    def encode(self, obj):
        data = self.base_encoder.encode(obj)
        if self.metadata:
            self._convert_metadata(data)
            
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
expose_property(XMLEncoder, "base_encoder", "in_place")
