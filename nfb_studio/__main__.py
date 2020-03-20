import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QListView, QWidget, QHBoxLayout

from nfb_studio.widgets.scheme import Scheme, Node, Input, Output, InfoMessage, WarningMessage, ErrorMessage, Toolbox
from nfb_studio import std_encoder as encoder


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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.toolbox = Toolbox(self)
        self.tbview = self.toolbox.getView()

        self.scheme = Scheme(self)
        self.scheme_view = self.scheme.view

        w = QWidget()
        layout = QHBoxLayout()
        self.setCentralWidget(w)
        w.setLayout(layout)

        layout.addWidget(self.tbview)
        layout.addWidget(self.scheme_view)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    tb = main_window.toolbox
    lsl_input = TestNode()
    lsl_input.removeInput(-1)
    lsl_input.removeInput(-1)
    lsl_input.removeOutput(-1)
    lsl_input.removeOutput(-1)
    lsl_input.setTitle("LSL Input")

    bpf = Node()
    bpf.addInput(Input("Raw data"))
    bpf.addOutput(Output("Filtered data"))
    bpf.setTitle("Bandpass Filter")
    bpf.setDescription("Filter range:\n    50 Hz ~ 200 Hz")

    tb.addItem("LSL Input", lsl_input)
    tb.addItem("Bandpass Filter", bpf)

    '''scene = Scheme(app)

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

    w = scene.view
    w.setMinimumSize(800, 600)
    w.show()'''

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
