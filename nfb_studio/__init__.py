"""NFB experiment designer."""
from .serialize import ObjectEncoder, ObjectDecoder, serialize_qt, deserialize_qt

standard_encoder = ObjectEncoder(object_hooks=serialize_qt, indent='\t')
bytestr_encoder = ObjectEncoder(object_hooks=serialize_qt, ensure_ascii=True)
standard_decoder = ObjectDecoder(object_hooks=deserialize_qt)
