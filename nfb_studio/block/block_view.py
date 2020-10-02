"""Config widget for a single experiment block."""
from PySide2.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit, QCheckBox, QGroupBox


class BlockView(QWidget):
    """Config widget for a single experiment block.  
    In a model-view paradigm, this is a view, and block is a model. A new block can be set using setModel.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self._model = None

        # Block properties ---------------------------------------------------------------------------------------------
        self.duration = QDoubleSpinBox()
        self.duration.setValue(10)
        self.duration.setSuffix("s")

        self.feedback_source = QLineEdit("All")

        self.feedback_type = QComboBox()
        self.feedback_type.addItem("Baseline")
        self.feedback_type.addItem("Feedback")

        self.mock_signal_path = QLineEdit()
        self.mock_signal_dataset = QLineEdit()
        self.mock_previous = QSpinBox()
        self.mock_previous_reverse = QCheckBox()
        self.mock_previous_random = QCheckBox()
        self.pause = QCheckBox()
        self.beep = QCheckBox()
        self.start_data_driven_filter_designer = QCheckBox()
        self.update_statistics = QCheckBox()

        self.random_bound = QComboBox()
        self.random_bound.addItem("SimCircle")
        self.random_bound.addItem("RandomCircle")
        self.random_bound.addItem("Bar")

        self.video_path = QLineEdit()
        self.message = QLineEdit()
        self.voiceover = QCheckBox()

        # Grouped properties -------------------------------------------------------------------------------------------
        # Mock signal
        mock_signal_groupbox = QGroupBox("Mock signal")
        mock_signal_gblayout = QFormLayout()
        mock_signal_groupbox.setLayout(mock_signal_gblayout)
        mock_signal_gblayout.addRow("Mock signal file path", self.mock_signal_path)
        mock_signal_gblayout.addRow("Mock signal file dataset", self.mock_signal_dataset)
        mock_signal_gblayout.addRow("Mock previous", self.mock_previous)
        mock_signal_gblayout.addRow("Reverse mock previous", self.mock_previous_reverse)
        mock_signal_gblayout.addRow("Random mock previous", self.mock_previous_random)

        # After block actions
        after_block_groupbox = QGroupBox("After block actions")
        after_block_gblayout = QFormLayout()
        after_block_groupbox.setLayout(after_block_gblayout)
        after_block_gblayout.addRow("Start data driven filter designer", self.start_data_driven_filter_designer)
        after_block_gblayout.addRow("Pause", self.pause)
        after_block_gblayout.addRow("Beep", self.beep)
        after_block_gblayout.addRow("Update statistics", self.update_statistics)

        # Adding properties to the widget ------------------------------------------------------------------------------
        layout.addRow("Duration", self.duration)
        layout.addRow("Source", self.feedback_source)
        layout.addRow("FB Type", self.feedback_type)
        layout.addRow("Random bound", self.random_bound)
        layout.addRow("Video path", self.video_path)
        layout.addRow("Message for test subject", self.message)
        layout.addRow("Voiceover for message", self.voiceover)
        layout.addRow(mock_signal_groupbox)
        layout.addRow(after_block_groupbox)

    def model(self):
        return self._model

    def setModel(self, block, /):
        """Set the model block for this view.
        Data in the view will be updated to reflect the new block.
        """
        self._model = block
        block._view = self
        self._model.updateView()
    
    def updateModel(self):
        """Copy data from this view to the block model.
        A similarly named function in the block copies data the opposite way. Use one or the other depending on where
        data was changed.
        """
        block = self.model()
        if block is None:
            return
        
        block.duration = self.duration.value()
        block.feedback_source = self.feedback_source.text()
        block.feedback_type = self.feedback_type.currentText()
        block.random_bound = self.random_bound.currentText()
        block.video_path = self.video_path.text()
        block.message = self.message.text()
        block.voiceover = self.voiceover.isChecked()
        block.mock_signal_path = self.mock_signal_path.text()
        block.mock_signal_dataset = self.mock_signal_dataset.text()
        block.mock_previous = self.mock_previous.value()
        block.mock_previous_reverse = self.mock_previous_reverse.isChecked()
        block.mock_previous_random = self.mock_previous_random.isChecked()
        block.start_data_driven_filter_designer = self.start_data_driven_filter_designer.isChecked()
        block.pause = self.pause.isChecked()
        block.beep = self.beep.isChecked()
        block.update_statistics = self.update_statistics.isChecked()
