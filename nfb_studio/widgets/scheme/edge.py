from typing import Union

from PySide2.QtCore import QPointF, QRectF, QLineF
from PySide2.QtGui import QPainter, QPainterPath, QPen

from nfb_studio.widgets import ShadowSelectableItem

from .style import Style
from .palette import Palette
from .scheme_item import SchemeItem
from .node import Node
from .connection import Input, Output, Connection
from .data_type import DataType


class Edge(SchemeItem, ShadowSelectableItem):
    """An graphics item representing a bezier curve, connecting one node's output to another's input."""

    def __init__(self):
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

        self._path = QPainterPath()
        self._pen = QPen()

        self.styleChange()
        self.paletteChange()

    # Observer functions ===============================================================================================
    def sourceNode(self) -> Union[Node, None]:
        """Return a node from which the edge originates, if it exists.  
        If the edge has no source connection, it consequently has no source node.
        """
        if self.source():
            return self.source().parentItem()
        return None

    def targetNode(self) -> Union[Node, None]:
        """Return a node to which the edge goes, if it exists.  
        If the edge has no target connection, it consequently has no target node.
        """
        if self.target():
            return self.target().parentItem()
        return None

    def source(self) -> Union[Output, None]:
        """Return an output connection from which the edge goes, if it exists.  
        Note that an edge can have a source pos (as in coordinates), but not a source connection.
        """
        return self._source

    def target(self) -> Union[Input, None]:
        """Return an input connection to which the edge goes, if it exists.  
        Note that an edge can have a target pos (as in coordinates), but not a target connection.
        """
        return self._target

    def sourcePos(self) -> Union[QPointF, None]:
        """Return this edge's source position, if it exists.  
        If the edge is connected to a node on the source side, node's output's coordinates is this position. If it is
        not connected but has a statis position set, that is returned. Otherwise, this function returns None.
        """
        return self._source_pos

    def targetPos(self) -> Union[QPointF, None]:
        """Return this edge's source position, if it exists.  
        If the edge is connected to a node on the target side, node's input's coordinates is this position. If it is
        not connected but has a statis position set, that is returned. Otherwise, this function returns None.
        """
        return self._source_pos

    def dataType(self) -> Union[DataType, None]:
        """Return this edge's data type.  
        By themselves, edges do not have a data type. However, if an edge is connected to something, it assumes that
        connection's data type as its own.  
        If the edge is not connected to anything, returns None."""
        if self.source() is not None:
            return self.source().dataType()
        elif self.target() is not None:
            return self.target().dataType()
        
        return None

    # Setter functions =================================================================================================
    def attach(self, connection: Connection):
        """Attach this edge to a connection.  
        This function is similar to setSource and setTarget, but determines which side to attach automatically.
        """
        connection.attach(self)
    
    def detach(self, connection: Connection):
        """Detach this edge from a connection.  
        This function is similar to setSource(None) and setTarget(None), but determines which side to detach
        automatically.
        """
        connection.detach(self)
    
    def detachAll(self):
        """Detach this edge from both source and target nodes."""
        if self.source() is not None:
            self.setSource(None)
        
        if self.target() is not None:
            self.setTarget(None)

    def setTarget(self, target: Union[Input, None]):
        """Set (or unset) the target of this edge.

        Unsetting the target sets the target position to None, which causes the edge to not be drawn, until another
        target (or target position) is supplied.
        """
        assert(target is None or isinstance(target.parentItem(), Node))

        if (self._target is not None) and (self._target is not target):
            # Remove self direcly from self._target.edges instead of calling self._target.detach
            # to prevent infinite recursion.
            self._target.edges.remove(self)

        if target is not None:
            target.edges.add(self)

        self._target = target
        self._target_pos = None

        self.checkDataType()
        self.adjust()

    def setSource(self, source: Union[Output, None]):
        """Set (or unset) the source of this edge.

        Unsetting the source sets the source position to None, which causes the edge to not be drawn, until another
        source (or source position) is supplied.
        """
        assert(source is None or isinstance(source.parentItem(), Node))

        if (self._source is not None) and (self._source is not source):
            # Remove self direcly from self._target.edges instead of calling self._target.detach
            # to prevent infinite recursion.
            self._source.edges.remove(self)

        if source is not None:
            source.edges.add(self)

        self._source = source
        self._source_pos = None  # Is set to None in case source is None. If needed, will be changed by adjust()

        self.checkDataType()
        self.adjust()

    def setTargetPos(self, pos: QPointF):
        """Set target position not from a target connection, but to some static coordinates.

        Useful when drawing an edge to the tip of the mouse. This function sets edge's target to None.
        pos is in scene pixel coordinates.
        """
        self._target = None
        self._target_pos = pos

        self.adjust()

    def setSourcePos(self, pos: QPointF):
        """Set source position not from a source connection, but to some static coordinates.

        Useful when drawing an edge to the tip of the mouse. This function sets edge's source to None.
        pos is in scene pixel coordinates.
        """
        self._source = None
        self._source_pos = pos

        self.adjust()

    # Geometry and drawing =============================================================================================
    def path(self):
        """Compute and return QPainterPath that is used to draw the curved line.  
        Internal function use this to reset their path in response to external changes. 
        """
        if self._source_pos is None or self._target_pos is None:
            return QPainterPath()
        
        result = QPainterPath()
        result.moveTo(self._source_pos)
        result.cubicTo(self._bezier_point_1(), self._bezier_point_2(), self._target_pos)
        
        return result

    def _bezier_offset(self) -> QPointF:
        """Symmetric offset of a control point from source/target.
        
        Bezier calculation functions assume that sourcePos() and targetPos() are not None.
        """
        close_distance = self.style().pixelMetric(Style.EdgeBezierCloseDistance)
        point_offset = self.style().pixelMetric(Style.EdgeBezierPointOffset)

        closeness_factor = min(
            QLineF(self._source_pos, self._target_pos).length() / close_distance,
            1
        )

        return QPointF(point_offset, 0) * closeness_factor

    def _bezier_point_1(self) -> QPointF:
        """Bezier control point 1 for drawing the edge on the screen.
        
        Bezier calculation functions assume that sourcePos() and targetPos() are not None.
        """
        return self._source_pos + self._bezier_offset()

    def _bezier_point_2(self) -> QPointF:
        """Bezier control point 2 for drawing the edge on the screen.
        
        Bezier calculation functions assume that sourcePos() and targetPos() are not None.
        """
        return self._target_pos - self._bezier_offset()

    def boundingRect(self) -> QRectF:
        if self._source_pos is None or self._target_pos is None:
            return QRectF()

        edge_width = self.style().pixelMetric(Style.EdgeWidth)

        return self._path.boundingRect().adjusted(0, -edge_width/2, 0, edge_width/2)

    def paint(self, painter: QPainter, option, widget=...) -> None:
        if self._source_pos is None or self._target_pos is None:
            return

        painter.setPen(self._pen)
        painter.drawPath(self._path)

    # Utility functions ================================================================================================
    def adjust(self):
        """Adjust the edge's coordinates to match those of the input and output of nodes.

        Call this function if the node moved or source/target was changed.
        """
        self.prepareGeometryChange()
        
        if self._source is not None:
            self._source_pos = self._source.mapToScene(self._source.stemTip())

        if self._target is not None:
            self._target_pos = self._target.mapToScene(self._target.stemTip())

        self._path = self.path()  # Recompute path
    
    def checkDataType(self):
        """Check if the data type of two connections matches and raise a ValueError if it does not."""
        if self._source is None or self._target is None:
            return

        if self._source.dataType() != self._target.dataType():
            raise ValueError(
                "data types of connections (\"" +
                str(self._source.dataType()) +
                "\" and \"" +
                str(self._target.dataType()) +
                "\") are not compatible"
            )

    def updateSelectedStatus(self):
        """Checks if both connections at the ends are selected. If so, set this edge to "selected".

        Edges are not selectable - this function only recolors the edge. Opposite also applies - if at least one of the
        nodes is not selected, deselect this edge. This edge queries nodes - not connections - for selected status.
        Connections derive their selected status from edges, not the other way around.
        """
        if self._source is None or self._target is None:
            self.setShadowSelected(False)
            return

        if self.sourceNode().isSelected() and self.targetNode().isSelected():
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

    # Events ===========================================================================================================
    def itemShadowSelectedHasChangedEvent(self, value):
        pal = self.palette()

        if value == True:
            pal.setCurrentColorGroup(Palette.Selected)
        else:
            pal.setCurrentColorGroup(Palette.Active)
        
        self.paletteChange()

    # Style and palette ================================================================================================
    def styleChange(self):
        super().styleChange()
        self.prepareGeometryChange()
        style = self.style()

        self._pen = style.edgePen(self.palette())
        self._path = self.path()  # Recompute path with new parameters
        
    def paletteChange(self):
        self._pen = self.style().edgePen(self.palette())

        self.update(self.boundingRect())
