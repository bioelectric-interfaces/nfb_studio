from Qt.QtCore import QPointF, QSizeF


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

deserialize_qt = {
    QPointF: deserialize_QPointF,
    QSizeF: deserialize_QSizeF
}
