"""Config widget for a single experiment block."""
import itertools
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit, QCheckBox, QGroupBox


class BlockConfig(QWidget):
    """Config widget for a single experiment block."""
    newid = itertools.count()

    def __init__(self, block, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self.data = block

        self.name = QLabel("Block" + str(next(self.newid)))
        self.data.name = self.name.text()

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
        layout.addRow("Name", self.name)
        layout.addRow("Duration", self.duration)
        layout.addRow("Source", self.feedback_source)
        layout.addRow("FB Type", self.feedback_type)
        layout.addRow("Random bound", self.random_bound)
        layout.addRow("Video path", self.video_path)
        layout.addRow(mock_signal_groupbox)
        layout.addRow(after_block_groupbox)
