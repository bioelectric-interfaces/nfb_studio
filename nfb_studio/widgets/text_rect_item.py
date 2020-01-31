from typing import Union

from Qt.QtCore import Qt, QRectF
from Qt.QtGui import QPainter
from Qt.QtWidgets import QGraphicsSimpleTextItem

from nfb_studio.gui import inches_to_pixels as px

from .real_size_item import RealSizeItem


class TextRectItem(QGraphicsSimpleTextItem, RealSizeItem):
    def __init__(self, *args, **kwargs):
        """A text item that is confined to a certain rectangular frame.
        Parts of text that do not fit will be cut off.
        """
        super(TextRectItem, self).__init__(*args, **kwargs)

        self._frame: Union[QRectF, None] = None
        self._alignment = Qt.AlignLeft

    def setFrame(self, frame: Union[QRectF, None]) -> None:
        """Set the frame to which the text must be confined. Frame measurements are in inches.
        If frame is None, text will be displayed with no limitations.
        """
        self._frame = frame

    def setAlignment(self, flag):
        """Set alignment of the text inside the rectangle, such as Qt.AlignLeft."""
        self._alignment = flag

    def frame(self) -> Union[QRectF, None]:
        """Frame to which the text must be confined. Frame measurements are in inches."""
        return self._frame

    def alignment(self):
        return self._alignment

    def paint(self, painter: QPainter, option, widget=...) -> None:
        if self.frame() is None:
            super(TextRectItem, self).paint(painter, option, widget)
        else:
            painter.setFont(self.font())
            painter.setBrush(self.brush())
            painter.drawText(px(self.frame()), self.alignment(), self.text())
