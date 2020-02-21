"""A collection of properties for drawing scheme items."""
from enum import Enum, auto

from PySide2.QtCore import Qt
from PySide2.QtGui import QPen, QFont

from nfb_studio.gui import inches_to_pixels as px
from nfb_studio.util import import_enum

from .palette import Palette


class Style:
    """A collection of sizes and fonts, as well as a default palette that is used to draw the items in the scheme."""

    class SizeMetric(Enum):
        """Various available size metrics.
        
        A size metric is a style dependent size represented by a single value. This enum contains a set of "keys", that
        can be used as arguments in `Style.inchMetric()` or `Style.pixelMetric()` to get the corresponding 
        values.
        """

        NodeFrameCornerRadius = 0
        """Rounded rectangle corner radius."""
        NodeFrameTextPadding = auto()
        """Padding for text inside the node body."""
        NodeDividerTextMargin = auto()
        """Margin between text and the title/description divider."""
        NodeMessagePadding = auto()
        """Padding between messages below the node."""
        NodeConnectionPadding = auto()
        """Padding between connections."""
        NodeFrameWidth = auto()
        """Width of the rounded rectangle frame."""
        NodeWidth = auto()
        """Body width."""
        
        EdgeWidth = 20
        """Width of the curved line. Also width of the connection stem."""
        EdgeBezierPointOffset = auto()
        """Max horizontal offset of control points on a bezier curve compared to its endpoints."""
        EdgeBezierCloseDistance = auto()
        """Distance that's considered "too close" by the bezier curve calculation algorithm. If distance between source 
        and target is less that this variable, control points are moved closer together.
        """

        ConnectionStemLength = 40
        """Length of the line going out of the node body."""
        ConnectionTextLength = auto()
        """Horizontal length of the box in which the text is drawn."""
        ConnectionStemTextMargin = auto()
        """Margin between the end of the stem and the node's description."""

        MessageIconSize = 60
        """Size of the icon (width and height). The icon is expected to be square."""
        MessageTextLength = auto()
        """Horizontal length of the box in which the text is drawn."""
        MessageIconTextMargin = auto()
        """Margin between the icon and the message's text."""

        PasteOffset = 80
        """Amount by which the selection should be shifted when pasted from clipboard."""

    class Font(Enum):
        """Various fonts used in the scheme items.
        
        This enum contains a set of "keys", that can be used as arguments in `Style.font()` to get 
        the corresponding values.
        """
        Default = 0
        """Default font for non-specific purposes."""

        NodeTitle = auto()
        """Font used in the node's title."""
        NodeDescription = auto()
        """Font used in the node's description."""
        ConnectionText = auto()
        """Font used in the connection's description."""
        MessageText = auto()
        """Font used in the message's text."""

    def __init__(self):
        """Constructs a Style."""
        SM = self.SizeMetric
        FT = self.Font

        self._inch_metric = {
            SM.NodeFrameCornerRadius: 0.1,
            SM.NodeFrameTextPadding: 0.1,
            SM.NodeDividerTextMargin: 0.05,
            SM.NodeMessagePadding: 0.05,
            SM.NodeConnectionPadding: 0.15,
            SM.NodeFrameWidth: 0.02,
            SM.NodeWidth: 2,
            
            SM.EdgeWidth: 0.02,
            SM.EdgeBezierPointOffset: 0.8,
            SM.EdgeBezierCloseDistance: 1.5,

            SM.ConnectionStemLength: 0.2,
            SM.ConnectionTextLength: 1.5,
            SM.ConnectionStemTextMargin: 0.05,

            SM.MessageIconSize: 0.16,
            SM.MessageTextLength: 2.5,
            SM.MessageIconTextMargin: 0.05,

            SM.PasteOffset: 0.5
        }

        default_font = QFont("Segoe UI")
        default_font.setPointSizeF(10.5)

        title_font = QFont("Segoe UI Semibold")
        title_font.setPointSizeF(10.5)

        self._font = {
            FT.Default: default_font,
            FT.NodeTitle: title_font,
            FT.NodeDescription: QFont(default_font),
            FT.ConnectionText: QFont(default_font),
            FT.MessageText: QFont(default_font)
        }

        self._frame_pen = QPen()
        self._frame_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        self._frame_pen.setWidthF(self.pixelMetric(SM.NodeFrameWidth))
        
        self._edge_pen = QPen()
        self._edge_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        self._edge_pen.setWidthF(self.pixelMetric(SM.EdgeWidth))
    
    def framePen(self, palette: Palette) -> QPen:
        result = QPen(self._frame_pen)
        result.setColor(palette.color(Palette.Frame))

        return result
    
    def edgePen(self, palette: Palette) -> QPen:
        result = QPen(self._edge_pen)
        result.setColor(palette.color(Palette.Edge))

        return result

    def inchMetric(self, metric: SizeMetric, /):
        return self._inch_metric[metric]
    
    def pixelMetric(self, metric: SizeMetric, /):
        return px(self._inch_metric[metric])
    
    def font(self, which: Font, /):
        return self._font[which]

# For convenience, nested enums are imported into the class itself.
import_enum(Style, Style.SizeMetric)
import_enum(Style, Style.Font, "{name}{cls}")
