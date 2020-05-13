from PySide2.QtCore import Qt, QPointF, QRectF, QLineF, QMimeData
from PySide2.QtGui import QDrag, QPainterPath
from PySide2.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsSceneDragDropEvent, QApplication

from ...scheme_item import SchemeItem
from ...style import Style

class Trigger(SchemeItem):
    """Special invisible item that handles the area from which and to which the edge can be drawn."""
    DragMimeType = "application/x-nfb_studio-edge_drag"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(self.ItemHasNoContents)  # Item is invisible
        self.setAcceptDrops(True)
        self.setCursor(Qt.CrossCursor)

        self._radius = self.style().pixelMetric(Style.EdgeDragPrecisionRadius)
    
    def shape(self):
        path = QPainterPath()
        path.addEllipse(QPointF(), self._radius, self._radius)
        return path; 

    def boundingRect(self):
        return QRectF(-self._radius, -self._radius, self._radius*2, self._radius*2)
    
    def paint(self, painter, option, widget):
        '''path = QPainterPath()
        path.addEllipse(QPointF(), self._radius, self._radius)
        painter.drawPath(path)'''

    def styleChange(self):
        self.prepareGeometryChange()
        self._radius = self.style().pixelMetric(Style.EdgeDragPrecisionRadius)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if (QLineF(event.screenPos(), event.buttonDownScreenPos(Qt.LeftButton)).length()
            < QApplication.startDragDistance()):
            return
        
        self.parentItem().edgeDragStart()

        package = QMimeData()
        package.setData(self.DragMimeType, bytes())

        drag = QDrag(event.widget())
        drag.setMimeData(package)
        drag.exec_()

        self.parentItem().edgeDragStop()

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        package = event.mimeData()

        if package.hasFormat(self.DragMimeType):
            event.setAccepted(self.parentItem().edgeDragAccept())
        else:
            event.ignore()

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):
        self.parentItem().edgeDragDrop()
