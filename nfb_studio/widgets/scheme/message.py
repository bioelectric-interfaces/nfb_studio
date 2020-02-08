import os

from PySide2.QtCore import QRectF
from PySide2.QtGui import QPainter, QFontMetricsF, QBrush, QColor
from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtSvg import QGraphicsSvgItem, QSvgRenderer

from nfb_studio.gui import FontF, inches_to_pixels as px, pixels_to_inches as inches
from nfb_studio.widgets import RealSizeItem, TextLineItem
from nfb_studio.util import FileDict

icons_dir = os.path.dirname(__file__)


class Message(RealSizeItem):
    icon_size = 0.16
    """Size of the icon (width and height). The icon is expected to be square."""
    max_text_length = 2.5
    icon_text_margin = 0.05

    text_font_name = "Segoe UI"
    text_font_size = 10.5

    svg_renderers = FileDict(create_item=QSvgRenderer)

    def __init__(self, text=None, icon_filename=None, parent=None):
        """A message that is displayed to the user.
        Messages can be of different severity. This base class is inherited by InfoMessage, WarningMessage and
        ErrorMessage.
        """
        super(Message, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemHasNoContents)

        # Message text -------------------------------------------------------------------------------------------------
        self._text_item = TextLineItem(text or "Message", self)
        self._text_item.setFont(FontF(self.text_font_name, self.text_font_size))
        metrics = QFontMetricsF(self._text_item.font())
        self._text_item.setMaximumWidth(self.max_text_length)

        # Position
        self._text_item.setPos(px(self.icon_size + self.icon_text_margin), 0)
        self._text_item.moveBy(0, metrics.capHeight() / 2)
        self._text_item.moveBy(0, px(self.icon_size) / 2)

        # Background color
        self._text_item.setBackgroundBrush(QBrush(QColor(255, 255, 255, 196)))

        # Message icon -------------------------------------------------------------------------------------------------
        self._icon_item = QGraphicsSvgItem(self)
        if icon_filename is not None:
            self.setIcon(icon_filename)

    @classmethod
    def severity(cls):
        """Message severity: how important is this message. Lower is more important."""
        return 0

    def setText(self, text):
        self._text_item.setText(text)

    def setIcon(self, icon_filename):
        """Set the icon from an SVG file."""
        renderer: QSvgRenderer = self.svg_renderers[icon_filename]
        self._icon_item.setSharedRenderer(renderer)

        scale = px(self.icon_size) / renderer.defaultSize().width()
        self._icon_item.setScale(scale)

    def text(self):
        return self._text_item.text()

    def boundingRect(self) -> QRectF:
        return QRectF()

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass

    def serialize(self) -> dict:
        return {
            "text": self.text()
        }

    def deserialize(self, data: dict):
        self.setText(data["text"])


class InfoMessage(Message):
    def __init__(self, text=None, parent=None):
        """An informational message that is displayed to the user.
        This message reports normal events. If these events are unexpected, they do not impact the user's work in a
        problematic way.
        """
        super(InfoMessage, self).__init__(
            text=text or "Info message",
            icon_filename=icons_dir+"/icons/info.svg",
            parent=parent
        )

    @classmethod
    def severity(cls):
        """Message severity: how important is this message. Lower is more important."""
        return 3


class WarningMessage(Message):
    def __init__(self, text=None, parent=None):
        """A warning message that is displayed to the user.
        This message reports a problem that does not pose a critical risk to the user's work.
        """
        super(WarningMessage, self).__init__(
            text=text or "Warning message",
            icon_filename=icons_dir+"/icons/warning.svg",
            parent=parent
        )

    @classmethod
    def severity(cls):
        """Message severity: how important is this message. Lower is more important."""
        return 2


class ErrorMessage(Message):
    def __init__(self, text=None, parent=None):
        """An error message that is displayed to the user.
        This message reports a serious problem that poses a critical risk to the user's work.
        """
        super(ErrorMessage, self).__init__(
            text=text or "Error message",
            icon_filename=icons_dir+"/icons/error.svg",
            parent=parent
        )

    @classmethod
    def severity(cls):
        """Message severity: how important is this message. Lower is more important."""
        return 1
