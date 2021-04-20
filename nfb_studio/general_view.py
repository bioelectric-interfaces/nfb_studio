"""Config widget for general properties of an experiment."""
from PySide2.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QLineEdit, QHBoxLayout, QCheckBox, QDoubleSpinBox, QFileDialog
)
from nfb_studio.util import StackedDictWidget
from nfb_studio.pathedit import PathEdit


class GeneralView(QWidget):
    """Config widget for general properties of an experiment.
    This "view" does not have a model. Instead, it is a part of a bigger view called ExperimentView, and gets updated
    with it.
    """

    inlet_type_export_values = {
        "LSL stream": "lsl",
        "LSL file stream": "lsl_from_file",
        "LSL generator": "lsl_generator",
        "Field trip buffer": "ftbuffer"
    }
    inlet_type_import_values = {v: k for k, v in inlet_type_export_values.items()}

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QFormLayout()
        self.setLayout(layout)

        self.name = QLineEdit()

        # prefilter_lower_bound ---------------------------------------------------------------------------------------------
        self.prefilter_lower_bound_enable = QCheckBox()
        self.prefilter_lower_bound_enable.stateChanged.connect(self._adjust)

        self.prefilter_lower_bound = QDoubleSpinBox()
        self.prefilter_lower_bound.setEnabled(False)
        self.prefilter_lower_bound.valueChanged.connect(self._adjust)
        self.prefilter_lower_bound.setMinimum(0)
        self.prefilter_lower_bound.setMaximum(0)  # TODO: add proper value
        self.prefilter_lower_bound.setValue(0)    # TODO: add proper value

        prefilter_lower_bound_widget = QWidget()
        prefilter_lower_bound_widget.setContentsMargins(0, 0, 0, 0)
        prefilter_lower_bound_widget.setLayout(QHBoxLayout())
        prefilter_lower_bound_widget.layout().setContentsMargins(0, 0, 0, 0)
        prefilter_lower_bound_widget.layout().addWidget(self.prefilter_lower_bound_enable)
        prefilter_lower_bound_widget.layout().addWidget(self.prefilter_lower_bound)

        # prefilter_upper_bound --------------------------------------------------------------------------------------------
        self.prefilter_upper_bound_enable = QCheckBox()
        self.prefilter_upper_bound_enable.stateChanged.connect(self._adjust)

        self.prefilter_upper_bound = QDoubleSpinBox()
        self.prefilter_upper_bound.setEnabled(False)
        self.prefilter_upper_bound.valueChanged.connect(self._adjust)
        self.prefilter_upper_bound.setMinimum(self.prefilter_lower_bound.value())
        self.prefilter_upper_bound.setMaximum(10000)  # TODO: add proper value
        self.prefilter_upper_bound.setValue(0)        # TODO: add proper value

        prefilter_upper_bound_widget = QWidget()
        prefilter_upper_bound_widget.setContentsMargins(0, 0, 0, 0)
        prefilter_upper_bound_widget.setLayout(QHBoxLayout())
        prefilter_upper_bound_widget.layout().setContentsMargins(0, 0, 0, 0)
        prefilter_upper_bound_widget.layout().addWidget(self.prefilter_upper_bound_enable)
        prefilter_upper_bound_widget.layout().addWidget(self.prefilter_upper_bound)

        # Inlet selection ----------------------------------------------------------------------------------------------
        self.inlet_type = QComboBox()
        self.inlet_type.addItem("LSL stream")
        self.inlet_type.addItem("LSL file stream")
        self.inlet_type.addItem("LSL generator")
        self.inlet_type.addItem("Field trip buffer")

        self.lsl_stream_name = QComboBox()
        self.lsl_stream_name.addItem("NVX136_Data")
        self.lsl_stream_name.addItem("Mitsar")

        self.lsl_filename = PathEdit()
        dialog = QFileDialog(self, "Open")
        dialog.setFileMode(dialog.AnyFile)
        self.lsl_filename.setDialog(dialog)
        self.hostname_port = QLineEdit("localhost:1972")

        self.inlet_params = StackedDictWidget()
        self.inlet_params.setMaximumHeight(25)
        self.inlet_params.addWidget("LSL stream", self.lsl_stream_name)
        self.inlet_params.addWidget("LSL file stream", self.lsl_filename)
        self.inlet_params.addWidget("LSL generator", QWidget())
        self.inlet_params.addWidget("Field trip buffer", self.hostname_port)
        # TODO: LSL generator is not reflected in the exported file, even when selected.

        self.inlet_type.currentTextChanged.connect(self.inlet_params.setCurrentKey)

        self.inlet_config = QWidget()
        self.inlet_config.setContentsMargins(0, 0, 0, 0)
        inlet_layout = QHBoxLayout()
        inlet_layout.setContentsMargins(0, 0, 0, 0)
        inlet_layout.addWidget(self.inlet_type)
        inlet_layout.addWidget(self.inlet_params)
        self.inlet_config.setLayout(inlet_layout)

        # --------------------------------------------------------------------------------------------------------------
        self.name = QLineEdit("Experiment")
        self.dc = QCheckBox()

        self.plot_raw = QCheckBox()
        self.plot_raw.setChecked(True)
        self.plot_signals = QCheckBox()
        self.plot_signals.setChecked(True)
        self.show_subject_window = QCheckBox()
        self.show_subject_window.setChecked(True)

        self.discard_channels = QLineEdit()
        self.reference_sub = QLineEdit()
        self.show_proto_rectangle = QCheckBox()
        self.show_notch_filters = QCheckBox()

        # Adding properties to the widget ------------------------------------------------------------------------------
        layout.addRow("Name", self.name)
        layout.addRow("Inlet", self.inlet_config)
        layout.addRow("Enable DC blocker", self.dc)
        layout.addRow("Prefilter band (lower bound)", prefilter_lower_bound_widget)
        layout.addRow("Prefilter band (upper bound)", prefilter_upper_bound_widget)
        layout.addRow("Plot raw", self.plot_raw)
        layout.addRow("Plot signals", self.plot_signals)
        layout.addRow("Show subject window", self.show_subject_window)
        layout.addRow("Discard channels", self.discard_channels)
        layout.addRow("Reference sub", self.reference_sub)
        layout.addRow("Show proto rectangle", self.show_proto_rectangle)
        layout.addRow("Show notch filters", self.show_notch_filters)
    
    def updateModel(self, ex, /):
        ex.name = self.name.text()
        ex.inlet = self.inlet_type_export_values[self.inlet_type.currentText()]
        ex.lsl_stream_name = self.lsl_stream_name.currentText()
        ex.raw_data_path = self.lsl_filename.text()
        ex.hostname_port = self.hostname_port.text()
        ex.dc = self.dc.isChecked()
        
        if self.prefilter_lower_bound_enable.isChecked():
            prefilter_lower_bound = self.prefilter_lower_bound.value()
        else:
            prefilter_lower_bound = None
        
        if self.prefilter_upper_bound_enable.isChecked():
            prefilter_upper_bound = self.prefilter_upper_bound.value()
        else:
            prefilter_upper_bound = None
        
        ex.prefilter_band = (prefilter_lower_bound, prefilter_upper_bound)
        ex.plot_raw = self.plot_raw.isChecked()
        ex.plot_signals = self.plot_signals.isChecked()
        ex.show_subject_window = self.show_subject_window.isChecked()
        ex.discard_channels = self.discard_channels.text()
        ex.reference_sub = self.reference_sub.text()
        ex.show_proto_rectangle = self.show_proto_rectangle.isChecked()
        ex.show_notch_filters = self.show_notch_filters.isChecked()

    def _adjust(self):
        if self.prefilter_lower_bound_enable.isChecked():
            self.prefilter_lower_bound.setEnabled(True)
            self.prefilter_upper_bound.setMinimum(self.prefilter_lower_bound.value())
        else:
            self.prefilter_lower_bound.setEnabled(False)
            self.prefilter_upper_bound.setMinimum(0)
        
        if self.prefilter_upper_bound_enable.isChecked():
            self.prefilter_upper_bound.setEnabled(True)
            self.prefilter_lower_bound.setMaximum(self.prefilter_upper_bound.value())
        else:
            self.prefilter_upper_bound.setEnabled(False)
            self.prefilter_lower_bound.setMaximum(10000)  # TODO: add proper value
