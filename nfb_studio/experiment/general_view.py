"""Config widget for general properties of an experiment."""
from PySide2.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox, QLineEdit, QHBoxLayout, QCheckBox, QDoubleSpinBox
from nfb_studio.util.qt import StackedDictWidget


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

        # prefilterBandLow ---------------------------------------------------------------------------------------------
        self.prefilterBandLow_enable = QCheckBox()
        self.prefilterBandLow_enable.stateChanged.connect(self.on_prefilterBandLow_toggled)

        self.prefilterBandLow_label = QLabel("Prefilter band from")

        self.prefilterBandLow_input = QDoubleSpinBox()
        self.prefilterBandLow_input.setEnabled(False)
        self.prefilterBandLow_input.valueChanged.connect(self.on_prefilterBandLow_changed)
        self.prefilterBandLow_input.setMinimum(0)
        self.prefilterBandLow_input.setMaximum(0)  # TODO: add proper value
        self.prefilterBandLow_input.setValue(0)    # TODO: add proper value

        self.prefilterBandLow_rwidget = QWidget()
        self.prefilterBandLow_rwidget.setContentsMargins(0, 0, 0, 0)
        self.prefilterBandLow_rwidget.setLayout(QHBoxLayout())
        self.prefilterBandLow_rwidget.layout().setContentsMargins(0, 0, 0, 0)
        self.prefilterBandLow_rwidget.layout().addWidget(self.prefilterBandLow_enable)
        self.prefilterBandLow_rwidget.layout().addWidget(self.prefilterBandLow_input)

        # prefilterBandHigh --------------------------------------------------------------------------------------------
        self.prefilterBandHigh_enable = QCheckBox()
        self.prefilterBandHigh_enable.stateChanged.connect(self.on_prefilterBandHigh_toggled)

        self.prefilterBandHigh_label = QLabel("Prefilter band to")

        self.prefilterBandHigh_input = QDoubleSpinBox()
        self.prefilterBandHigh_input.setEnabled(False)
        self.prefilterBandHigh_input.valueChanged.connect(self.on_prefilterBandHigh_changed)
        self.prefilterBandHigh_input.setMinimum(self.prefilterBandLow_input.value())
        self.prefilterBandHigh_input.setMaximum(10000)  # TODO: add proper value
        self.prefilterBandHigh_input.setValue(0)        # TODO: add proper value

        self.prefilterBandHigh_rwidget = QWidget()
        self.prefilterBandHigh_rwidget.setContentsMargins(0, 0, 0, 0)
        self.prefilterBandHigh_rwidget.setLayout(QHBoxLayout())
        self.prefilterBandHigh_rwidget.layout().setContentsMargins(0, 0, 0, 0)
        self.prefilterBandHigh_rwidget.layout().addWidget(self.prefilterBandHigh_enable)
        self.prefilterBandHigh_rwidget.layout().addWidget(self.prefilterBandHigh_input)

        # Inlet selection ----------------------------------------------------------------------------------------------
        self.inlet_type = QComboBox()
        self.inlet_type.addItem("LSL stream")
        self.inlet_type.addItem("LSL file stream")
        self.inlet_type.addItem("LSL generator")
        self.inlet_type.addItem("Field trip buffer")

        self.lsl_stream_name = QComboBox()
        self.lsl_stream_name.addItem("NVX136_Data")
        self.lsl_stream_name.addItem("Mitsar")

        self.lsl_filename = QLineEdit()
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
        self.dc                 = QCheckBox()
        self.name     = QLineEdit("Experiment")

        self.plot_raw            = QCheckBox()
        self.plot_raw.setChecked(True)
        self.plot_signals        = QCheckBox()
        self.plot_signals.setChecked(True)
        self.show_subject_window  = QCheckBox()
        self.show_subject_window.setChecked(True)

        self.discard_channels    = QLineEdit()
        self.reference_sub       = QLineEdit()
        self.show_proto_rectangle = QCheckBox()
        self.show_notch_filters    = QCheckBox()

        # Adding properties to the widget ------------------------------------------------------------------------------
        layout.addRow("Name", self.name)
        layout.addRow("Inlet", self.inlet_config)
        layout.addRow("dc", self.dc)
        layout.addRow("Prefilter band from", self.prefilterBandLow_rwidget)
        layout.addRow("Prefilter band to", self.prefilterBandHigh_rwidget)
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
        
        if self.prefilterBandLow_enable.isChecked():
            prefilterBandLow = self.prefilterBandLow_input.value()
        else:
            prefilterBandLow = None
        
        if self.prefilterBandHigh_enable.isChecked():
            prefilterBandHigh = self.prefilterBandHigh_input.value()
        else:
            prefilterBandHigh = None
        
        ex.prefilter_band = (prefilterBandLow, prefilterBandHigh)
        ex.plot_raw = self.plot_raw.isChecked()
        ex.plot_signals = self.plot_signals.isChecked()
        ex.show_subject_window = self.show_subject_window.isChecked()
        ex.discard_channels = self.discard_channels.text()
        ex.reference_sub = self.reference_sub.text()
        ex.show_proto_rectangle = self.show_proto_rectangle.isChecked()
        ex.show_notch_filters = self.show_notch_filters.isChecked()


    def on_prefilterBandLow_toggled(self):
        if self.prefilterBandLow_enable.isChecked():
            self.prefilterBandLow_input.setEnabled(True)

            # Update limits
            self.prefilterBandHigh_input.setMinimum(self.prefilterBandLow_input.value())
        else:
            self.prefilterBandLow_input.setEnabled(False)

            # Update limits
            self.prefilterBandHigh_input.setMinimum(0)

    def on_prefilterBandHigh_toggled(self):
        if self.prefilterBandHigh_enable.isChecked():
            self.prefilterBandHigh_input.setEnabled(True)

            # Update limits
            self.prefilterBandLow_input.setMaximum(self.prefilterBandHigh_input.value())
        else:
            self.prefilterBandHigh_input.setEnabled(False)

            # Update limits
            self.prefilterBandLow_input.setMaximum(10000)  # TODO: add proper value

    def on_prefilterBandLow_changed(self):
        # Update limits
        self.prefilterBandHigh_input.setMinimum(self.prefilterBandLow_input.value())

    def on_prefilterBandHigh_changed(self):
        # Update limits
        self.prefilterBandLow_input.setMaximum(self.prefilterBandHigh_input.value())
