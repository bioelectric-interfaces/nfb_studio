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
            # Generate a label for radio button
            # Find starting node in sequence
            node = None
            for node in seq.nodes:
                if len(node.inputs[0].edges) == 0:
                    break
            
            label = node.title()
            # Go to next node in this sequence
            while len(node.outputs[0].edges) != 0:
                for edge in node.outputs[0].edges:
                    if edge.targetNode() in seq.nodes:
                        node = edge.targetNode()
                        label = label + " → " + node.title()
                        break

            button = QRadioButton(label)
            button.clicked.connect(makeSelectSequence(seq))

            self.button_group.addButton(button)
            self.layout().addWidget(button)
        
        self.layout().addWidget(scheme.getView())


class ExportWizard(QWizard):
    """A wizard responsible for guiding the user through the process of exporting an experiment."""
    def __init__(self, parent, experiment):
        super().__init__(parent)
        self.setWindowTitle("Experiment Export")
        self.sequence_page = SelectSequencePage(self, experiment.sequence_scheme)
        self.addPage(self.sequence_page)

    def sequence(self):
        return self.sequence_page.sequence
