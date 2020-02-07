from Qt.QtCore import Qt
from Qt.QtGui import QPainter
from Qt.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem

from .node import Node
from .edge import Edge
from .connection import Input, Output


class Scheme(QGraphicsScene):
    def __init__(self, parent=None):
        """A data model for the nfb experiment's system of signals and their components.

        This graph holds two sets: a set of nodes and a set of edges.
        Intended to use inside the scheme.

        See Also
        --------
        Node
        Edge
        """
        super().__init__(parent)

        self.nodes = set()
        self.edges = set()

    def addItem(self, item: QGraphicsItem):
        """Add an item to the scene.

        An override of QGraphicsScene.addItem method that detects when a node or edge was added.
        """
        super().addItem(item)

        if isinstance(item, Node):
            self.nodes.add(item)

        if isinstance(item, Edge):
            # Check that this edge is valid, that is both its source and target are in the scene (if they exist)
            if (item.source_node() is None or item.source_node() in self.nodes) and \
               (item.target_node() is None or item.target_node() in self.nodes):
                # Ensure that the connections know about this edge
                item.source().edges.add(item)
                item.target().edges.add(item)

                self.edges.add(item)

    def removeItem(self, item):
        """Add an item to the scene.

        An override of QGraphicsScene.removeItem method that detects when a node or edge was removed.
        """
        super().removeItem(item)

        if isinstance(item, Node):
            self.nodes.remove(item)

            # If a node is removed, all edges incoming and outgoing are removed too
            for edge in self.edges:
                if edge.source_node() == item or edge.target_node() == item:
                    self.removeItem(edge)

        if isinstance(item, Edge):
            self.edges.remove(item)

            item.source().edges.remove(item)
            item.target().edges.remove(item)

    def connect_nodes(self, source: Output, target: Input):
        edge = Edge()

        edge.setSource(source)
        edge.setTarget(target)

        source.edges.add(edge)
        target.edges.add(edge)

        self.addItem(edge)
        return edge

    def disconnect_nodes(self, source: Output, target: Input):
        for edge in self.edges:
            if edge.source() == source and edge.target() == target:
                self.removeItem(edge)
                break

    def getView(self) -> QGraphicsView:
        """Generate and return a new QGraphicsView, configured for optimal viewing."""
        v = QGraphicsView(self)
        v.setDragMode(QGraphicsView.RubberBandDrag)
        v.setRubberBandSelectionMode(Qt.ContainsItemShape)
        v.setRenderHint(QPainter.Antialiasing)
        v.setRenderHint(QPainter.SmoothPixmapTransform)

        return v

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

    def deserialize(self, data: dict):
        # Clear --------------------------------------------------------------------------------------------------------
        for node in self.nodes:
            self.removeItem(node)

        # Deserialize nodes --------------------------------------------------------------------------------------------
        for node in data["nodes"]:
            self.addItem(node)
            print(node.outputs)

        # Deserialize edges --------------------------------------------------------------------------------------------
        for edge_data in data["edges"]:
            source_node = data["nodes"][edge_data["source"]["node_index"]]
            target_node = data["nodes"][edge_data["target"]["node_index"]]

            source = source_node.outputs[edge_data["source"]["connection_index"]]
            target = target_node.inputs[edge_data["target"]["connection_index"]]

            self.connect_nodes(source, target)
