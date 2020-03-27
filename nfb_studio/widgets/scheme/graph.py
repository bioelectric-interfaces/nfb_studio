"""Classes representing the graph stucture in the signal scheme."""
from typing import Union
from itertools import filterfalse
from collections import MutableSet

from PySide2.QtCore import QRectF

from .node import Node
from .edge import Edge
from .connection import Input, Output
from ..graphics_item_group import GraphicsItemGroup


class Graph(GraphicsItemGroup):
    """A collection of nodes and edges connecting them."""
    def __init__(self):
        super().__init__()

        self.nodes = set()
        self.edges = set()

    # Core set methods =================================================================================================
    def add(self, item):
        if isinstance(item, Node):
            self.nodes.add(item)
        elif isinstance(item, Edge):
            self.edges.add(item)
        else:
            raise TypeError("Graph accepts only Node and Edge objects, not " + type(item).__name__)

        super().add(item)
    
    def discard(self, item):
        super().discard(item)
        
        if isinstance(item, Node):
            # If a node is removed, all edges to or from that node are also removed.
            # Remove connected edges
            to_remove = []
            for edge in self.edges:
                if edge.sourceNode() == item or edge.targetNode() == item:
                    to_remove.append(edge)
            
            for edge in to_remove:
                self.discard(edge)

            # Remove the node
            self.nodes.discard(item)
        elif isinstance(item, Edge):
            # Disconnect from nodes that are still in this graph
            item.detachAll()
            self.edges.discard(item)
    
    # Edge manipulation ================================================================================================
    def connect_nodes(self, source: Output, target: Input) -> Edge:
        """Connect an Output connection to an Input connection with an edge.
        
        Returns the newly created edge.
        """
        edge = Edge()
        edge.setSource(source)
        edge.setTarget(target)

        self.add(edge)
        return edge

    def disconnect_nodes(self, source: Output, target: Input) -> Union[Edge, None]:
        """Remove a connection between a node output and an input.
        
        If output and input are connected more than once, only one edge is removed.
        Returns the edge that was removed, or None if no such edge was found.
        """
        for edge in self.edges:
            if edge.source() == source and edge.target() == target:
                self.discard(edge)
                return edge
        return None

    # Selection ========================================================================================================
    def selectAll(self):
        """Select the whole graph."""
        for node in self.nodes:
            node.setSelected(True)

    def selection(self):
        """Return a Graph containing all selected nodes and edges.
        
        This selection is equivalent to the highlighted items the user sees on screen. This means that it is possible
        that the resulting graph will contain only edges and no nodes.
        """
        result = Graph()

        for item in self:
            if item.isSelected():
                result.add(item)

        return result
    
    def clipboardSelection(self):
        """Return a Graph containing all selected nodes and edges, suitable for copying to clipboard.
        
        This selection is similar to `self.selection()` in that it only contains nodes and edges highlighted to the
        user. The difference is that if the user selected only edges, this is considered unsuitable for copying and an
        empty graph is returned instead.
        """
        result = self.selection()

        if len(result.nodes) == 0:
            return Graph()

        return result

    def wideSelection(self):
        """Return a graph snapshot containing all selected nodes and all connected edges.
        
        Unlike `self.selection()`, this method also gets all edges where at least one end is a selected node.  
        This snapshot is equivalent to the items that are deleted when a selection is removed or cut.
        """
        result = self.selection()

        for edge in self.edges:
            if ((edge.sourceNode() is not None and self.sourceNode().isSelected()) or 
                (edge.targetNode() is not None and self.targetNode().isSelected())):
                result.add(edge)  

        return result
    
    def extract(self, other):
        """Extract other graph from this graph.
        
        After calling this function, self.isdisjoint(other) will return True. All edges that become dangling from node
        removal are also removed.
        """
        for edge in other.edges:
            self.discard(edge)

        for node in other.nodes:
            self.discard(node)

    def merge(self, other):
        """Merge other graph into this graph.
        
        After calling this function, other.issubset(self) will return True.
        """
        super().__ior__(other)
        self.nodes |= other.nodes
        self.edges |= other.edges

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
    
    def deserialize(self, data: dict):
        """Deserialize this object from a dict of data.
        
        Edges are not serialized as objects. Instead, only their connections are remembered and reconstructed during the
        deserialization.
        """
        self.clear()

        # Deserialize nodes --------------------------------------------------------------------------------------------
        for node in data["nodes"]:
            self.add(node)

        # Deserialize edges --------------------------------------------------------------------------------------------
        for edge_data in data["edges"]:
            source_node = data["nodes"][edge_data["source"]["node_index"]]
            target_node = data["nodes"][edge_data["target"]["node_index"]]

            source = source_node.outputs[edge_data["source"]["connection_index"]]
            target = target_node.inputs[edge_data["target"]["connection_index"]]

            self.connect_nodes(source, target)
