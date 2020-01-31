from Qt.QtCore import Qt
from Qt.QtGui import QPainter
from Qt.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from nfb_studio.widgets.scheme import Node, Edge, Input, Output, InfoMessage, WarningMessage, ErrorMessage


class TestNode(Node):
    def __init__(self):
        super(TestNode, self).__init__()

        self.setTitle("Test node")
        self.setDescription("Stream: Mitsar\nFrequency: 500 Hz\nChannels: 30")

        self.addInput(Input("Input 1"))
        self.addInput(Input("Input 2"))
        self.addInput(Input("Input 3"))

        self.addOutput(Output("Output 1"))
        self.addOutput(Output("Output 3"))
        self.insertOutput(1, Output("Output 2 long long long long long long"))

        self.removeInput(0)


def main():
    app = QApplication([])
    scene = QGraphicsScene()
    n = TestNode()
    n2 = TestNode()
    n3 = TestNode()
    e = Edge()
    e2 = Edge()
    e.setSource(n.outputs[0])
    e.setTarget(n2.inputs[0])
    n.outputs[0].edges.add(e)
    n2.inputs[0].edges.add(e)

    e2.setSource(n3.outputs[0])
    e2.setTarget(n2.inputs[1])
    n3.outputs[0].edges.add(e2)
    n2.inputs[1].edges.add(e2)

    n.setPosition(1, 1)
    n.addMessage(InfoMessage("InfoMessage message"))
    n.addMessage(WarningMessage("WarningMessage message"))
    n.addMessage(ErrorMessage("ErrorMessage message"))
    scene.addItem(e)
    scene.addItem(e2)
    scene.addItem(n)
    scene.addItem(n2)
    scene.addItem(n3)

    n.setTitle("LSL Input")
    n.setDescription("Stream: Mitsar\nFrequency: 500 Hz\nChannels: 30")

    n2.setTitle("Bandpass Filter")
    n3.setTitle("Aux Input")

    w = QGraphicsView(scene)
    w.setDragMode(QGraphicsView.RubberBandDrag)
    w.setRubberBandSelectionMode(Qt.ContainsItemShape)
    w.setRenderHint(QPainter.Antialiasing)
    w.setRenderHint(QPainter.SmoothPixmapTransform)
    w.setMinimumSize(800, 600)
    w.show()

    n2.setPosition(3, 3)

    return app.exec_()


if __name__ == "__main__":
    main()
