from PySide2.QtWidgets import QWizard, QWizardPage, QButtonGroup, QVBoxLayout, QRadioButton, QFileDialog, QLabel

from .util import FileSelect


class SelectSequencePage(QWizardPage):
    def __init__(self, scheme):
        super().__init__()
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


class FilePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.file_select = FileSelect()
        dialog = QFileDialog()
        dialog.setDefaultSuffix(".xml")
        dialog.setAcceptMode(dialog.AcceptSave)
        dialog.setWindowTitle("Save exported experiment")
        dialog.setNameFilter("XML Files (*.xml)")
        self.file_select.setDialog(dialog)

        layout.addWidget(QLabel("Location of exported experiment file:"))
        layout.addWidget(self.file_select)


class ExportWizard(QWizard):
    """A wizard responsible for guiding the user through the process of exporting an experiment."""
    def __init__(self, parent, experiment):
        super().__init__(parent)
        self.setWindowTitle("Experiment Export")
        self.sequence_page = None
        self.file_page = FilePage()

        self.preselected_sequence = None
        sequences = list(experiment.sequence_scheme.graph.sequences())
        if len(sequences) == 1:
            # If only one sequence is possible, skip the sequence select window.
            self.preselected_sequence = next(iter(sequences))
        else:
            self.sequence_page = SelectSequencePage(experiment.sequence_scheme)
            self.addPage(self.sequence_page)

        self.addPage(self.file_page)

    def sequence(self):
        return self.preselected_sequence or self.sequence_page.sequence

    def savePath(self):
        return self.file_page.file_select.text()