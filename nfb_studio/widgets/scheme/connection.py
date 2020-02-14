from PySide2.QtCore import Qt, QPointF, QRectF, QLineF
from PySide2.QtGui import QPainter, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem

from nfb_studio.widgets import ShadowSelectableItem, TextLineItem

from .style import Style
from .palette import Palette
from .scheme_item import SchemeItem
from .data_type import DataType, Unknown


class Connection(SchemeItem, ShadowSelectableItem):
    """Connection is an input or output from a Node."""

    def __init__(self, text=None, data_type: DataType = None, parent: QGraphicsItem = None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)  # To enable edge adjusting
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemHasNoContents)  # Drawing occurs using child items

        self.edges = set()  # Edges related to this connection

        self._text_item = TextLineItem(text or "Connection", self)
        self._stem_item = QGraphicsLineItem(self)

        self._data_type = data_type or Unknown

        self.styleChange()
        self.paletteChange()

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
    
    def styleChange(self):
        super().styleChange()
        style = self.style()

        self._text_item.setFont(style.font(Style.ConnectionTextFont))
        self._text_item.setMaximumWidth(style.pixelMetric(Style.ConnectionTextLength))

        self._stem_item.setPen(style.edgePen(self.palette()))

    def paletteChange(self):
        super().paletteChange()
        text_bg = self.palette().background().color()
        text_bg.setAlpha(196)

        self._text_item.setBackgroundBrush(text_bg)
        self._text_item.setBrush(self.palette().text())

        self._stem_item.setPen(self.style().edgePen(self.palette()))

    def itemChange(self, change, value):
        """A function that runs every time some change happens to the connection.
        This processes position changes by adjusting all the edges and forwards the arguments to the superclass.
        """
        if change == QGraphicsItem.ItemScenePositionHasChanged:
            for edge in self.edges:
                edge.adjust()

        return super().itemChange(change, value)

    def itemShadowSelectedHasChangedEvent(self, value):
        pal = self.palette()

        if value == True:
            pal.setCurrentColorGroup(Palette.Selected)
        else:
            pal.setCurrentColorGroup(Palette.Active)
        
        self.paletteChange()

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

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        return {
            "text": self.text(),
            "data_type": self.dataType()
        }

    def deserialize(self, data: dict):
        self.setText(data["text"])
        self.setDataType(data["data_type"])


class Input(Connection):
    """A data input into a node."""

    def __init__(self, text=None, data_type: DataType = None):
        super().__init__(text or "Input", data_type)

        self._text_item.setAlignMode(Qt.AlignRight)

        self.styleChange()

    def styleChange(self):
        super().styleChange()
        self.prepareGeometryChange()
        style = self.style()

        margin = style.pixelMetric(Style.ConnectionStemTextMargin)
        metrics = QFontMetricsF(self._text_item.font())

        self._stem_item.setLine(QLineF(self.stemRoot(), self.stemTip()))
        self._text_item.setPos(self.stemTip().x() - margin, metrics.capHeight() / 2)

    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local coordinates."""
        return QPointF(0, 0)  # Stem root is located exactly at the origin

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local coordinates."""
        stem_length = self.style().pixelMetric(Style.ConnectionStemLength)

        return self.stemRoot() - QPointF(stem_length, 0)


class Output(Connection):
    """A data output from a node."""
    
    def __init__(self, text=None, data_type: DataType = None):
        super().__init__(text or "Output", data_type)

        self._text_item.setAlignMode(Qt.AlignLeft)
        
        self.styleChange()

    def styleChange(self):
        super().styleChange()
        self.prepareGeometryChange()
        style = self.style()

        margin = style.pixelMetric(Style.ConnectionStemTextMargin)
        metrics = QFontMetricsF(self._text_item.font())

        self._stem_item.setLine(QLineF(self.stemRoot(), self.stemTip()))
        self._text_item.setPos(self.stemTip().x() + margin, metrics.capHeight() / 2)

    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local coordinates."""
        return QPointF(0, 0)  # Stem root is located exactly at the origin

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local coordinates."""
        stem_length = self.style().pixelMetric(Style.ConnectionStemLength)

        return self.stemRoot() + QPointF(stem_length, 0)
