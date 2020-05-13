"""A collection of widgets that are used to represent the signal editing experience in NFB studio.
SchemeEditor is the main widget that contains the node toolbox as well as the scheme. The node module contains all the
classes related to the graphical node.
"""
from .editor import SchemeEditor
from .toolbox import Toolbox
from .scheme import Scheme

from .node import Node, Edge, Connection, Input, Output, DataType, Message, InfoMessage, WarningMessage, ErrorMessage

from .palette import Palette
from .style import Style
