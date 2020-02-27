"""Object-aware implementation of QMimeData."""
from typing import Union
from PySide2.QtCore import QMimeData, QByteArray

from nfb_studio.serialize.encoder import JSONEncoder
from nfb_studio.serialize.decoder import JSONDecoder


class MimeData:
    """A Mime data class that extends QMimeData by providing ways to serialize python objects."""

    def __init__(self, data: QMimeData = None, object_hooks=None):
        object_hooks = object_hooks or ({}, {})

        self.qmimedata = data or QMimeData()
        self._encoder = JSONEncoder(object_hooks=object_hooks[0], separators=(",", ":"), ensure_ascii=False)
        self._decoder = JSONDecoder(object_hooks=object_hooks[1])

    # Observer functions ===============================================================================================
    def hasFormat(self, mime_type, /):
        return self.qmimedata.hasFormat(mime_type)

    def hasObject(self, object_type) -> bool:
        mime_type = self._mime_type_of(object_type)
        return self.hasFormat(mime_type)

    # Set functions ====================================================================================================
    def setData(self, mime_type, binary_data: Union[bytes, bytearray, QByteArray]):
        self.qmimedata.setData(mime_type, QByteArray(binary_data))

    def setObject(self, obj):
        object_type = obj.__class__
        mime_type = self._mime_type_of(object_type)
        data = self._encoder.encode(obj)
        bstr = data.encode("unicode-escape")

        self.setData(mime_type, bstr)

    # Get functions ====================================================================================================
    def data(self, mime_type):
        return self.qmimedata.data(mime_type)

    def objectData(self, object_type):
        if self.hasObject(object_type):
            mime_type = self._mime_type_of(object_type)
            data = str(self.data(mime_type), "unicode-escape")

            obj = self._decoder.decode(data)

            return obj
        return None
    
    @staticmethod
    def _mime_type_of(object_type) -> str:
        return "application/x-pyobject+json;type=\"" + object_type.__module__ + "." + object_type.__qualname__ + "\""
