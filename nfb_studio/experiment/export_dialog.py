from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QRadioButton, QButtonGroup

class ExportDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Select the sequence of blocks you would like to export"))

        self._sequence_scheme = None

    def setSequenceScheme(self, scheme):
        self._sequence_scheme = scheme
        self._button_group = QButtonGroup(self)

        def selectSequence(seq):
            print("Result:", ", ".join([n.title() for n in seq.nodes]))

            scheme.clearSelection()
            seq.selectAll()

        def makeSelectSequence(seq):
            return lambda: selectSequence(seq)

        for seq in scheme.graph.sequences():
            name = ", ".join([n.title() for n in seq.nodes])

            button = QRadioButton(name)
            button.clicked.connect(makeSelectSequence(seq))

            self._button_group.addButton(button)
            self.layout().addWidget(button)
        
        self.layout().addWidget(scheme.getView())
