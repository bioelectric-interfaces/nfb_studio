"""Config widget for a single experiment block."""
from PySide2.QtWidgets import (
    QWidget, QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit, QCheckBox, QGroupBox, QHBoxLayout, QLabel
)


class BlockView(QWidget):
    """Config widget for a single experiment block.  
    In a model-view paradigm, this is a view, and block is a model. A new block can be set using setModel.
    """
    statistics_type_to_name = {
        "max": "Min/Max",
        "meanstd": "Standardise"
    }
    statistics_name_to_type = {v: k for k, v in statistics_type_to_name.items()}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self._model = None

        # Block properties ---------------------------------------------------------------------------------------------
        self.duration = QWidget()
        self.duration.setContentsMargins(0, 0, 0, 0)
        ly = QHBoxLayout()
        ly.setContentsMargins(0, 0, 0, 0)
        self.duration.setLayout(ly)

        self.duration_base = QDoubleSpinBox()
        self.duration_base.setRange(0, 1000)
        self.duration_base.setValue(10)

        self.duration_deviation = QDoubleSpinBox()
        self.duration_deviation.setRange(0, 10)
        self.duration_deviation.setValue(0)
        self.duration_deviation.setSingleStep(0.1)
        self.duration_deviation.setSuffix(" s")
        self.duration_base.valueChanged.connect(self.duration_deviation.setMaximum)

        ly.addWidget(self.duration_base)
        ly.addWidget(QLabel("±"))
        ly.addWidget(self.duration_deviation)

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
        self.statistics_type = QComboBox()
        for name in self.statistics_name_to_type:
            self.statistics_type.addItem(name)
        self.statistics_type.setCurrentText("Standardise")

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
        after_block_gblayout.addRow("Statistics type", self.statistics_type)

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
        self.updateView()
    
    def updateModel(self):
        """Copy data from this view to the block model.
        A similarly named function in the block copies data the opposite way. Use one or the other depending on where
        data was changed.
        """
        model = self.model()
        if model is None:
            return
        
        model.duration = self.duration_base.value()
        model.duration_deviation = self.duration_deviation.value()
        model.feedback_source = self.feedback_source.text()
        model.feedback_type = self.feedback_type.currentText()
        model.random_bound = self.random_bound.currentText()
        model.video_path = self.video_path.text()
        model.message = self.message.text()
        model.voiceover = self.voiceover.isChecked()
        model.mock_signal_path = self.mock_signal_path.text()
        model.mock_signal_dataset = self.mock_signal_dataset.text()
        model.mock_previous = self.mock_previous.value()
        model.mock_previous_reverse = self.mock_previous_reverse.isChecked()
        model.mock_previous_random = self.mock_previous_random.isChecked()
        model.start_data_driven_filter_designer = self.start_data_driven_filter_designer.isChecked()
        model.pause = self.pause.isChecked()
        model.beep = self.beep.isChecked()
        model.update_statistics = self.update_statistics.isChecked()
        model.statistics_type = self.statistics_name_to_type[self.statistics_type.currentText()]

    def updateView(self):
        model = self.model()
        if model is None:
            return
        
        self.duration_base.setValue(model.duration)
        self.duration_deviation.setValue(model.duration_deviation)
        self.feedback_source.setText(model.feedback_source)
        self.feedback_type.setCurrentText(model.feedback_type)
        self.mock_signal_path.setText(model.mock_signal_path)
        self.mock_signal_dataset.setText(model.mock_signal_dataset)
        self.mock_previous.setValue(model.mock_previous)
        self.mock_previous_reverse.setChecked(model.mock_previous_reverse)
        self.mock_previous_random.setChecked(model.mock_previous_random)
        self.pause.setChecked(model.pause)
        self.beep.setChecked(model.beep)
        self.start_data_driven_filter_designer.setChecked(model.start_data_driven_filter_designer)
        self.update_statistics.setChecked(model.update_statistics)
        self.statistics_type.setCurrentText(self.statistics_type_to_name[model.statistics_type])
        self.random_bound.setCurrentText(model.random_bound)
        self.video_path.setText(model.video_path)
        self.message.setText(model.message)
        self.voiceover.setChecked(model.voiceover)