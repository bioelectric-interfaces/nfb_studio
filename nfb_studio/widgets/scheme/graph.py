from .node import Node
from .edge import Edge
from .connection import Input, Output


class Graph:
    def __init__(self):
        """A collection of nodes and edges connecting them.
        This graph holds two sets: a set of nodes and a set of edges.
        Intended to use inside the scheme.

        See Also
        --------
        Node
        Edge
        """
        self.nodes = set()
        self.edges = set()

    def addNode(self, node: Node):
        """Add a node to the graph."""
        self.nodes.add(node)

    def removeNode(self, node: Node):
        """Remove a node from the graph."""
        self.nodes.remove(node)

    def connect(self, source: Output, target: Input):
        edge = Edge()

        edge.setSource(source)
        edge.setTarget(target)

        source.edges.add(edge)
        target.edges.add(edge)

        self.edges.add(edge)

    def disconnect(self, source: Output, target: Input):
        for edge in self.edges:
            if edge.source() == source and edge.target() == target:
                self.edges.remove(edge)

                source.edges.remove(edge)
                target.edges.remove(edge)

                break

    def serialize(self) -> dict:
        data = {}

        # Serialize nodes ----------------------------------------------------------------------------------------------
        nodes = list(self.nodes)
        data["nodes"] = nodes

        # Serialize edges ----------------------------------------------------------------------------------------------
        data["edges"] = []

        for edge in self.edges:
            source_node = edge.source().parentItem()
            target_node = edge.target().parentItem()

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
        # Deserialize nodes --------------------------------------------------------------------------------------------
        nodes = data["nodes"]
        self.nodes = set(nodes)

        # Deserialize edges --------------------------------------------------------------------------------------------
        for edge_data in data["edges"]:
            source_node = nodes[edge_data["source"]["node_index"]]
            target_node = nodes[edge_data["target"]["node_index"]]

            source = source_node.outputs[edge_data["source"]["connection_index"]]
            target = target_node.inputs[edge_data["target"]["connection_index"]]

            self.connect(source, target)
