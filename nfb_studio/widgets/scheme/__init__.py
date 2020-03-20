"""A graph scheme as a Qt object that represents the dataflow diagram of signals in nfb_studio."""
from .scheme import Scheme

from .node import Node
from .edge import Edge
from .connection import Input, Output
from .message import InfoMessage, WarningMessage, ErrorMessage

from .toolbox import Toolbox

from .style import Style
from .palette import Palette