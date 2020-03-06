from PySide2.QtCore import Qt, QPointF, QRectF, QLineF
from PySide2.QtGui import QPainter, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem

from nfb_studio.widgets import ShadowSelectableItem, TextLineItem

from ..style import Style
from ..palette import Palette
from ..scheme_item import SchemeItem
from ..data_type import DataType, Unknown
from .connection import Connection


class Output(Connection):
    """A data output from a node."""
    
    def __init__(self, text=None, data_type: DataType = None):
        super().__init__(text or "Output", data_type)

        self._text_item.setAlignMode(Qt.AlignLeft)
        self._trigger_item.setPos(self.stemTip())
        
        self.styleChange()

    # Working with edges ===============================================================================================
    def attach(self, edge):
        """Attach an edge to this connection."""
        edge.setSource(self)

    def detach(self, edge):
        """Detach an edge from this connection.  
        Other connection of this edge is unaffected.
        """
        assert(edge in self.edges)
        assert(edge.source() is self)

        edge.setSource(None)

    def detachAll(self):
        """Detach all edges."""
        edges_ = list(self.edges)  # self.edges will shrink during iteration
        for edge in edges_:
            edge.setSource(None)

    # Style and palette ================================================================================================
    def styleChange(self):
        super().styleChange()
        self.prepareGeometryChange()
        style = self.style()

        margin = style.pixelMetric(Style.ConnectionStemTextMargin)
        metrics = QFontMetricsF(self._text_item.font())

        self._stem_item.setLine(QLineF(self.stemRoot(), self.stemTip()))
        self._text_item.setPos(self.stemTip().x() + margin, metrics.capHeight() / 2)

    # Geometry and drawing =============================================================================================
    def stemRoot(self):
        """Return position of stem's root (where the stem connects to the node) in local coordinates."""
        return QPointF(0, 0)  # Stem root is located exactly at the origin

    def stemTip(self):
        """Return position of stem's root (where the stem connects to the edge) in local coordinates."""
        stem_length = self.style().pixelMetric(Style.ConnectionStemLength)

        return self.stemRoot() + QPointF(stem_length, 0)

    # Drawing edges ====================================================================================================
    # The heavy lifting such as detecting when the edge started being drawn, mouse moving and data transfers are handled
    # by a member item called self._trigger_item. Connection handles the logic.
    def edgeDragAccept(self):
        """Called when a new edge is being dragged into the drop zone.  
        Returns True or False depending on whether the dragged edge should be accepted or not.
        """
        fake_edge = self.scene()._dragging_edge  # The edge being dragged as the mouse moves

        return fake_edge.source() is None and fake_edge.dataType() == self.dataType()

    def edgeDragDrop(self):
        """Called when a new edge has been dragged and was dropped.  
        This operation concludes the edge drawing process. It creates a real edge between source and self.
        """
        scene = self.scene()
        fake_edge = scene._dragging_edge

        scene.connect_nodes(self, fake_edge.target())