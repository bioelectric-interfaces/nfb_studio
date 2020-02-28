from PySide2.QtCore import Qt, QPointF, QRectF, QLineF
from PySide2.QtGui import QPainter, QFontMetricsF
from PySide2.QtWidgets import QGraphicsItem, QGraphicsLineItem

from nfb_studio.widgets import ShadowSelectableItem, TextLineItem

from ..style import Style
from ..palette import Palette
from ..scheme_item import SchemeItem
from ..data_type import DataType, Unknown
from .connection import Connection
from .edge_drag import EdgeDrag

class Input(Connection):
    """A data input into a node."""

    def __init__(self, text=None, data_type: DataType = None):
        super().__init__(text or "Input", data_type)

        self._text_item.setAlignMode(Qt.AlignRight)
        self._trigger_item.setPos(self.stemTip())

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

    # Drawing edges ====================================================================================================
    # The heavy lifting such as detecting when the edge started being drawn, mouse moving and data transfers are handled
    # by a member item called self._trigger_item. Connection handles the logic.
    def edgeDragStart(self) -> EdgeDrag:
        """Called when user tries to drag an edge from this connection.
        
        This operation starts the edge drawing process. It returns an EdgeDrag object that will be given to the
        reciever.
        """
        scene = self.scene()
        to_remove = list(self.edges)
        for edge in to_remove:
            scene.removeItem(edge)

        result = EdgeDrag()
        node = self.parentItem()

        result.node_id = id(node)
        result.connection_type = "Input"
        result.connection_index = node.inputs.index(self)
        result.data_type = self.dataType()
        
        return result

    def edgeDragAccept(self, edge_drag: EdgeDrag):
        """Called when a new edge is being dragged into the drop zone.
        
        Returns True or False depending on whether the dragged edge should be accepted or not.
        """
        return (edge_drag.connection_type != "Input" and edge_drag.data_type == self.dataType())

    def edgeDragDrop(self, edge_drag: EdgeDrag):
        """Called when a new edge has been dragged and was dropped.
        
        This operation concludes the edge drawing process.
        """
        scene = self.scene()

        target = self

        source_node = scene.findNode(edge_drag.node_id)
        source = source_node.outputs[edge_drag.connection_index]

        scene.connect_nodes(source, target)
