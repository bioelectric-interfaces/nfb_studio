from PySide2.QtCore import Qt
from PySide2.QtWidgets import QButtonGroup, QRadioButton, QWidget, QVBoxLayout, QDockWidget, QScrollArea, QLabel, QSizePolicy
from .scheme import SchemeEditor
from .scheme.graph import Graph


class SequenceEditor(SchemeEditor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sequences = []
        """All sequences as a list of tuples (seq_as_graph, seq_as_list, radio_button)"""

        self.selector_placeholder = QLabel("(none)")
        self.selector_placeholder.setAlignment(Qt.AlignCenter)

        self.selector = QScrollArea()
        self.selector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout = QVBoxLayout()
        layout.addWidget(self.selector_placeholder)
        self.selector.setLayout(layout)
        self.selector_button_group = QButtonGroup()

        self.selector_dock = QDockWidget("Active Sequence", self)
        self.selector_dock.setWidget(self.selector)
        self.selector_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.selector_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.selector_dock)

    def setScheme(self, scheme):
        super().setScheme(scheme)
        self.scheme().graphChanged.connect(lambda item: self._updateSelector(item))
        self._updateSelector()

    def sequences(self):
        """Return a list of tuples (sequence_as_graph, sequence_as_list, sequence_button)."""
        return self._sequences
    
    def selectedSequence(self):
        """Return a tuple (sequence_as_graph, sequence_as_list, sequence_button) of the selected sequence."""
        checked = [s for s in self.sequences() if s[2].isChecked()]
        
        assert len(checked) <= 1
        if len(checked) == 1:
            return checked[0]
        return None

    def _updateSelector(self):
        sequences = list(self._possibleSequences())
        
        # Build a new widget with all the new options
        new_selector = QScrollArea()
        new_selector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        layout = QVBoxLayout()
        layout.addWidget(self.selector_placeholder)
        new_selector.setLayout(layout)
        self.selector_button_group = QButtonGroup()
        self.selector_dock.setWidget(new_selector)
        self.selector = new_selector
        
        if len(sequences) == 0:
            self.selector_placeholder.show()
            return
        self.selector_placeholder.hide()

        # Some black magic because of problems with scopes
        def selectSequence(seq):
            self.scheme().clearSelection()
            seq[0].selectAll()

        def makeSelectSequence(seq):
            return lambda: selectSequence(seq)
        # End of black magic

        self._sequences = []
        for sgraph, slist in sequences:
            label = " → ".join([node.title() for node in slist])

            button = QRadioButton(label)
            button.clicked.connect(makeSelectSequence((sgraph, slist)))

            self.selector_button_group.addButton(button)
            layout.addWidget(button)
            self._sequences.append((sgraph, slist, button))
        
        # Now that the new widget was built, determine which point should be selected considering previous selection
        selected = self.selectedSequence()

        if selected is None:
            # If no previous selection, select the first one
            self._sequences[0][2].setChecked(True)
            return

        candidates = []
        for sgraph, slist, button in self._sequences:
            # Analyze every new option
            if selected[0] <= sgraph:
                # If old selection is a subset of a new option, that means a new node was attached and current selection
                # should be expanded
                button.setChecked(True)
                return
            
            if sgraph <= selected[0]:
                # This option is a subset of previous option, which means that something was deleted. If an edge was
                # removed, there may be other parts of previous options, add them all to candidates for new selection.
                candidates.append((sgraph, slist, button))

        if len(candidates) == 0:
            # If there are no candidates, select the first option.
            self._sequences[0][2].setChecked(True)
            return

        for node in selected[1]:
            # For each node in order in prev. selection, see if any candidates have it. Select the first mathcing one.
            for sgraph, slist, button in candidates:
                if node in sgraph:
                    button.setChecked(True)
                    return

    def _possibleSequences(self):
        """Return a list of tuples, where each tuple represents a possible experiment sequence.
        Tuple contains 2 items: a graph-view of the sequence, and a list of nodes of that sequence in order.
        """
        g = self.scheme().graph

        for node in g.nodes:
            if len(node.inputs) == 0 or len(list(node.inputs[0].edges)) == 0:
                for sequence in self._possibleSequencesFrom(node):
                    yield sequence

    def _possibleSequencesFrom(self, node):
        """Return a list of tuples, where each tuple represents a possible experiment sequence starting from this node.
        Tuple contains 2 items: a graph-view of the sequence, and a list of nodes of that sequence in order.
        """
        has_sequences = False

        for out in node.outputs:
            for edge in out.edges:
                connected = edge.targetNode()

                if connected is None:
                    # Filter for edges with no target nodes. These are usually fake edges that the user drags.
                    # When they drop and become real, they will have a node.
                    continue

                for sequence_graph, sequence_list in self._possibleSequencesFrom(connected):
                    sequence_graph.add(node)
                    sequence_graph.add(edge)
                    sequence_list.insert(0, node)
                    
                    yield (sequence_graph, sequence_list)
                    has_sequences = True
        
        if not has_sequences:
            # If no sequences could be built, this node is the final node.
            # In this case, just yield itself.
            result = (Graph(), list())
            result[0].add(node)
            result[1].append(node)
            yield result
