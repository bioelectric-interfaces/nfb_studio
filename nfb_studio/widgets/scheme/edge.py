from typing import Union

from Qt.QtCore import Qt, QPointF, QRectF, QLineF
from Qt.QtGui import QColor, QPainter, QPainterPath, QPen

from nfb_studio.gui import inches_to_pixels as px
from nfb_studio.widgets import RealSizeItem, ShadowSelectableItem

from .node import Node
from .connection import Input, Output


class Edge(RealSizeItem, ShadowSelectableItem):
    # Static graphics properties (in inches)
    outline_thickness = 0.02
    outline_color = Qt.black
    outline_selection_color = QColor.fromRgb(0, 0, 200)

    bezier_max_point_offset = 0.8
    """Horizontal offset of control points on a bezier curve compared to its endpoints"""
    bezier_close_distance = 1.5
    """Distance that's considered "too close" by the algorithm
    If distance between source and target is less that this variable, move control points closer together.
    """

    def __init__(self):
        """An graphics item representing a bezier curve, connecting one node's output to another's input.
        """
        super(Edge, self).__init__()
        self.setZValue(-1)  # Draw edges behind nodes

        self._source: Union[Output, None] = None
        """An edge is drawn from its source to its target. Node's output is edge's source.
        This variable represents current source as a variable of type Output.
        """
        self._target: Union[Input, None] = None
        """An edge is drawn from its source to its target. Node's input is edge's target.
        This variable represents current target as a variable of type Input.
        """

        self._source_pos: Union[QPointF, None] = None
        """An edge is drawn from its source to its target. Node's output is edge's source.
        This variable represents current source coordinates in scene pixels.
        """
        self._target_pos: Union[QPointF, None] = None
        """An edge is drawn from its source to its target. Node's input is edge's target.
        This variable represents current target coordinates in scene pixels.
        """

        self._pen = QPen(self.outline_color, px(self.outline_thickness))

    def source_node(self) -> Union[Node, None]:
        """Return a node from which the edge originates, if it exists.

        If the edge has no source connection, it consequently has no source node.
        """
        if self.source():
            return self.source().parentItem()
        return None

    def target_node(self) -> Union[Node, None]:
        """Return a node to which the edge goes, if it exists.

        If the edge has no target connection, it consequently has no target node.
        """
        if self.target():
            return self.target().parentItem()
        return None

    def source(self) -> Union[Output, None]:
        return self._source

    def target(self) -> Union[Input, None]:
        return self._target

    def setTarget(self, target: Union[Input, None]):
        """Set (or unset) the target of this edge.
        Unsetting the target sets the target position to None, which causes the edge to not be drawn, until another
        target (or target position) is supplied.
        """
        self._target = target

        if target is None:
            self.prepareGeometryChange()
            self._target_pos = None
        else:
            self.checkDataType()
            self.adjust()

    def setSource(self, source: Union[Output, None]):
        """Set (or unset) the target of this edge.
        Unsetting the source sets the source position to None, which causes the edge to not be drawn, until another
        source (or source position) is supplied.
        """
        self._source = source

        if source is None:
            self.prepareGeometryChange()
            self._source_pos = None
        else:
            self.checkDataType()
            self.adjust()

    def setTargetPos(self, pos: QPointF):
        """Set target position not from a target connection, but to some static coordinates.
        Useful when drawing an edge to the tip of the mouse. This function sets edge's target to None.
        pos is in scene pixel coordinates.
        """
        self._target = None

        self.prepareGeometryChange()
        self._target_pos = pos

    def setSourcePos(self, pos: QPointF):
        """Set source position not from a source connection, but to some static coordinates.
        Useful when drawing an edge to the tip of the mouse. This function sets edge's source to None.
        pos is in scene pixel coordinates.
        """
        self._source = None

        self.prepareGeometryChange()
        self._source_pos = pos

    def setPen(self, pen: QPen):
        self._pen = pen

    def pen(self) -> QPen:
        return self._pen

    def adjust(self):
        """Adjust the edge's coordinates to match those of the input and output of nodes.
        Call this function if the node moved or source/target was changed.
        """
        if self._source is None or self._target is None:
            return

        self.prepareGeometryChange()

        self._source_pos = self._source.mapToScene(px(self._source.stemTip()))
        self._target_pos = self._target.mapToScene(px(self._target.stemTip()))

    def _bezier_offset(self) -> QPointF:
        """Symmetric offset of a control point from source/target."""
        closeness_factor = min(
            QLineF(self._source_pos, self._target_pos).length() / px(self.bezier_close_distance),
            1
        )

        return QPointF(px(self.bezier_max_point_offset), 0) * closeness_factor

    def _bezier_point_1(self) -> QPointF:
        """Bezier control point 1 for drawing the edge on the screen."""
        return self._source_pos + self._bezier_offset()

    def _bezier_point_2(self) -> QPointF:
        """Bezier control point 2 for drawing the edge on the screen."""
        return self._target_pos - self._bezier_offset()

    def boundingRect(self) -> QRectF:
        if self._source_pos is None or self._target_pos is None:
            return QRectF()

        left = min(self._source_pos.x(), self._bezier_point_2().x())
        right = max(self._target_pos.x(), self._bezier_point_1().x())

        top = min(self._source_pos.y(), self._target_pos.y())
        bottom = max(self._source_pos.y(), self._target_pos.y())

        extra = px(self.outline_thickness)/2

        return QRectF(QPointF(left, top), QPointF(right, bottom)).adjusted(0, -extra, 0, extra)

    def paint(self, painter: QPainter, option, widget=...) -> None:
        if self._source_pos is None or self._target_pos is None:
            return

        painter.setPen(self.pen())

        path = QPainterPath()
        path.moveTo(self._source_pos)
        path.cubicTo(self._bezier_point_1(), self._bezier_point_2(), self._target_pos)
        painter.drawPath(path)

    def itemShadowSelectedHasChangedEvent(self, value):
        if value == True:
            self.setPen(QPen(self.outline_selection_color, px(self.outline_thickness)))
        else:
            self.setPen(QPen(self.outline_color, px(self.outline_thickness)))
        self.update()

    def checkDataType(self):
        """Check if the data type of two connections matches and raise a ValueError if it does not."""
        if self._source is None or self._target is None:
            return

        if self._source.dataType() != self._target.dataType():
            raise ValueError(
                "edge: data types of connections (\"" +
                str(self._source.dataType()) +
                "\" and \"" +
                str(self._target.dataType()) +
                "\") are not compatible"
            )

    def updateSelectedStatus(self):
        """Checks if both connections at the ends are selected. If so, set this edge to "selected".
        Edges are not selectable - this function only recolors the edge.
        Opposite also applies - if at least one of the nodes is not selected, deselect this edge.
        This edge queries nodes - not connections - for selected status. Connections derive their selected status from
        edges, not the other way around.
        """
        if self._source is None or self._target is None:
            self.setShadowSelected(False)
            return

        if self.source_node().isSelected() and self.target_node().isSelected():
            self.setShadowSelected(True)
            # Edge does not know which connection called this update. If source called it, target does not know it has
            # to be selected. So the edge explicitly selects both.
            self._source.setShadowSelected(True)
            self._target.setShadowSelected(True)
        else:
            # When deselecting, the connections might still be selected because of other edges - so instead of
            # explicitly deselecting both connections, edge calls updateSelectedStatus() on them.
            # This happens only when the edge was "toggled", not "set", to prevent infinite recursion.
            is_toggled = self.isShadowSelected()
            self.setShadowSelected(False)

            if is_toggled:
                self._source.updateSelectedStatus()
                self._target.updateSelectedStatus()
