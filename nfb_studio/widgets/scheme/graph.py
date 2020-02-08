from .node import Node
from .edge import Edge
from .connection import Input, Output


class AbstractGraphBase:
    """An abstract (not supposed to be created) base class for Graph and GraphSnapshot."""
    def __init__(self):
        self.nodes = None  # Defined in implementations
        self.edges = None  # Defined in implementations

    def serialize(self) -> dict:
        data = {}

        # Serialize nodes ----------------------------------------------------------------------------------------------
        nodes = list(self.nodes)
        data["nodes"] = nodes

        # Serialize edges ----------------------------------------------------------------------------------------------
        data["edges"] = []

        for edge in self.edges:
            source_node = edge.source_node()
            target_node = edge.target_node()

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


class Graph(AbstractGraphBase):
    def __init__(self):
        super().__init__()

        self.nodes = set()
        self.edges = set()

    def addNode(self, node: Node):
        self.nodes.add(node)

    def addEdge(self, edge: Edge):
        # Check that this edge is valid, that is both its source and target are in the scene (if they exist)
        if (edge.source_node() is None or edge.source_node() in self.nodes) and \
           (edge.target_node() is None or edge.target_node() in self.nodes):
            # Ensure that the connections know about this edge
            edge.source().edges.add(edge)
            edge.target().edges.add(edge)

            self.edges.add(edge)
        else:
            raise ValueError("one of edge's connections is not in this graph")

    def removeNode(self, node: Node):
        self.nodes.remove(node)

        # If a node is removed, all edges incoming and outgoing are removed too
        for edge in self.edges:
            if edge.source_node() == node or edge.target_node() == node:
                self.removeEdge(edge)

    def removeEdge(self, edge: Edge):
        self.edges.remove(edge)

        edge.source().edges.remove(edge)
        edge.target().edges.remove(edge)

    def connect_nodes(self, source: Output, target: Input):
        edge = Edge()

        edge.setSource(source)
        edge.setTarget(target)

        source.edges.add(edge)
        target.edges.add(edge)

        self.addEdge(edge)
        return edge

    def disconnect_nodes(self, source: Output, target: Input):
        for edge in self.edges:
            if edge.source() == source and edge.target() == target:
                self.removeEdge(edge)
                return edge
        return None

    def deserialize(self, data: dict):
        # Clear --------------------------------------------------------------------------------------------------------
        for node in self.nodes:
            self.removeNode(node)

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


class GraphSnapshot(AbstractGraphBase):
    def __init__(self, nodes=None, edges=None):
        """A static reference to a part of a graph. Contains a frozenset of nodes and a frozenset of edges.

        A snapshot is not meant to be edited.
        """
        super().__init__()

        self.nodes = nodes or frozenset()
        self.edges = edges or frozenset()

    def deserialize(self, data: dict):
        # Temporarily deserialize to a mutable Graph, then freeze the data
        g = Graph()
        g.deserialize(data)

        self.nodes = frozenset(g.nodes)
        self.edges = frozenset(g.edges)
