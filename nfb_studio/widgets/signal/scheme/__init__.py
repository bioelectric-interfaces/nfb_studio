"""A graph scheme as a Qt object that represents the dataflow diagram of signals in nfb_studio."""
from .scheme import Scheme

from .node import Node
from .edge import Edge
from .connection import Connection, Input, Output
from .message import Message, InfoMessage, WarningMessage, ErrorMessage
from .data_type import DataType

from .style import Style
from .palette import Palette