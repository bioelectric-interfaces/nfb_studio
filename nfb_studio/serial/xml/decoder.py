"""An object-aware JSON encoder."""
from typing import Union

import xmltodict as xd

from ..hooks import Hooks
from ..base import BaseDecoder


class XMLDecoder:
    def __init__(self, **kw):
        self.base_decoder = BaseDecoder(**kw)

    def encode(self, data):
        data_dict = xd.parse(data)
        return self.base_decoder.decode(data_dict)
