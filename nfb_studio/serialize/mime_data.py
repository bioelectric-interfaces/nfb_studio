"""Object-aware implementation of QMimeData."""
from PySide2.QtCore import QMimeData, QByteArray

from nfb_studio.serialize.encoder import JSONEncoder
from nfb_studio.serialize.decoder import JSONDecoder


class MimeData(QMimeData):
    """A Mime data class that extends QMimeData by providing ways to serialize python objects."""

    def __init__(self, object_hooks=None):
        super().__init__()

        object_hooks = object_hooks or ({}, {})
        self._encoder = JSONEncoder(object_hooks=object_hooks[0], separators=(",", ":"), ensure_ascii=False)
        self._decoder = JSONDecoder(object_hooks=object_hooks[1])

    def hasObject(self, object_type) -> bool:
        mime_type = self._mime_type_of(object_type)
        return self.hasFormat(mime_type)

    def setObject(self, obj):
        object_type = obj.__class__
        mime_type = self._mime_type_of(object_type)
        data = self._encoder.encode(obj)
        bstr = data.encode("unicode-escape")

        self.setData(mime_type, QByteArray(bstr))

    def objectData(self, object_type):
        if self.hasObject(object_type):
            mime_type = self._mime_type_of(object_type)
            data = str(self.data(mime_type), "unicode-escape")

            obj = self._decoder.decode(data)

            return obj
        return None
    
    @staticmethod
    def _mime_type_of(object_type) -> str:
        return "application/x-pyobject+json;type=\"" + object_type.__module__ + "." + object_type.__name__ + "\""
