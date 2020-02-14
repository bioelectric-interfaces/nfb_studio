from typing import Union

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QGraphicsSimpleTextItem


class TextRectItem(QGraphicsSimpleTextItem):
    """A block of text.
    
    Text can be confined to a certain rectangular frame. Parts of text that do not fit will be cut off.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frame: Union[QRectF, None] = None
        self._alignment = Qt.AlignLeft

    def setFrame(self, frame: Union[QRectF, None]):
        """Set the frame to which the text must be confined.
        If frame is None, text will be displayed with no limitations.
        """
        self._frame = frame

    def setAlignment(self, flag):
        """Set alignment of the text inside the rectangle, such as Qt.AlignLeft."""
        self._alignment = flag

    def frame(self) -> Union[QRectF, None]:
        """Frame to which the text must be confined."""
        return self._frame

    def alignment(self):
        return self._alignment

    def paint(self, painter: QPainter, option, widget=...):
        if self.frame() is None:
            super().paint(painter, option, widget)
        else:
            painter.setFont(self.font())
            painter.setBrush(self.brush())
            painter.drawText(self.frame(), self.alignment(), self.text())
