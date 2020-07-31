from PySide2.QtWidgets import QWizard, QWizardPage, QButtonGroup, QVBoxLayout, QRadioButton


class SelectSequencePage(QWizardPage):
    def __init__(self, parent, scheme):
        super().__init__(parent)
        self.sequence = None

        self.setLayout(QVBoxLayout())
        self.setTitle("Select the block sequence")
        self.setSubTitle("The block sequence you select will be executed in order from left to right.")

        self.button_group = QButtonGroup(self)

        def selectSequence(seq):
            print("Result:", ", ".join([n.title() for n in seq.nodes]))

            scheme.clearSelection()
            seq.selectAll()
            self.sequence = seq

        def makeSelectSequence(seq):
            return lambda: selectSequence(seq)

        for seq in scheme.graph.sequences():
            name = ", ".join([n.title() for n in seq.nodes])

            button = QRadioButton(name)
            button.clicked.connect(makeSelectSequence(seq))

            self.button_group.addButton(button)
            self.layout().addWidget(button)
        
        self.layout().addWidget(scheme.getView())


class ExportWizard(QWizard):
    def __init__(self, parent, experiment):
        super().__init__(parent)
        self.setWindowTitle("Experiment Export")
        self.sequence_page = SelectSequencePage(self, experiment.sequence_scheme)
        self.addPage()

    def sequence(self):
        return self.sequence_page.sequence