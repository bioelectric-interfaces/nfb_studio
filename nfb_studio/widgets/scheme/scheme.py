"""A data model for the nfb experiment's system of signals and their components."""
from PySide2.QtCore import Qt, QPointF, QMimeData, Signal
from PySide2.QtGui import QPainter, QKeySequence
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QShortcut, QApplication

from nfb_studio.serial import mime, hooks

from .graph import Graph
from .node import Node, Edge, Input, Output, Connection
from .style import Style
from .palette import Palette

class Scheme(QGraphicsScene):
    """A data model for the nfb experiment's system of signals and their components.

    This class is a combination of three things:
    - nfb_studio.widgets.scheme.Graph: a graph of nodes and edges;
    - QGraphicsScene (inherits): a Qt representation of that graph and additional items;
    - QGraphicsView: a view of QGraphicsScene. Only one view is allowed - creating multiple views will make the program
    behave incorrectly.

    The main components are available as self.graph, super() and self.view().

    See Also
    --------
    nfb_studio.widgets.scheme.Node : Graph node.
    nfb_studio.widgets.scheme.Edge : Graph edge.
    nfb_studio.widgets.scheme.Graph : A collection of nodes and edges.
    """
    class View(QGraphicsView):
        """Custom view widget for Scheme."""

        configRequested = Signal(object)
        """Emitted when a config of a node was requested. Sends the node."""

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
            #self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        def setScene(self, scene):
            if not isinstance(scene, Scheme):
                raise TypeError("Scheme.View can only have Scheme as it's scene, not " + type(scene).__name__)

            super().setScene(scene)
            cut_shortcut = QShortcut(QKeySequence.Cut, self)
            cut_shortcut.activated.connect(scene.cutEvent)

            copy_shortcut = QShortcut(QKeySequence.Copy, self)
            copy_shortcut.activated.connect(scene.copyEvent)

            paste_shortcut = QShortcut(QKeySequence.Paste, self)
            paste_shortcut.activated.connect(scene.pasteEvent)

            delete_shortcut = QShortcut(QKeySequence.Delete, self)
            delete_shortcut.activated.connect(scene.deleteEvent)
        
        def setScheme(self, scheme):
            """Alias function for setScene."""
            self.setScene(scheme)


    ClipboardMimeType = "application/x-nfb_studio-graph"

    def __init__(self, parent=None):
        """Constructs a Scheme with an optional `parent` parameter that is passed to the super()."""
        super().__init__(parent)
        self.graph = Graph()

        self._view = None

        self._custom_drop_events = {}
        """A dict mapping MIME types to custom functions to be executed when drag and drop operation finishes.  
        Users of this scheme can set their own drop event for a particular MIME type. MIME types that are present in
        this dict will always be accepted drags.
        """

        # Drag-drawing edges support -----------------------------------------------------------------------------------
        self._dragging_edge = None
        """A temporary edge that is being displayed when an edge is drawn by the user with drag and drop."""

        # Clipboard support --------------------------------------------------------------------------------------------
        self.paste_pos = QPointF()
        """Position where the center of the pasted object will be located."""

        # Style and palette --------------------------------------------------------------------------------------------
        self._style = Style()
        self._palette = Palette()

        self.styleChange()
        self.paletteChange()

    # Viewing ==========================================================================================================
    def view(self):
        """Return a Scheme.View, suitable for displaying contents of the scheme.
        Note that only one view can exist for a given scheme. This function will construct the widget when it's first
        called, and always return this widget.
        """
        if self._view is None:
            self._view = self.View()
            self._view.setScene(self)

        return self._view

    # Element manipulation =============================================================================================
    def addItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of super().addItem method that detects when a node or edge was added.
        """
        self.graph.add(item)
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
        
        self.graph.remove(item)

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

    def extract(self, other: Graph):
        """Update the scheme, removing elements from a graph.
        
        `other` represents a subgraph of the scheme graph that is to be extracted.
        """
        for edge in other.edges:
            self.removeItem(edge)

        for node in other.nodes:
            self.removeItem(node)

    def merge(self, other: Graph):
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

    # Selection ========================================================================================================
    def selectAll(self):
        self.graph.selectAll()

    def selection(self) -> Graph:
        return self.graph.selection()
    
    def clipboardSelection(self) -> Graph:
        return self.graph.clipboardSelection()
    
    def wideSelection(self) -> Graph:
        return self.graph.wideSelection()

    # User actions =====================================================================================================
    def cutEvent(self):
        """Cut the selected graph and place it in the clipboard."""
        self.copyEvent()
        self.deleteEvent()

    def copyEvent(self):
        """Copy the selected graph and place it in the clipboard."""
        graph = self.clipboardSelection()
        if len(graph.nodes) == 0:  # Nothing to copy
            return

        self.paste_pos = graph.boundingRect().center()
        self.advancePastePos()

        package = QMimeData()
        mime.dump(graph, package, self.ClipboardMimeType, hooks=hooks.qt)

        clipboard = QApplication.clipboard()
        clipboard.setMimeData(package)

    def pasteEvent(self):
        """Retrieve the data from a clipboard and paste it."""
        clipboard = QApplication.clipboard()
        package = clipboard.mimeData()

        if package.hasFormat(self.ClipboardMimeType):
            graph = mime.load(package, self.ClipboardMimeType, hooks=hooks.qt)
            self.merge(graph)

            self.clearSelection()  # Clear old selection
            graph.selectAll()  # Create new selection (pasted items)

            graph.moveCenter(self.paste_pos)
            self.advancePastePos()

    def deleteEvent(self):
        """Delete the selection."""
        self.extract(self.selection())

    def advancePastePos(self):
        """Move the paste position (usually down and to the right).  
        This function is usually called when an object has been pasted.
        """
        offset = self.schemeStyle().pixelMetric(Style.PasteOffset)
        self.paste_pos += QPointF(offset, offset)

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
        Cleans up by removing the fake edge. This function is called regardless of whether edge drag resulted in a
        successful connection.
        """
        super().removeItem(self._dragging_edge)

        self._dragging_edge.detachAll()
        self._dragging_edge = None

    def dragEnterEvent(self, event):
        package = event.mimeData()

        # Form a list of accepted formats. Accepted formats include all format with custom drop functions, as well as
        # Connection.EdgeDragMimeType
        accepted_formats = (
            list(self._custom_drop_events.keys()) + 
            [Connection.EdgeDragMimeType]
        )
        
        # If any of the accepted_formats is present in package.formats(), accept the event.
        for fmt in package.formats():
            if fmt in accepted_formats:
                event.accept()
                break
    
    def dropEvent(self, event):
        package = event.mimeData()

        for fmt, drop_event in self._custom_drop_events.items():
            if package.hasFormat(fmt):
                drop_event(scheme=self, event=event)

        super().dropEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(Connection.EdgeDragMimeType) and self.hasEdgeDrag():
            # Update edge position, but otherwise do the default thing.
            super().dragMoveEvent(event)  
            if self._dragging_edge.source() is None:
                self._dragging_edge.setSourcePos(event.scenePos())
            else:
                self._dragging_edge.setTargetPos(event.scenePos())

    def setCustomDropEvent(self, fmt, event):
        """Set a custom drop event for a particular MIME type (format).
        Setting a custom event for a format will make this format get accepted by the scheme during drag and drop.
        If event is None, the format is instead removed from the list of accepted formats.
        If not None, event should be a function accepting two keyword arguments:
        - scheme, which will contain this scheme
        - event, which will contain the event that is being dropped
        """
        if event is None:
            self._custom_drop_events.pop(fmt)
        else:
            self._custom_drop_events[fmt] = event

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

    @classmethod
    def deserialize(cls, data: dict):
        """Deserialize this object from a dict of data."""
        obj = cls()

        # Deserialize the graph ----------------------------------------------------------------------------------------
        obj.graph = Graph.deserialize(data)

        # Bring the scene up to speed ----------------------------------------------------------------------------------
        for node in obj.graph.nodes:
            super(Scheme, obj).addItem(node)

        for edge in obj.graph.edges:
            super(Scheme, obj).addItem(edge)
        
        return obj
