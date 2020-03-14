"""A data model for the nfb experiment's system of signals and their components."""
from typing import Union

from PySide2.QtCore import Qt, QPointF, QMimeData
from PySide2.QtGui import QPainter, QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QShortcut, QApplication

from nfb_studio.serial import mime, hooks

from .graph import AbstractGraph, Graph, GraphSnapshot
from .node import Node
from .edge import Edge
from .connection import Input, Output, Connection
from .connection.edge_drag import EdgeDrag
from .style import Style
from .palette import Palette

class Scheme(QGraphicsScene):
    """A data model for the nfb experiment's system of signals and their components.

    This class is a combination of three things:
    - nfb_studio.widgets.scheme.Graph: a graph of nodes and edges;
    - QGraphicsScene (inherits): a Qt representation of that graph and additional items;
    - QGraphicsView: a view of QGraphicsScene. Only one view is allowed - creating multiple views will make the program
    behave incorrectly.

    The main components are available as self.graph, super() and self.view.

    See Also
    --------
    nfb_studio.widgets.scheme.Node : Graph node.
    nfb_studio.widgets.scheme.Edge : Graph edge.
    nfb_studio.widgets.scheme.Graph : A collection of nodes and edges.
    """
    class View(QGraphicsView):
        def __init__(self, parent=None):
            super().__init__(parent=parent)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setRubberBandSelectionMode(Qt.ContainsItemShape)
            self.setRenderHint(QPainter.Antialiasing)
            self.setRenderHint(QPainter.SmoothPixmapTransform)

            # Remove the scrollbars
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.setSceneRect(0, 0, self.size().width(), self.size().height())

        def setScene(self, scene):
            if not isinstance(scene, Scheme):
                raise TypeError("Scheme.View only connects to a Scheme as its data source")

            super().setScene(scene)
            cut_shortcut = QShortcut(QKeySequence.Cut, self)
            cut_shortcut.activated.connect(scene.cutEvent)

            copy_shortcut = QShortcut(QKeySequence.Copy, self)
            copy_shortcut.activated.connect(scene.copyEvent)

            paste_shortcut = QShortcut(QKeySequence.Paste, self)
            paste_shortcut.activated.connect(scene.pasteEvent)

            delete_shortcut = QShortcut(QKeySequence.Delete, self)
            delete_shortcut.activated.connect(scene.deleteEvent)
        



    def __init__(self, parent=None):
        """Constructs a Scheme with an optional `parent` parameter that is passed to the super()."""
        super().__init__(parent)
        self.graph = Graph()

        self.view = self.View()
        self.view.setScene(self)

        # Drag-drawing edges support -----------------------------------------------------------------------------------
        self._dragging_edge = None
        """A temporary edge that is being displayed when an edge is drawn by the user with drag and drop."""

        # Style and palette --------------------------------------------------------------------------------------------
        self._style = Style()
        self._palette = Palette()

        self.styleChange()
        self.paletteChange()

    # Element manipulation =============================================================================================
    def addItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of super().addItem method that detects when a node or edge was added.
        """
        if isinstance(item, Node):
            self.graph.addNode(item)
        elif isinstance(item, Edge):
            self.graph.addEdge(item)
        else:
            raise TypeError("unrecognised graphics item of type " + type(item).__name__)

        super().addItem(item)

    def removeItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of super().removeItem method that detects when a node or edge was removed.
        """
        super().removeItem(item)

        # Remove a Node ------------------------------------------------------------------------------------------------
        if isinstance(item, Node):
            # Remove connected edges first
            to_remove = []
            for edge in self.graph.edges:
                if edge.sourceNode() is item or edge.targetNode() is item:
                    to_remove.append(edge)
            
            for edge in to_remove:
                self.removeItem(edge)

            # Remove the node
            self.graph.removeNode(item)
        # Remove an Edge -----------------------------------------------------------------------------------------------
        elif isinstance(item, Edge):
            self.graph.removeEdge(item)
        # Unknown item -------------------------------------------------------------------------------------------------
        else:
            raise TypeError("unrecognised graphics item of type " + type(item).__name__)

    def connect_nodes(self, source: Output, target: Input):
        """Connect an Output connection to an Input connection with an edge.
        
        Returns the newly created edge.
        """
        edge = self.graph.connect_nodes(source, target)
        super().addItem(edge)

        return edge

    def disconnect_nodes(self, source: Output, target: Input):
        """Remove a connection between a node output and an input.
        
        If output and input are connected more than once, only one edge is removed.
        Returns the edge that was removed, or None if no such edge was found.
        """
        edge = self.graph.disconnect_nodes(source, target)
        if edge is not None:
            super().removeItem(edge)
        return edge

    def extract(self, other: AbstractGraph):
        """Update the scheme, removing elements from a graph.
        
        `other` represents a subgraph of the scheme graph that is to be extracted.
        """
        for edge in other.edges:
            self.removeItem(edge)

        for node in other.nodes:
            self.removeItem(node)

    def merge(self, other: AbstractGraph):
        """Update the scheme, adding elements from a graph."""
        self.graph.merge(other)

        for node in other.nodes:
            super().addItem(node)
        for edge in other.edges:
            super().addItem(edge)

    def clear(self):
        """Clear the scheme."""
        super().clear()
        self.graph.clear()

    # Observer methods =================================================================================================
    def findNode(self, node_id: int) -> Union[Node, None]:
        return self.graph.findNode(node_id)

    # Selection ========================================================================================================
    def selectAll(self):
        self.graph.selectAll()

    def selection(self) -> GraphSnapshot:
        return self.graph.selection()
    
    def clipboardSelection(self) -> GraphSnapshot:
        return self.graph.clipboardSelection()
    
    def wideSelection(self) -> GraphSnapshot:
        return self.graph.wideSelection()

    # User actions =====================================================================================================
    def cutEvent(self):
        """Cut the selected graph and place it in the clipboard."""
        self.copyEvent()
        self.deleteEvent()

    def copyEvent(self):
        """Copy the selected graph and place it in the clipboard."""
        snapshot = self.clipboardSelection()
        if len(snapshot.nodes) == 0:  # Nothing to copy
            return

        package = QMimeData()
        mime.dump(snapshot, package, "application/x-nfb_studio-graph", hooks=hooks.qt)

        clipboard = QApplication.clipboard()
        clipboard.setMimeData(package)

    def pasteEvent(self):
        """Retrieve the data from a clipboard and paste it."""
        clipboard = QApplication.clipboard()
        package = clipboard.mimeData()

        if package.hasFormat("application/x-nfb_studio-graph"):
            snapshot = mime.load(package, "application/x-nfb_studio-graph", hooks=hooks.qt)
            self.merge(snapshot)

            self.clearSelection()  # Clear old selection
            snapshot.selectAll()  # Create new selection (pasted items)

            offset = self.schemeStyle().pixelMetric(Style.PasteOffset)
            snapshot.moveBy(offset, offset)  # Move all items by some offset 

            self.copyEvent()  # Copy the selection again (nothing changes except for the item offset)

    def deleteEvent(self):
        """Delete the selection."""
        self.extract(self.selection())

    # Style and palette ================================================================================================
    def styleChange(self):
        pass

    def paletteChange(self):
        super().setBackgroundBrush(self.schemePalette().background())

    def schemeStyle(self):
        return self._style

    def setStyle(self, style):
        self._style = style
        self.styleChange()

    def schemePalette(self):
        return self._palette
    
    def setPalette(self, palette):
        self._palette = palette
        self.paletteChange()

    # Edge drawing =====================================================================================================
    def hasEdgeDrag(self) -> bool:
        """Returns True if an edge is currently being drawn via drag and drop."""
        return self._dragging_edge is not None

    def edgeDragStart(self, connection: Connection):
        """Triggers a start to an edge drawing mode.  
        By holding left mouse button while dragging from an end of a connection, user can start dragging an edge from
        one connection to the other. The scene stores a "fake" edge that the user drags with their mouse. That edge is
        created here and updated with mouse movements in dragMoveEvent.
        """
        self._dragging_edge = Edge()
        self._dragging_edge.attach(connection)       

        super().addItem(self._dragging_edge)  # Edge is present in the scene, but not in the graph.

    def edgeDragStop(self):
        """Triggers an end of an edge drawing mode.  
        Cleans up by removing the fake edge. This function is called from the QDrag-like object, EdgeDrag.
        """
        super().removeItem(self._dragging_edge)

        self._dragging_edge.detachAll()
        self._dragging_edge = None

    def dragEnterEvent(self, event):
        package = event.mimeData()
        event.setAccepted(package.hasFormat("application/x-toolbox-node"))
        print("ok tho")
    
    def dropEvent(self, event):
        package = event.mimeData()
        node = mime.load(package, "application/x-toolbox-node", hooks=hooks.qt)

        node.setPos(event.scenePos())
        self.addItem(node)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(EdgeDrag.format) and self.hasEdgeDrag():
            # Update edge position, but otherwise do the default thing.
            super().dragMoveEvent(event)  
            if self._dragging_edge.source() is None:
                self._dragging_edge.setSourcePos(event.scenePos())
            else:
                self._dragging_edge.setTargetPos(event.scenePos())

    # Key presses ======================================================================================================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Alt:
            event.accept()
            for node in self.graph.nodes:
                node.showConnectionText()
            return
        
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Alt:
            event.accept()
            for node in self.graph.nodes:
                node.hideConnectionText()
            return

        super().keyReleaseEvent(event)

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        return self.graph.serialize()

    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data."""
        # Clear --------------------------------------------------------------------------------------------------------
        for node in self.nodes:
            self.removeItem(node)

        # Deserialize as graph -----------------------------------------------------------------------------------------
        self.graph.deserialize(data)

        # Bring the scene up to speed ----------------------------------------------------------------------------------
        for node in self.nodes:
            super().addItem(node)

        for edge in self.edges:
            super().addItem(edge)
