import os

from PySide2.QtCore import QRectF
from PySide2.QtGui import QPainter, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtSvg import QGraphicsSvgItem, QSvgRenderer

from nfb_studio.widgets import TextLineItem
from nfb_studio.util import FileDict

from .style import Style
from .scheme_item import SchemeItem

this_dir = os.path.dirname(__file__)


class Message(SchemeItem):
    """A message that is displayed to the user.
    
    Messages can be of different severity. This base class is inherited by InfoMessage, WarningMessage and
    ErrorMessage.
    """
    svg_renderers = FileDict(create_item=QSvgRenderer)

    def __init__(self, text=None, icon_filename=None, parent=None):
        super(Message, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemHasNoContents)

        # Message text -------------------------------------------------------------------------------------------------
        self._text_item = TextLineItem(text or "Message", self)

        # Message icon -------------------------------------------------------------------------------------------------
        self._icon_item = QGraphicsSvgItem(self)
        if icon_filename is not None:
            self.setIcon(icon_filename)

        self.styleChange()
        self.paletteChange()

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

        icon_size = self.style().pixelMetric(Style.MessageIconSize)

        scale = icon_size / renderer.defaultSize().width()
        self._icon_item.setScale(scale)

    def text(self):
        return self._text_item.text()

    def styleChange(self):
        super().styleChange()
        style = self.style()

        # Text item ----------------------------------------------------------------------------------------------------
        self._text_item.setFont(style.font(Style.MessageTextFont))
        self._text_item.setMaximumWidth(style.pixelMetric(Style.MessageTextLength))

        # Position
        text_metrics = QFontMetricsF(self._text_item.font())
        icon_size = style.pixelMetric(Style.MessageIconSize)
        margin = style.pixelMetric(Style.MessageIconTextMargin)

        self._text_item.setPos(icon_size + margin, 0)
        self._text_item.moveBy(0, text_metrics.capHeight() / 2)
        self._text_item.moveBy(0, icon_size / 2)

        # Icon item ----------------------------------------------------------------------------------------------------
        icon_renderer = self._icon_item.renderer()
        if icon_renderer is None:  # No icon set
            scale = 1
        else:
            scale = icon_size / icon_renderer.defaultSize().width()

        self._icon_item.setScale(scale)
    
    def paletteChange(self):
        super().paletteChange()
        text_bg = self.palette().background().color()
        text_bg.setAlpha(196)

        self._text_item.setBrush(self.palette().text())
        self._text_item.setBackgroundBrush(text_bg)

    def boundingRect(self) -> QRectF:
        return QRectF()

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass
    
    # Serialization ====================================================================================================
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
            icon_filename=this_dir+"/icons/info.svg",
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
            icon_filename=this_dir+"/icons/warning.svg",
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
            icon_filename=this_dir+"/icons/error.svg",
            parent=parent
        )

    @classmethod
    def severity(cls):
        """Message severity: how important is this message. Lower is more important."""
        return 1
