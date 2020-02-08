from PySide2.QtGui import QFont


class FontF(QFont):
    def __init__(self, family, pointSize=-1, weight=-1, italic=False):
        """A convenience class that subclasses QFont and sets correct font size in the constructor.
        QFont can set fractional font sizes, but only through a special method - not in the constructor.
        """
        super(FontF, self).__init__(family, -1, weight, italic)
        if pointSize != -1:
            self.setPointSizeF(pointSize)
