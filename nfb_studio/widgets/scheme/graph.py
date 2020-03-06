"""Classes representing the graph stucture in the signal scheme."""
from typing import Union

from PySide2.QtCore import QRectF

from .node import Node
from .edge import Edge
from .connection import Input, Output


class AbstractGraph:
    """An abstract (not supposed to be created) base class for Graph and GraphSnapshot.
    
    Both Graph and GraphSnapshot contain two members - `self.nodes` and `self.edges`. In Graph those are sets, in
    GraphSnapshot - frozensets.
    """
    def __init__(self):
        self.nodes = None  # Defined in implementations
        self.edges = None  # Defined in implementations

    # Selection ========================================================================================================
    def selectAll(self):
        """Select the whole graph."""
        for node in self.nodes:
            node.setSelected(True)

    def selection(self):
        """Return a GraphSnapshot containing all selected nodes and edges.
        
        This selection is equivalent to the highlighted items the user sees on screen. This means that it is possible
        that the resulting GraphSnapshot will contain only edges and no nodes.
        """
        result = GraphSnapshot()

        selected_nodes = [node for node in self.nodes if node.isSelected()]
        selected_edges = [edge for edge in self.edges if edge.isSelected()]

        result.nodes = frozenset(selected_nodes)
        result.edges = frozenset(selected_edges)

        return result
    
    def clipboardSelection(self):
        """Return a GraphSnapshot containing all selected nodes and edges, suitable for copying to clipboard.
        
        This selection is similar to `self.selection()` in that it only contains nodes and edges highlighted to the
        user. The difference is that if the user selected only edges, this is considered unsuitable for copying and an
        empty GraphSnapshot is returned instead.
        """
        result = GraphSnapshot()

        selected_nodes = [node for node in self.nodes if node.isSelected()]
        if len(selected_nodes) == 0:
            return result

        selected_edges = [edge for edge in self.edges if edge.isSelected()]

        result.nodes = frozenset(selected_nodes)
        result.edges = frozenset(selected_edges)

        return result


    def wideSelection(self):
        """Return a graph snapshot containing all selected nodes and all connected edges.
        
        Unlike `self.selection()`, this method also gets all edges where at least one end is a selected node.  
        This snapshot is equivalent to the items that are deleted when a selection is removed or cut.
        """
        result = GraphSnapshot()

        selected_nodes = [node for node in self.nodes if node.isSelected()]
        
        selected_edges = []
        for edge in self.edges:
            if ((edge.sourceNode() is not None and self.sourceNode().isSelected()) or 
                (edge.targetNode() is not None and self.targetNode().isSelected())):
                selected_edges.append(edge)  

        result.nodes = frozenset(selected_nodes)
        result.edges = frozenset(selected_edges)

        return result

    # Observer functions ===============================================================================================
    def findNode(self, node_id: int) -> Union[Node, None]:
        """Find and return a node that has the corresponding id.
        
        If no such node could be found, return None.
        """
        for node in self.nodes:
            if node_id == id(node):
                return node
        return None

    # Transformations ==================================================================================================
    def boundingRect(self) -> QRectF:
        """Return the combined bounding box of all the items in the graph."""
        result = QRectF()

        for node in self.nodes:
            result = result | node.boundingRect() | node.childrenBoundingRect()
        for edge in self.edge:
            result = result | edge.boundingRect() | edge.childrenBoundingRect()
        
        return result

    def moveBy(self, dx, dy):
        """Move all nodes by some offset."""
        for node in self.nodes:
            node.moveBy(dx, dy)

    # Utility functions ================================================================================================
    def __len__(self):
        """Size of the graph. Equal to len(self.nodes)."""
        return len(self.nodes)
    
    def __contains__(self, obj, /):
        """Check if the graph contains a node or an edge."""
        if isinstance(obj, Node):
            return obj in self.nodes
        elif isinstance(obj, Edge):
            return obj in self.edges
        return False
    
    def isdisjoint(self, other):
        """Return True if the graph has no elements in common with other.
        
        Dangling nodes are not considered valid parts of a graph. They can only exist as temporary objects.
        This means that if no nodes are shared, no edges can be shared. If nodes are shared, the graph is already not
        disjoint. For this reason edges are not checked.
        """
        return self.nodes.isdisjoint(other.nodes)

    def issubset(self, other):
        """Test whether every element in the set is in other."""
        return self.nodes.issubset(other.nodes) and self.edges.issubset(other.edges)
    
    def issuperset(self, other):
        """Test whether every element in other is in the set."""
        return other.issubset(self)

    # Serialization ====================================================================================================
    def serialize(self) -> dict:
        data = {}

        # Serialize nodes ----------------------------------------------------------------------------------------------
        nodes = list(self.nodes)
        data["nodes"] = nodes

        # Serialize edges ----------------------------------------------------------------------------------------------
        data["edges"] = []

        for edge in self.edges:
            source_node = edge.sourceNode()
            target_node = edge.targetNode()

            if source_node is None or target_node is None:
                # Not serializing dangling nodes
                continue

            edge_data = {
                "source": {
                    "node_index": nodes.index(source_node),
                    "connection_index": source_node.outputs.index(edge.source())
                },
                "target": {
                    "node_index": nodes.index(target_node),
                    "connection_index": target_node.inputs.index(edge.target())
                }
            }

            data["edges"].append(edge_data)

        return data


