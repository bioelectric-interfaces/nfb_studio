from PySide2.QtCore import QMimeData
from PySide2.QtGui import QDrag

class EdgeDrag(QDrag):
    format = "application/x-edgedrag"
    """Format that is used as the tag mime type. Actual information is stored in the scene."""

    def __init__(self, scheme, dragSource):
        super().__init__(dragSource)
        self.scheme = scheme

        # Add a tag-like mimedata. No info, just a type.
        package = QMimeData()
        package.setData(self.format, bytes())
        self.setMimeData(package)

    def exec_(self, *args, **kwargs):
        result = super().exec_(*args, **kwargs)
        
        # Delete the fake edge, regardless of the outcome
        self.scheme.edgeDragStop()

        return result