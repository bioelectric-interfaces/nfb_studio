"""A data model for the nfb experiment's system of signals and their components."""
from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QPainter, QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QShortcut, QApplication

from nfb_studio import StdMimeData

from .graph import AbstractGraph, Graph, GraphSnapshot
from .node import Node
from .edge import Edge
from .connection import Input, Output
from .style import Style
from .palette import Palette


class Scheme(QGraphicsScene):
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
        """Constructs a Scheme with an optional `parent` parameter that is passed to the super()."""
        super().__init__(parent)
        self._graph = Graph()

        self._style = Style()
        self._palette = Palette()

        self.schemeStyleChange()
        self.schemePaletteChange()

    # Element manipulation =============================================================================================
    def addItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of super().addItem method that detects when a node or edge was added.
        """
        if isinstance(item, Node):
            self._graph.addNode(item)
        elif isinstance(item, Edge):
            self._graph.addEdge(item)
        else:
            raise TypeError("unrecognised graphics item of type " + type(item).__name__)

        super().addItem(item)

    def removeItem(self, item):
        """Add an item to the scene.

        An override of super().removeItem method that detects when a node or edge was removed.
        """
        # Remove a Node ------------------------------------------------------------------------------------------------
        if isinstance(item, Node):
            # Remove connected edges first
            to_remove = []
            for edge in self._graph.edges:
                if edge.source_node() == item or edge.target_node() == item:
                    to_remove.append(edge)
            
            for edge in to_remove:
                self.removeItem(edge)

            # Remove the node
            self._graph.removeNode(item)
        # Remove an Edge -----------------------------------------------------------------------------------------------
        elif isinstance(item, Edge):
            self._graph.removeEdge(item)
        # Unknown item -------------------------------------------------------------------------------------------------
        else:
            raise TypeError("unrecognised graphics item of type " + type(item).__name__)

        super().removeItem(item)

    def connect_nodes(self, source: Output, target: Input):
        """Connect an Output connection to an Input connection with an edge.
        
        Returns the newly created edge.
        """
        edge = self._graph.connect_nodes(source, target)
        super().addItem(edge)

        return edge

    def disconnect_nodes(self, source: Output, target: Input):
        """Remove a connection between a node output and an input.
        
        If output and input are connected more than once, only one edge is removed.
        Returns the edge that was removed, or None if no such edge was found.
        """
        edge = self._graph.disconnect_nodes(source, target)
        if edge is not None:
            super().removeItem(edge)
        return edge

    def extract(self, other: AbstractGraph):
        """Update the scheme, removing elements from a graph.
        
        `other` represents a subgraph of the scheme graph that is to be extracted.
        """
        for node in other.nodes:
            self.removeItem(node)

    def merge(self, other: AbstractGraph):
        """Update the scheme, adding elements from a graph."""
        self._graph.merge(other)

        for node in other.nodes:
            super().addItem(node)
        for edge in other.edges:
            super().addItem(edge)

    def clear(self):
        """Clear the scheme."""
        super().clear()
        self._graph.clear()

    # Selection ========================================================================================================
    def selectAll(self):
        self._graph.selectAll()

    def selection(self) -> GraphSnapshot:
        return self._graph.selection()
    
    def wideSelection(self) -> GraphSnapshot:
        return self._graph.wideSelection()

    # User actions =====================================================================================================
    def cutEvent(self):
        """Cut the selected graph and place it in the clipboard."""
        self.copyEvent()
        self.deleteEvent()

    def copyEvent(self):
        """Copy the selected graph and place it in the clipboard."""
        snapshot = self.selection()

        package = StdMimeData()
        package.setObject(snapshot)

        clipboard = QApplication.clipboard()
        clipboard.setMimeData(package)

    def pasteEvent(self):
        """Retrieve the data from a clipboard and paste it."""
        clipboard = QApplication.clipboard()
        package = clipboard.mimeData()

        if package.hasObject(GraphSnapshot):
            snapshot = package.objectData(GraphSnapshot)

            self.clearSelection()  # Clear old selection

            snapshot.selectAll()  # Create new selection (pasted items)

            offset = self.schemeStyle().pixelMetric(Style.PasteOffset)
            snapshot.moveBy(offset, offset)  # Move all items by some offset 
            
            self.merge(snapshot)

            self.copyEvent()  # Copy the selection again (nothing changes except for the item offset)

    def deleteEvent(self):
        """Delete the selection."""
        self.extract(self.selection())

    # Style and palette ================================================================================================
    def schemeStyleChange(self):
        pass

    def schemePaletteChange(self):
        self.setBackgroundBrush(self.schemePalette().background())

    def schemeStyle(self):
        return self._style

    def setSchemeStyle(self, style):
        self._style = style
        self.schemeStyleChange()

    def schemePalette(self):
        return self._palette
    
    def setSchemePalette(self, palette):
        self._palette = palette
        self.schemePaletteChange()

    # Widgets ==========================================================================================================
    def getView(self) -> QGraphicsView:
        """Generate and return a new QGraphicsView, configured for optimal viewing."""
        v = QGraphicsView(self)
        v.setDragMode(QGraphicsView.RubberBandDrag)
        v.setRubberBandSelectionMode(Qt.ContainsItemShape)
        v.setRenderHint(QPainter.Antialiasing)
        v.setRenderHint(QPainter.SmoothPixmapTransform)

        cut_shortcut = QShortcut(QKeySequence.Cut, v)
        cut_shortcut.activated.connect(self.cutEvent)

        copy_shortcut = QShortcut(QKeySequence.Copy, v)
        copy_shortcut.activated.connect(self.copyEvent)

        paste_shortcut = QShortcut(QKeySequence.Paste, v)
        paste_shortcut.activated.connect(self.pasteEvent)

        delete_shortcut = QShortcut(QKeySequence.Delete, v)
        delete_shortcut.activated.connect(self.deleteEvent)

        return v

    # Serialization ====================================================================================================
    # def serialize(self) -> dict: Inherited from Graph

    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data."""
        # Clear --------------------------------------------------------------------------------------------------------
        for node in self.nodes:
            self.removeItem(node)

        # Deserialize as graph -----------------------------------------------------------------------------------------
        self._graph.deserialize(data)

        # Bring the scene up to speed ----------------------------------------------------------------------------------
        for node in self.nodes:
            super().addItem(node)

        for edge in self.edges:
            super().addItem(edge)
