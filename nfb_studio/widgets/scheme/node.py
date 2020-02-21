from PySide2.QtCore import QPointF, QSizeF, QRectF
from PySide2.QtGui import QPainter, QPainterPath, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsPathItem
from sortedcontainers import SortedList

from nfb_studio.gui import inches_to_pixels as px
from nfb_studio.math import clamp

from ..text_line_item import TextLineItem
from ..text_rect_item import TextRectItem
from .scheme_item import SchemeItem
from .connection import Input, Output
from .message import Message
from .style import Style


class Node(SchemeItem):
    """The main component of the graph scene.

    A node represents a single vertex of the graph, with its associated information and inputs/outputs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Default size and text
        self._size = QSizeF(0, 115)

        self._body_item = QGraphicsPathItem(self)
        self._title_item = TextLineItem("Node", self)
        self._divider = QGraphicsLineItem(self)
        self._description_item = TextRectItem("No description", self)

        # Inputs and outputs
        self.inputs = []
        self.outputs = []
        self.messages = SortedList(key=lambda item: item.severity())

        # Set proper style and color for the item
        self.styleChange()
        self.paletteChange()

    # Input/output management ==========================================================================================
    def addInput(self, obj: Input):
        self.insertInput(len(self.inputs), obj)

    def insertInput(self, index, obj: Input):
        index = clamp(index, 0, len(self.inputs))
        self.inputs.insert(index, obj)

        obj.setParentItem(self)

        self._updateInputPositions()

    def removeInput(self, index):
        removed = self.inputs.pop(index)
        removed.setParentItem(None)

        self._updateInputPositions()

        return removed

    def addOutput(self, obj: Output):
        self.insertOutput(len(self.outputs), obj)

    def insertOutput(self, index, obj: Output):
        index = clamp(index, 0, len(self.outputs))
        self.outputs.insert(index, obj)

        obj.setParentItem(self)

        self._updateOutputPositions()

    def removeOutput(self, index):
        removed = self.outputs.pop(index)
        removed.setParentItem(None)

        self._updateOutputPositions()

        return removed

    # Message management ===============================================================================================
    def addMessage(self, obj: Message):
        self.messages.add(obj)
        obj.setParentItem(self)

        self._updateMessagePositions()

    def removeMessage(self, index):
        removed = self.messages.pop(index)
        removed.setParentItem(None)

        self._updateMessagePositions()

        return removed

    # Member variables =================================================================================================
    def setTitle(self, title):
        self._title_item.setText(title)

    def setDescription(self, description):
        self._description_item.setText(description)

    def size(self):
        return self._size

    def title(self):
        return self._title_item.text()

    def description(self):
        return self._description_item.text()

    # Updating functions ===============================================================================================
    def _updateInputPositions(self):
        padding = self.style().pixelMetric(Style.NodeConnectionPadding)

        i = 0
        for item in self.inputs:
            item.setPos(0, padding * (2 * i + 1))
            i += 1

    def _updateOutputPositions(self):
        padding = self.style().pixelMetric(Style.NodeConnectionPadding)

        i = 0
        for item in self.outputs:
            item.setPos(self.size().width(), padding * (2 * i + 1))
            i += 1

    def _updateMessagePositions(self):
        padding = self.style().pixelMetric(Style.NodeMessagePadding)
        icon_size = self.style().pixelMetric(Style.MessageIconSize)

        i = 0
        for msg in self.messages:
            msg.setPos(
                0,
                self.size().height() +
                padding * (i + 1) +
                icon_size * i)
            i += 1

    # Geometry and drawing =============================================================================================
    def boundingRect(self) -> QRectF:
        frame_width = self.style().pixelMetric(Style.NodeFrameWidth)

        return QRectF(
            QPointF(-frame_width/2, -frame_width/2),
            self.size() + QSizeF(frame_width, frame_width)
        )

    def shape(self):
        frame_corner_radius = self.style().pixelMetric(Style.NodeFrameCornerRadius)

        path = QPainterPath()
        path.addRoundedRect(QRectF(QPointF(0, 0), self.size()), frame_corner_radius, frame_corner_radius)

        return path

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass
    
    # Event handlers ===================================================================================================
    def styleChange(self):
        self.prepareGeometryChange()
        style = self.style()

        # Size and Frame
        frame_width = style.pixelMetric(Style.NodeWidth)
        self._size.setWidth(frame_width)
        self._body_item.setPen(style.framePen(self.palette()))

        path = QPainterPath()
        path.addRoundedRect(
            QRectF(QPointF(), self.size()),
            style.pixelMetric(Style.NodeFrameCornerRadius),
            style.pixelMetric(Style.NodeFrameCornerRadius)
        )
        self._body_item.setPath(path)
        
        # Title item
        title_font = style.font(Style.NodeTitleFont)
        title_metrics = QFontMetricsF(title_font)

        padding = style.pixelMetric(Style.NodeFrameTextPadding)

        self._title_item.setFont(title_font)
        self._title_item.setPos(padding, padding)
        self._title_item.moveBy(0, title_metrics.capHeight())
        self._title_item.setMaximumWidth(frame_width - padding * 2)

        # Divider item
        div_margin = style.pixelMetric(Style.NodeDividerTextMargin)
        div_voffset = padding + title_metrics.capHeight() + title_metrics.descent() + div_margin
        
        self._divider.setLine(0, div_voffset, frame_width, div_voffset)
        self._divider.setPen(style.framePen(self.palette()))

        # Description item
        self._description_item.setFont(style.font(Style.NodeDescriptionFont))
        self._description_item.setPos(padding, div_voffset + div_margin)
        self._description_item.setFrame(
            QRectF(
                QPointF(0, 0),
                QSizeF(
                    px(frame_width) - padding * 2,
                    (px(self.size().height()) - padding) -
                    (div_voffset + padding)
                )
            )
        )
        
    def paletteChange(self):
        self._body_item.setPen(self.style().framePen(self.palette()))
        self._body_item.setBrush(self.palette().base())
        self._title_item.setBrush(self.palette().text())
        self._description_item.setBrush(self.palette().text())
        self._divider.setPen(self.style().framePen(self.palette()))

        self.update(self.boundingRect())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            # Update selection status for all connections
            for input in self.inputs:
                input.updateSelectedStatus()

            for output in self.outputs:
                output.updateSelectedStatus()

        return super().itemChange(change, value)

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        return {
            "title": self.title(),
            "description": self.description(),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "messages": list(self.messages),
            "position": self.position()
        }

    def deserialize(self, data: dict):
        self.setTitle(data["title"])
        self.setDescription(data["description"])

        for input in data["inputs"]:
            self.addInput(input)

        for output in data["outputs"]:
            self.addOutput(output)

        for message in data["messages"]:
            self.addMessage(message)

        self.setPosition(data["position"])
