"""An object-aware XML decoder."""
from typing import Union
import xmltodict as xd
from ..base import BaseDecoder


class XMLDecoder:
    def __init__(self, decode_attributes=True, force_list=None, **kw):
        self.base_decoder = BaseDecoder(**kw)

        self.decode_attributes = decode_attributes
        self.force_list = force_list

    def decode(self, data):
        data_dict = xd.parse(
            data, 
            xml_attribs=self.decode_attributes, 
            force_list=self.force_list
        )

        return self.base_decoder.decode(data_dict)
