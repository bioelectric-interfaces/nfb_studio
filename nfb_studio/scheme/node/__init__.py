"""Submodule of scheme containing all classes related to nodes, such as Node, Connection, Edge, etc."""
from .connection import Connection, Input, Output, DataType
from .node import Node
from .edge import Edge
from .message import Message, InfoMessage, WarningMessage, ErrorMessage