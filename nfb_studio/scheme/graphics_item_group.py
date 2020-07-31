"""A simple collection of QGraphicsItems."""
from collections.abc import MutableSet

from PySide2.QtCore import QRectF, QPointF
from PySide2.QtWidgets import QGraphicsItem


class GraphicsItemGroup(MutableSet):
    """A simple collection of QGraphicsItems.  
    Unlike a similarly named QGraphicsItemGroup from Qt, this class in not a QGraphicsItem. It has no position in the
    graphics scene, and items that it contains do not change their parent. This class is a convenient way of
    manipulating groups of items without disrupting the scene ownership tree.
    """
    def __init__(self):
        super().__init__()

        self._data = set()
    
    # Implementations of abstract methods ==============================================================================
    def __contains__(self, item):
        return self._data.__contains__(item)
    
    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return self._data.__len__()
    
    def add(self, item):
        if not isinstance(item, QGraphicsItem):
            raise TypeError("item has type " + type(item) + ", not QGraphicsItem")
        self._data.add(item)
    
    def discard(self, item):
        self._data.discard(item)

    # Geometry and position ============================================================================================
    def boundingRect(self):
        result = QRectF()

        for item in self:
            result |= item.boundingRect()
        
        return result

    def translate(self, *args):
        offset = QPointF(*args)

        for item in self:
            item.moveBy(offset.x(), offset.y())
    
    def moveTo(self, *args):
        self.moveTopLeft(*args)
    
    def moveTopLeft(self, *args):
        position = QPointF(*args)
        self.translate(position - self.boundingRect().topLeft())
    
    def moveTopRight(self, *args):
        position = QPointF(*args)
        self.translate(position - self.boundingRect().topRight())
    
    def moveBottomLeft(self, *args):
        position = QPointF(*args)
        self.translate(position - self.boundingRect().bottomLeft())
    
    def moveBottomRight(self, *args):
        position = QPointF(*args)
        self.translate(position - self.boundingRect().bottomRight())

    def moveCenter(self, *args):
        position = QPointF(*args)
        self.translate(position - self.boundingRect().center())
