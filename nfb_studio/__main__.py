from Qt.QtWidgets import QApplication

from nfb_studio.widgets.scheme import Scheme, Node, Input, Output, InfoMessage, WarningMessage, ErrorMessage
from nfb_studio.serialize import ObjectEncoder, ObjectDecoder, serialize_qt, deserialize_qt

encoder = ObjectEncoder(object_hooks=serialize_qt, indent=4)
decoder = ObjectDecoder(object_hooks=deserialize_qt)


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
    scene = Scheme()

    n = TestNode()
    n.setTitle("LSL Input")
    n.setDescription("Stream: Mitsar\nFrequency: 500 Hz\nChannels: 30")
    n.setPosition(1, 1)
    n.addMessage(InfoMessage("InfoMessage message"))
    n.addMessage(WarningMessage("WarningMessage message"))
    n.addMessage(ErrorMessage("ErrorMessage message"))

    n2 = TestNode()
    n2.setTitle("Bandpass Filter")
    n2.setPosition(3, 3)

    n3 = TestNode()
    n3.setTitle("Aux Input")

    scene.addItem(n)
    scene.addItem(n2)
    scene.addItem(n3)
    scene.connect_nodes(n.outputs[0], n2.inputs[0])
    scene.connect_nodes(n3.outputs[0], n2.inputs[1])

    data = encoder.encode(scene)

    w = scene.getView()
    w.setMinimumSize(800, 600)
    w.show()

    return app.exec_()


if __name__ == "__main__":
    main()
