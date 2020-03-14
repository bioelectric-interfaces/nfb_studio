"""A collection of object_hooks for serializing and deserializing some common Qt objects."""
from PySide2.QtCore import QPointF, QSizeF
import nfb_studio.serial.hooks as hk

# Serialize ============================================================================================================
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


# Deserialize ==========================================================================================================
def deserialize_QPointF(obj: QPointF, data: dict):
    obj.setX(data["x"])
    obj.setY(data["y"])

def deserialize_QSizeF(obj: QSizeF, data: dict):
    obj.setWidth(data["width"])
    obj.setHeight(data["height"])


# Hooks ================================================================================================================
qt = hk.Hooks(
    {
        QPointF: serialize_QPointF,
        QSizeF: serialize_QSizeF
    },
    {
        QPointF: deserialize_QPointF,
        QSizeF: deserialize_QSizeF
    }
)
"""Serialization hooks for the most common Qt classes."""
