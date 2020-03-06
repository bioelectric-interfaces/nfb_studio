from PySide2.QtCore import Qt, QPointF, QRectF, QLineF
from PySide2.QtGui import QPainter, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem

from nfb_studio.widgets import ShadowSelectableItem, TextLineItem

from ..style import Style
from ..palette import Palette
from ..scheme_item import SchemeItem
from ..data_type import DataType, Unknown
from .edge_drag import EdgeDrag
from .trigger import Trigger

class Connection(SchemeItem, ShadowSelectableItem):
    """Connection is an input or output from a Node."""

    def __init__(self, text=None, data_type: DataType = None, parent: QGraphicsItem = None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)  # To enable edge adjusting
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemHasNoContents)  # Drawing occurs using child items

        self.edges = set()
        """Edges attached to this connection. To change this set use `Connection`'s methods: attach, detach, detachAll.
        """

        self._text_item = TextLineItem(text or "Connection", self)
        self._stem_item = QGraphicsLineItem(self)

        self._trigger_item = Trigger(self)

        self._data_type = data_type or Unknown

        self.styleChange()
        self.paletteChange()

    # Working with edges ===============================================================================================
    def attach(self, edge):
        """Attach an edge to this connection."""
        raise NotImplementedError

    def detach(self, edge):
        """Detach an edge from this connection.  
        Other connection of this edge is unaffected.
        """
        raise NotImplementedError

    def detachAll(self):
        """Detach all edges."""
        raise NotImplementedError

    # Member access ====================================================================================================
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

    # Geometry and drawing =============================================================================================
    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local inches."""
        raise NotImplementedError

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local inches."""
        raise NotImplementedError
    
    def boundingRect(self):
        return QRectF()

    def paint(self, painter: QPainter, option, widget=...) -> None:
        pass

    # Style and palette ================================================================================================
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

    # Events ===========================================================================================================
    def itemChange(self, change, value):
        """A function that runs every time some change happens to the connection.
        
        This processes position changes by adjusting all the edges and forwards the arguments to the superclass.
        """
        if change == QGraphicsItem.ItemScenePositionHasChanged or change == QGraphicsItem.ItemVisibleHasChanged:
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
    
    # Drawing edges ====================================================================================================
    # The heavy lifting such as detecting when the edge started being drawn, mouse moving and data transfers are handled
    # by a member item called self._trigger_item. Connection handles the logic.
    def edgeDragStart(self):
        """Called when user tries to drag an edge from this connection."""
        self.scene().edgeDragStart(self)

    def edgeDragAccept(self) -> bool:
        """Called when a new edge is being dragged into the drop zone.  
        Returns True or False depending on whether the dragged edge should be accepted or not.
        """
        raise NotImplementedError

    def edgeDragDrop(self):
        """Called when a new edge has been dragged and was dropped.  
        This operation concludes the edge drawing process.
        """
        raise NotImplementedError