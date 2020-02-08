"""A collection of object_hooks for serializing and deserializing some common Qt objects."""
from PySide2.QtCore import QPointF, QSizeF


def serialize_QPointF(obj: QPointF) -> dict:
    return {
        "x": obj.x(),
        "y": obj.y()
    }


def serialize_QSizeF(obj: QSizeF) -> dict:
    return {
        "width": obj.width(),
        "height": obj.height()
    }


def deserialize_QPointF(obj: QPointF, data: dict):
    obj.setX(data["x"])
    obj.setY(data["y"])


def deserialize_QSizeF(obj: QSizeF, data: dict):
    obj.setWidth(data["width"])
    obj.setHeight(data["height"])


serialize_qt = {
    QPointF: serialize_QPointF,
    QSizeF: serialize_QSizeF
}
"""An `object_hooks` Qt dict for the `nfb_studio.serialize.encoder.ObjectEncoder`."""

deserialize_qt = {
    QPointF: deserialize_QPointF,
    QSizeF: deserialize_QSizeF
}
"""An `object_hooks` Qt dict for the `nfb_studio.serialize.decoder.ObjectDecoder`."""
