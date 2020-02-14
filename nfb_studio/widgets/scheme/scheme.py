"""A data model for the nfb experiment's system of signals and their components."""
from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QPainter, QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QShortcut, QApplication

from nfb_studio import StdMimeData

from .graph import Graph, GraphSnapshot
from .node import Node
from .edge import Edge
from .connection import Input, Output


class Scheme(Graph, QGraphicsScene):
    """A data model for the nfb experiment's system of signals and their components.

    This class is a combination of nfb_studio.widgets.scheme.Graph and a QGraphicsScene, which represents the node graph
    in a graphical scene that is then displayed by a QGraphicsView. To get a QGraphicsView that is pre-configured to
    display the contents correcly and has all the necessary shortcuts attached, use the `getView` method.        

    See Also
    --------
    nfb_studio.widgets.scheme.Node : Graph node.
    nfb_studio.widgets.scheme.Edge : Graph edge.
    nfb_studio.widgets.scheme.Graph : A collection of nodes and edges.
    """
    def __init__(self, parent=None):
        """Constructs a Scheme with an optional `parent` parameter that is passed to the QGraphicsScene."""
        Graph.__init__(self)
        QGraphicsScene.__init__(self, parent)

    # Element manipulation ---------------------------------------------------------------------------------------------
    def addItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of QGraphicsScene.addItem method that detects when a node or edge was added.
        """
        if isinstance(item, Node):
            Graph.addNode(self, item)
        elif isinstance(item, Edge):
            Graph.addEdge(self, item)

        QGraphicsScene.addItem(self, item)

    def removeItem(self, item):
        """Add an item to the scene.

        An override of QGraphicsScene.removeItem method that detects when a node or edge was removed.
        """
        QGraphicsScene.removeItem(self, item)

        if isinstance(item, Node):
            Graph.removeNode(self, item)

        if isinstance(item, Edge):
            Graph.removeEdge(self, item)

    def connect_nodes(self, source: Output, target: Input):
        """Connect an Output connection to an Input connection with an edge.
        
        Returns the newly created edge.
        """
        edge = Graph.connect_nodes(self, source, target)
        QGraphicsScene.addItem(self, edge)

        return edge

    def disconnect_nodes(self, source: Output, target: Input):
        """Remove a connection between a node output and an input.
        
        If output and input are connected more than once, only one edge is removed.
        Returns the edge that was removed, or None if no such edge was found.
        """
        edge = Graph.disconnect_nodes(self, source, target)
        if edge is not None:
            QGraphicsScene.removeItem(self, edge)
        return edge

    def merge(self, *others):
        """Update the scheme, adding elements other schemes."""
        Graph.merge(*others)

        for other in others:
            for node in other.nodes:
                QGraphicsScene.addItem(self, node)
            for edge in other.edges:
                QGraphicsScene.addItem(self, edge)

    def clear(self):
        """Clear the scheme."""
        QGraphicsScene.clear(self)
        Graph.clear(self)

    # Selection and clipboard ------------------------------------------------------------------------------------------
    def selectedGraph(self) -> GraphSnapshot:
        """Return the selected part of the dataflow graph as a GraphSnapshot."""
        result = GraphSnapshot()

        selected_nodes = [node for node in self.nodes if node.isSelected()]
        selected_edges = [edge for edge in self.edges if edge.isShadowSelected()]

        result.nodes = frozenset(selected_nodes)
        result.edges = frozenset(selected_edges)

        return result

    def copySelectedGraph(self):
        """Copies the selected graph and places it in the clipboard."""
        snapshot = self.selectedGraph()

        package = StdMimeData()
        package.setObject(snapshot)

        clipboard = QApplication.clipboard()
        clipboard.setMimeData(package)

    def paste(self):
        """Retrieves the data from a clipboard and pastes it."""
        clipboard = QApplication.clipboard()
        package = clipboard.mimeData()

        if package.hasObject(GraphSnapshot):
            snapshot = package.objectData(GraphSnapshot)

            self.clearSelection()
            for node in snapshot.nodes:
                node.setSelected(True)
                node.setPosition(node.position() + QPointF(0.5, 0.5))
            
            self.merge(snapshot)

    # Widgets ----------------------------------------------------------------------------------------------------------
    def getView(self) -> QGraphicsView:
        """Generate and return a new QGraphicsView, configured for optimal viewing."""
        v = QGraphicsView(self)
        v.setDragMode(QGraphicsView.RubberBandDrag)
        v.setRubberBandSelectionMode(Qt.ContainsItemShape)
        v.setRenderHint(QPainter.Antialiasing)
        v.setRenderHint(QPainter.SmoothPixmapTransform)

        copy_shortcut = QShortcut(QKeySequence.Copy, v)
        copy_shortcut.activated.connect(self.copySelectedGraph)

        paste_shortcut = QShortcut(QKeySequence.Paste, v)
        paste_shortcut.activated.connect(self.paste)

        return v

    # Serialization ----------------------------------------------------------------------------------------------------
    # def serialize(self) -> dict: Inherited from Graph

    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data."""
        # Clear --------------------------------------------------------------------------------------------------------
        for node in self.nodes:
            self.removeItem(node)

        # Deserialize as graph -----------------------------------------------------------------------------------------
        Graph.deserialize(self, data)

        # Bring the scene up to speed ----------------------------------------------------------------------------------
        for node in self.nodes:
            QGraphicsScene.addItem(self, node)

        for edge in self.edges:
            QGraphicsScene.addItem(self, edge)
