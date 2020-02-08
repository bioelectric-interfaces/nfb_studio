from PySide2.QtCore import Qt, QPointF, QSizeF, QRectF
from PySide2.QtGui import QPainter, QPainterPath, QColor, QPen, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem, QGraphicsPathItem
from sortedcontainers import SortedList

from nfb_studio.gui import FontF, inches_to_pixels as px, pixels_to_inches as inches
from nfb_studio.widgets import RealSizeItem, TextLineItem, TextRectItem
from nfb_studio.math import clamp

from .connection import Input, Output
from .message import Message


class Node(RealSizeItem):
    """The main component of the graph scene.

    A node represents a single vertex of the graph, with its associated information and inputs/outputs. All sizes and
    positions are measured in inches.
    """
    # Static graphics properties (in inches)
    corner_radius = 0.1  # Rounded rectangle corner radius
    internal_padding = 0.1  # Padding for text inside the body
    divider_padding = 0.05  # Padding between text and the title/description divider
    external_padding = 0.05  # Padding between errors, between error icon and text
    connection_padding = 0.15  # Padding between connections
    outline_thickness = 0.02
    outline_color = Qt.black
    outline_selection_color = QColor.fromRgb(0, 0, 200)
    fill_color = QColor.fromRgb(240, 240, 240)
    fill_selection_color = QColor.fromRgb(247, 247, 255)

    title_font_name = "Segoe UI Semibold"
    title_font_size = 10.5
    description_font_name = "Segoe UI"
    description_font_size = 10.5

    def __init__(self, parent=None):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        # Default size and text
        self._size = QSizeF(2, 1.2)

        self._body_item = QGraphicsPathItem(self)
        self._body_item.setPen(QPen(self.outline_color, px(self.outline_thickness)))
        self._body_item.setBrush(self.fill_color)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(QPointF(), px(self.size())),
            px(self.corner_radius),
            px(self.corner_radius)
        )
        #painter.fillPath(path, self.fill_color)
        self._body_item.setPath(path)

        self._title_item = TextLineItem("Node", self)
        self._title_item.setFont(FontF(self.title_font_name, self.title_font_size))
        title_font_metrics = QFontMetricsF(self._title_item.font())
        self._title_item.setPosition(self.internal_padding, self.internal_padding)
        self._title_item.moveBy(0, title_font_metrics.capHeight())
        self._title_item.setMaximumWidth(self.size().width() - self.internal_padding * 2)

        # Vertical space between body top and the title/description divider
        divider_offset = \
            self.internal_padding + \
            inches(title_font_metrics.capHeight() + title_font_metrics.descent()) + \
            self.divider_padding
        self._divider = QGraphicsLineItem(0, px(divider_offset), px(self.size().width()), px(divider_offset), self)
        self._divider.setPen(QPen(self.outline_color, px(self.outline_thickness)))

        self._description_item = TextRectItem("No description", self)
        self._description_item.setFont(FontF(self.description_font_name, self.description_font_size))
        self._description_item.setPosition(self.internal_padding, divider_offset + self.divider_padding)
        self._description_item.setFrame(
            QRectF(
                QPointF(),
                QSizeF(
                    self.size().width() - self.internal_padding * 2,
                    (self.size().height() - self.internal_padding) -
                    (divider_offset + self.divider_padding)
                )
            )
        )

        # Inputs and outputs
        self.inputs = []
        self.outputs = []
        self.messages = SortedList(key=lambda item: item.severity())

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
    def setSize(self, size):
        self._size = size

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
        i = 0
        for item in self.inputs:
            item.setPosition(0, self.connection_padding * (2 * i + 1))
            i += 1

    def _updateOutputPositions(self):
        i = 0
        for item in self.outputs:
            item.setPosition(self.size().width(), self.connection_padding * (2 * i + 1))
            i += 1

    def _updateMessagePositions(self):
        i = 0
        for msg in self.messages:
            msg.setPosition(
                0,
                self.size().height() +
                self.external_padding * (i + 1) +
                Message.icon_size * i)
            i += 1

    # Geometry and drawing =============================================================================================
    def boundingRect(self) -> QRectF:
        return QRectF(
            QPointF(-px(self.outline_thickness)/2, -px(self.outline_thickness)/2),
            px(self.size()) + QSizeF(px(self.outline_thickness), px(self.outline_thickness))
        )

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(QPointF(0, 0), px(self.size())),
            px(self.corner_radius),
            px(self.corner_radius)
        )

        return path

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            # Update selection status for all connections
            for input in self.inputs:
                input.updateSelectedStatus()

            for output in self.outputs:
                output.updateSelectedStatus()

            # Change color
            if value == True:
                self._body_item.setPen(QPen(self.outline_selection_color, px(self.outline_thickness)))
                self._body_item.setBrush(self.fill_selection_color)
            else:
                self._body_item.setPen(QPen(self.outline_color, px(self.outline_thickness)))
                self._body_item.setBrush(self.fill_color)
            self.update()

        return super().itemChange(change, value)

    def serialize(self) -> dict:
        return {
            "title": self.title(),
            "description": self.description(),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "messages": list(self.messages),
            "position": self.position(),
            "size": self.size()
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
        self.setSize(data["size"])
