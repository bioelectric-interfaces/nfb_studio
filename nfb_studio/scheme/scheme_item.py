"""A QGraphicsItem that has a style and a palette."""
from PySide2.QtWidgets import QGraphicsItem

from .style import Style
from .palette import Palette

class SchemeItem(QGraphicsItem):
    """A QGraphicsItem that has a style and a palette."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._style = Style()
        self._palette = Palette()

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
            if value:
                self._palette.setCurrentColorGroup(Palette.Selected)
            else:
                self._palette.setCurrentColorGroup(Palette.Active)
            self.paletteChange()

        return super().itemChange(change, value)
