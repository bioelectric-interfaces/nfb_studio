"""NFB experiment designer."""
from . import serialize

std_encoder = serialize.JSONEncoder(object_hooks=serialize.serialize_qt, indent='\t')
std_decoder = serialize.JSONDecoder(object_hooks=serialize.deserialize_qt)


class StdMimeData(serialize.MimeData):
    def __init__(self):
        super().__init__(object_hooks=(serialize.serialize_qt, serialize.deserialize_qt))
