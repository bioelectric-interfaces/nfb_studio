"""A collection of custom general-purpose Qt widgets.
Generally, all graphics widgets accept measurements in inches instead of pixels to preserve sizes on different screens.
Conversion functions to and from inches are available in nfb_widgets.gui module.
"""
from .elided_line_item import ElidedLineItem
from .text_rect_item import TextRectItem
from .real_size_item import RealSizeItem
from .shadow_selectable_item import ShadowSelectableItem
