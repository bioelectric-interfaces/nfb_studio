from Qt.QtCore import Qt, QPointF, QRectF, QLineF
from Qt.QtGui import QPainter, QFontMetricsF, QPen, QBrush, QColor
from Qt.QtWidgets import QGraphicsItem, QGraphicsLineItem

from nfb_studio.gui import FontF, inches_to_pixels as px
from nfb_studio.widgets import RealSizeItem, ShadowSelectableItem, TextLineItem

from .data_type import DataType, Unknown


class Connection(RealSizeItem, ShadowSelectableItem):
    stem_length = 0.2  # Length of the line going out of the
    max_text_length = 1.5  # Horizontal length of the box in which the text is drawn
    stem_text_margin = 0.05  # Space between stem and title
    outline_thickness = 0.02
    outline_color = Qt.black
    outline_selection_color = QColor.fromRgb(0, 0, 200)

    text_font_name = "Segoe UI"
    text_font_size = 10.5

    def __init__(self, text=None, data_type: DataType = None):
        """Connection is an input or output from a Node."""
        super(Connection, self).__init__()
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)  # To enable edge adjusting
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemHasNoContents)  # Drawing occurs using child items

        self.edges = set()  # Edges related to this connection

        # Connection text ----------------------------------------------------------------------------------------------
        self._text_item = TextLineItem(text or "Connection", self)
        self._text_item.setFont(FontF(self.text_font_name, self.text_font_size))
        self._text_item.setMaximumWidth(self.max_text_length)

        # Position is controlled by subclasses Input and Output

        # Background color
        self._text_item.setBackgroundBrush(QBrush(QColor(255, 255, 255, 196)))

        # Connection stem ----------------------------------------------------------------------------------------------
        self._stem_item = QGraphicsLineItem(self)
        self._stem_item.setPen(QPen(self.outline_color, px(self.outline_thickness)))

        # Position is controlled by subclasses Input and Output

        # --------------------------------------------------------------------------------------------------------------

        self._data_type = data_type or Unknown

    def text(self):
        return self._text_item.text()

    def dataType(self):
        return self._data_type

    def setText(self, text):
        self._text_item.setText(text)

    def setDataType(self, data_type):
        self._data_type = data_type

        for edge in self.edges:
            # Verify that all edges are fine with changing the data type.
            edge.checkDataType()

    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local inches."""
        raise NotImplementedError()

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local inches."""
        raise NotImplementedError()

    def itemChange(self, change, value):
        """A function that runs every time some change happens to the connection.
        This processes position changes by adjusting all the edges and forwards the arguments to the superclass.
        """
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for edge in self.edges:
                edge.adjust()

        return super().itemChange(change, value)

    def itemShadowSelectedHasChangedEvent(self, value: bool):
        if value == True:
            self._stem_item.setPen(QPen(self.outline_selection_color, px(self.outline_thickness)))
        else:
            self._stem_item.setPen(QPen(self.outline_color, px(self.outline_thickness)))
        self.update()

    def boundingRect(self):
        return QRectF()

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass

    def updateSelectedStatus(self):
        """Checks if at least one edge is selected. If so, set this connection to selected.
        Opposite also applies - if no edges are selected, deselect this edge.
        The connection is responsible to propagate this call to edges.
        """
        for edge in self.edges:
            edge.updateSelectedStatus()

        for edge in self.edges:
            if edge.isShadowSelected():
                self.setShadowSelected(True)
                break
        else:
            self.setShadowSelected(False)

    def serialize(self) -> dict:
        return {
            "text": self.text(),
            "data_type": self.dataType()
        }

    def deserialize(self, data: dict):
        self.setText(data["text"])
        self.setDataType(data["data_type"])


class Input(Connection):
    def __init__(self, text=None, data_type: DataType = None):
        """A data input into a node."""
        super(Input, self).__init__(text or "Input", data_type)

        # Connection text ----------------------------------------------------------------------------------------------
        metrics = QFontMetricsF(self._text_item.font())
        self._text_item.setAlignMode(Qt.AlignRight)
        self._text_item.setPos(px(self.stemTip().x() - self.stem_text_margin), metrics.capHeight() / 2)

        # Connection stem ----------------------------------------------------------------------------------------------
        self._stem_item.setLine(QLineF(px(self.stemRoot()), px(self.stemTip())))

    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local inches."""
        return QPointF(0, 0)

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local inches."""
        return self.stemRoot() - QPointF(self.stem_length, 0)


class Output(Connection):
    def __init__(self, text=None, data_type: DataType = None):
        """A data input into a node."""
        super(Output, self).__init__(text or "Output", data_type)

        # Connection text ----------------------------------------------------------------------------------------------
        metrics = QFontMetricsF(self._text_item.font())
        self._text_item.setAlignMode(Qt.AlignLeft)
        self._text_item.setPos(px(self.stemTip().x() + self.stem_text_margin), metrics.capHeight() / 2)

        # Connection stem ----------------------------------------------------------------------------------------------
        self._stem_item.setLine(QLineF(px(self.stemRoot()), px(self.stemTip())))

    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local inches."""
        return QPointF(0, 0)  # Stem root is located exactly at the origin

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local inches."""
        return self.stemRoot() + QPointF(self.stem_length, 0)
