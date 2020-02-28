from PySide2.QtCore import Qt, QPointF, QRectF, QLineF
from PySide2.QtGui import QDrag, QPainterPath
from PySide2.QtWidgets import QGraphicsSceneMouseEvent, QGraphicsSceneDragDropEvent, QApplication

from nfb_studio import StdMimeData

from ..scheme_item import SchemeItem
from ..style import Style
from .edge_drag import EdgeDrag

class Trigger(SchemeItem):
	"""Special invisible item that handles the area from which and to which the edge can be drawn."""

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setAcceptedMouseButtons(Qt.LeftButton)
		#self.setFlag(self.ItemHasNoContents)  # Item is invisible
		self.setAcceptDrops(True)

		self._radius = self.style().pixelMetric(Style.EdgeDragPrecisionRadius)
	
	def shape(self):
		path = QPainterPath()
		path.addEllipse(QPointF(), self._radius, self._radius)
		return path; 

	def boundingRect(self):
		return QRectF(-self._radius, -self._radius, self._radius*2, self._radius*2)
	
	def paint(self, painter, option, widget):
		path = QPainterPath()
		path.addEllipse(QPointF(), self._radius, self._radius)
		painter.drawPath(path)

	def styleChange(self):
		self.prepareGeometryChange()
		self._radius = self.style().pixelMetric(Style.EdgeDragPrecisionRadius)

	def mousePressEvent(self, event):
		pass

	def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
		if (QLineF(event.screenPos(), event.buttonDownScreenPos(Qt.LeftButton)).length()
			< QApplication.startDragDistance()):
			return
		
		drag = QDrag(event.widget())
		package = StdMimeData()
		drag.setMimeData(package.qmimedata)

		data = self.parentItem().edgeDragStart()
		package.setObject(data)

		drag.exec_()

	def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
		package = StdMimeData(event.mimeData())

		if package.hasObject(EdgeDrag):
			data = package.objectData(EdgeDrag)

			event.setAccepted(self.parentItem().edgeDragAccept(data))
		else:
			event.ignore()

	def dropEvent(self, event: QGraphicsSceneDragDropEvent):
		package = StdMimeData(event.mimeData())
		data = package.objectData(EdgeDrag)

		self.parentItem().edgeDragDrop(data)
