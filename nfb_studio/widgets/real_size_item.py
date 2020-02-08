from PySide2.QtCore import QPointF
from PySide2.QtWidgets import QGraphicsItem

from nfb_studio.gui import inches_to_pixels, pixels_to_inches


class RealSizeItem(QGraphicsItem):
    """An item that supports measurements in inches."""

    def __init__(self, parent=None):
        super(RealSizeItem, self).__init__(parent)

    def setPosition(self, *args, **kwargs):
        """Set node's position in inches.

        Does the same thing as setPos, except the arguments must be passed in inches.
        """
        point = QPointF(*args, **kwargs)

        self.setPos(inches_to_pixels(point))

    def position(self):
        """Returns node's position in inches.
        
        Does the same thing as setPos, except the return value is converted to inches.
        """
        return pixels_to_inches(self.pos())