class Graph(AbstractGraph):
    """A collection of nodes and edges connecting them."""

    def __init__(self):
        super().__init__()

        self.nodes = set()
        self.edges = set()

    def addNode(self, node: Node):
        """Add a new node to this graph."""
        self.nodes.add(node)

    def addEdge(self, edge: Edge):
        """Add a new edge to this graph.
        
        The both source and target nodes of this edge must already be present in the graph. Otherwise, ValueError is
        raised.
        """
        # Check that this edge is valid, that is both its source and target are in the scene (if they exist)
        if (edge.sourceNode() is None or edge.sourceNode() in self.nodes) and \
           (edge.targetNode() is None or edge.targetNode() in self.nodes):

            self.edges.add(edge)
        else:
            raise ValueError("one of edge's connections is not in this graph")

    def removeNode(self, node: Node):
        """Remove a node from this graph.
        
        If a node is removed, all edges to or from that node are also removed.
        """
        # Remove connected edges
        to_remove = []
        for edge in self.edges:
            if edge.sourceNode() == node or edge.targetNode() == node:
                to_remove.append(edge)
        
        for edge in to_remove:
            self.removeEdge(edge)

        # Remove the node
        self.nodes.remove(node)

    def removeEdge(self, edge: Edge):
        """Remove an edge from this graph."""
        self.edges.remove(edge)
        edge.detachAll()  # Disconnect from nodes that are still in this graph

    def connect_nodes(self, source: Output, target: Input) -> Edge:
        """Connect an Output connection to an Input connection with an edge.
        
        Returns the newly created edge.
        """
        edge = Edge()
        edge.setSource(source)
        edge.setTarget(target)

        self.addEdge(edge)
        return edge

    def disconnect_nodes(self, source: Output, target: Input) -> Union[Edge, None]:
        """Remove a connection between a node output and an input.
        
        If output and input are connected more than once, only one edge is removed.
        Returns the edge that was removed, or None if no such edge was found.
        """
        for edge in self.edges:
            if edge.source() == source and edge.target() == target:
                self.removeEdge(edge)
                return edge
        return None

    # def serialize(self) -> dict  # Inherited from AbstractGraph

    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data.
        
        Edges are not serialized as objects. Instead, only their connections are remembered and reconstructed during the
        deserialization.
        """
        self.clear()

        # Deserialize nodes --------------------------------------------------------------------------------------------
        for node in data["nodes"]:
            self.addNode(node)

        # Deserialize edges --------------------------------------------------------------------------------------------
        for edge_data in data["edges"]:
            source_node = data["nodes"][edge_data["source"]["node_index"]]
            target_node = data["nodes"][edge_data["target"]["node_index"]]

            source = source_node.outputs[edge_data["source"]["connection_index"]]
            target = target_node.inputs[edge_data["target"]["connection_index"]]

            self.connect_nodes(source, target)
    
    def extract(self, other: AbstractGraph):
        """Extract other graph from this graph.
        
        After calling this function, self.isdisjoint(other) will return True. All edges that become dangling from node
        removal are also removed.
        """
        for edge in other.edges:
            self.removeItem(edge)

        for node in other.nodes:
            self.removeNode(node)

    def merge(self, other: AbstractGraph):
        """Merge other graph into this graph.
        
        After calling this function, other.issubset(self) will return True.
        """
        self.nodes.update(other.nodes)
        self.edges.update(other.edges)
    
    def clear(self):
        for node in self.nodes:
            self.removeNode(node)


class GraphSnapshot(AbstractGraph):
    """A static reference to a part of a graph. Contains a frozenset of nodes and a frozenset of edges.

    A snapshot is not meant to be edited.
    """
    def __init__(self, nodes=None, edges=None):
        super().__init__()

        self.nodes = nodes or frozenset()
        self.edges = edges or frozenset()

    # def serialize(self) -> dict  # Inherited from AbstractGraph

    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data.
        
        This functions deserializes by loading data into a mutable Graph, then freezing it in a frozenset.
        """
        g = Graph()
        g.deserialize(data)

        self.nodes = frozenset(g.nodes)
        self.edges = frozenset(g.edges)
