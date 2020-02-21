"""A collection of colors for use in the scheme graphics items."""
from enum import Enum, auto

from PySide2.QtCore import Qt
from PySide2.QtGui import QBrush, QColor

from nfb_studio.util import import_enum

class Palette:
    """A collection of colors for use in the scheme graphics items."""
    class ColorGroup(Enum):
        """An enumeration of possible color groups in this Palette. 
        
        Color groups represent the states, in which the scheme item must be for the color set to be used."""
        Active = 0
        Selected = auto()
        Disabled = auto()
        Inactive = auto()
    
    class ColorRole(Enum):
        """An enumeration representing different roles, in which these colors are useful."""
        Background = 0
        Base = auto()
        Frame = auto()
        Edge = auto()
        Text = auto()

    def __init__(self):
        CG = self.ColorGroup
        CR = self.ColorRole

        self._brush = {}

        self._brush[CG.Active] = {
            CR.Background: QBrush(QColor.fromRgb(240, 240, 240)),
            CR.Base: QBrush(Qt.white),
            CR.Frame: QBrush(Qt.black),
            CR.Edge: QBrush(Qt.black),
            CR.Text: QBrush(Qt.black)
        }

        self._brush[CG.Selected] = {
            CR.Background: QBrush(Qt.white),
            CR.Base: QBrush(QColor.fromRgb(247, 247, 255)),
            CR.Frame: QBrush(QColor.fromRgb(0, 0, 200)),
            CR.Edge: QBrush(QColor.fromRgb(0, 0, 200)),
            CR.Text: QBrush(Qt.black)
        }

        self._brush[CG.Disabled] = {}
        self._brush[CG.Inactive] = {}

        # Copy Active group to other ones
        for key in self._brush[CG.Active]:
            self._brush[CG.Disabled][key] = QBrush(self._brush[CG.Active][key])
            self._brush[CG.Inactive][key] = QBrush(self._brush[CG.Active][key])
        
        self._current_color_group = CG.Active
    
    # Current color group ----------------------------------------------------------------------------------------------
    def setCurrentColorGroup(self, cg: ColorGroup, /):
        self._current_color_group = cg

    def currentColorGroup(self) -> ColorGroup:
        return self._current_color_group
    
    # Color & brush manipulation ---------------------------------------------------------------------------------------
    def brush(self, *args) -> QBrush:
        """Return the brush for the specified group and role.

        This function can accept the following arguments:  
        - `def brush(self, group: Palette.ColorGroup, role: Palette.ColorRole)`
        - `def brush(self, role: Palette.ColorRole)`

        If `group` is not specified, it defaults to `currentColorGroup()`.
        """
        if not 1 <= len(args) <= 2:
            raise TypeError("incorrect number of arguments provided")

        group = args[0] if len(args) == 2 else self.currentColorGroup()
        role = args[-1]

        return self._brush[group][role]
    
    def color(self, *args) -> QColor:
        """Return the color for the specified group and role.

        This function can accept the following arguments:  
        - `def color(self, group: Palette.ColorGroup, role: Palette.ColorRole)`
        - `def color(self, role: Palette.ColorRole)`

        If `group` is not specified, it defaults to `currentColorGroup()`.
        """
        return self.brush(*args).color()
    
    def setBrush(self, *args):
        """Set the brush for the specified group and role.

        This function can accept the following arguments:  
        - `def setBrush(self, group: Palette.ColorGroup, role: Palette.ColorRole, brush: QBrush)`
        - `def setBrush(self, role: Palette.ColorRole, color: QColor)`

        If `group` is not specified, it defaults to `currentColorGroup()`.
        """
        if not 2 <= len(args) <= 3:
            raise TypeError("incorrect number of arguments provided")

        group = args[0] if len(args) == 3 else self.currentColorGroup()
        role = args[-2]
        brush = args[-1]

        self._brush[group][role] = QBrush(brush)
    
    def setColor(self, *args):
        """Set the brush to solid color for the specified group and role.

        This function can accept the following arguments:  
        - `def setColor(self, group: Palette.ColorGroup, role: Palette.ColorRole, color: QColor)`
        - `def setColor(self, role: Palette.ColorRole, color: QColor)`

        If `group` is not specified, it defaults to `currentColorGroup()`.
        """
        # This function is provided for consistency with the QPalette implementation. Due to python duck-typing, 
        # setBrush actually accepts a QColor as an argument.
        self.setBrush(*args)

    # Individual brushes -----------------------------------------------------------------------------------------------
    def background(self) -> QBrush:
        return self.brush(self.ColorRole.Background)
    
    def base(self) -> QBrush:
        return self.brush(self.ColorRole.Base)

    def frame(self) -> QBrush:
        return self.brush(self.ColorRole.Frame)

    def edge(self) -> QBrush:
        return self.brush(self.ColorRole.Edge)

    def text(self) -> QBrush:
        return self.brush(self.ColorRole.Text)

import_enum(Palette, Palette.ColorGroup)
import_enum(Palette, Palette.ColorRole)
