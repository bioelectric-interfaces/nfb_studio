from PySide2.QtCore import QPointF
from PySide2.QtWidgets import QGraphicsItem

from .unitconv import inches_to_pixels, pixels_to_inches

from .style import Style
from .palette import Palette

class SchemeItem(QGraphicsItem):
    """An item that supports measurements in inches."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._style = Style()
        self._palette = Palette()

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

    def setStyle(self, style: Style):
        self._style = style
        self.styleChange()
    
    def style(self) -> Style:
        return self._style
    
    def setPalette(self, palette: Palette):
        self._palette = palette
        self.paletteChange()
    
    def palette(self) -> Palette:
        return self._palette
    
    def styleChange(self):
        pass

    def paletteChange(self):
        pass

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value == True:
                self._palette.setCurrentColorGroup(Palette.Selected)
            if value == False:
                self._palette.setCurrentColorGroup(Palette.Active)
            self.paletteChange()

        return super().itemChange(change, value)