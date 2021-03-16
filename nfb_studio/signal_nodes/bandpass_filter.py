"""NFB main source signal."""
from PySide2.QtWidgets import QSpinBox, QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .spatial_filter import SpatialFilter


class BandpassFilter(SignalNode):
    input_type = SpatialFilter.output_type
    output_type = DataType(102)

    class Config(SignalNode.Config):
        """Config widget displayed for BandpassFilter."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            # Upper bound ----------------------------------------------------------------------------------------------
            self.lower_bound_enable = QCheckBox()
            self.lower_bound_enable.setChecked(True)
            self.lower_bound_enable.stateChanged.connect(self.updateModel)

            self.lower_bound = QDoubleSpinBox()
            self.lower_bound.valueChanged.connect(self.updateModel)
            self.lower_bound.setMinimum(0)
            self.lower_bound.setMaximum(250)
            self.lower_bound.setSuffix(" Hz")

            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            lower_bound_widget = QWidget()
            lower_bound_widget.setContentsMargins(0, 0, 0, 0)
            lower_bound_widget.setLayout(layout)
            layout.addWidget(self.lower_bound_enable)
            layout.addWidget(self.lower_bound)

            # Lower bound ----------------------------------------------------------------------------------------------
            self.upper_bound_enable = QCheckBox()
            self.upper_bound_enable.setChecked(True)
            self.upper_bound_enable.stateChanged.connect(self.updateModel)

            self.upper_bound = QDoubleSpinBox()
            self.upper_bound.valueChanged.connect(self.updateModel)
            self.upper_bound.setMinimum(0)
            self.upper_bound.setMaximum(250)
            self.upper_bound.setSuffix(" Hz")

            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            upper_bound_widget = QWidget()
            upper_bound_widget.setContentsMargins(0, 0, 0, 0)
            upper_bound_widget.setLayout(layout)
            layout.addWidget(self.upper_bound_enable)
            layout.addWidget(self.upper_bound)

            # Filter type and length -----------------------------------------------------------------------------------
            self.filter_type = QComboBox()
            for name in BandpassFilter.filter_name_to_type:
                self.filter_type.addItem(name)
            self.filter_type.currentTextChanged.connect(self.updateModel)
            
            self.filter_length = QSpinBox()
            self.filter_length.setMinimum(2)
            self.filter_length.setMaximum(1000000)
            self.filter_length.setValue(1000)
            self.filter_length.valueChanged.connect(self.updateModel)

            self.filter_order = QSpinBox()
            self.filter_order.setRange(1, 4)
            self.filter_order.valueChanged.connect(self.updateModel)

            # ----------------------------------------------------------------------------------------------------------
            layout = QFormLayout()
            layout.addRow("Lower bound:", lower_bound_widget)
            layout.addRow("Upper bound:", upper_bound_widget)
            layout.addRow("Filter type:", self.filter_type)
            layout.addRow("Filter order:", self.filter_order)
            layout.addRow("Filter length:", self.filter_length)
            self.setLayout(layout)

        def updateModel(self):
            n = self.node()
            if n is None:
                return

            if self.lower_bound_enable.isChecked():
                lower_bound = self.lower_bound.value()
            else:
                lower_bound = None
            
            if self.upper_bound_enable.isChecked():
                upper_bound = self.upper_bound.value()
            else:
                upper_bound = None
            
            filter_type = n.filter_name_to_type[self.filter_type.currentText()]
            filter_length = self.filter_length.value()
            filter_order = self.filter_order.value()

            n.setLowerBound(lower_bound)
            n.setUpperBound(upper_bound)
            n.setFilterType(filter_type)
            n.setFilterLength(filter_length)
            n.setFilterOrder(filter_order)

        def updateView(self):
            n = self.node()
            if n is None:
                return

            # Prevent view fields from emitting signals while they are updated
            self.lower_bound.blockSignals(True)
            self.upper_bound.blockSignals(True)
            self.filter_type.blockSignals(True)
            self.filter_length.blockSignals(True)
            self.filter_order.blockSignals(True)

            if n.upperBound() is None:
                self.upper_bound_enable.setChecked(False)
            else:
                self.upper_bound_enable.setChecked(True)
                self.upper_bound.setValue(n.upperBound())
            
            if n.lowerBound() is None:
                self.lower_bound_enable.setChecked(False)
            else:
                self.lower_bound_enable.setChecked(True)
                self.lower_bound.setValue(n.lowerBound())
            
            self.filter_type.setCurrentText(n.filter_type_to_name[n.filterType()])
            self.filter_length.setValue(n.filterLength())
            self.filter_order.setValue(n.filterOrder())
            
            # Release the block and call adjust
            self.lower_bound.blockSignals(False)
            self.upper_bound.blockSignals(False)
            self.filter_type.blockSignals(False)
            self.filter_length.blockSignals(False)
            self.filter_order.blockSignals(False)
            self._adjust()

        def _adjust(self):
            """Adjust displayed values and limits in response to changes."""            
            # Enable spinbox widgets based on their checkbox
            self.lower_bound.setEnabled(self.lower_bound_enable.isChecked())
            self.upper_bound.setEnabled(self.upper_bound_enable.isChecked())

            # Adjust min and max so that lower_bound is never higher than upper_bound
            if self.lower_bound_enable.isChecked():
                self.upper_bound.setMinimum(self.lower_bound.value())
            else:
                self.upper_bound.setMinimum(0)
            
            if self.upper_bound_enable.isChecked():
                self.lower_bound.setMaximum(self.upper_bound.value())
            else:
                self.lower_bound.setMaximum(250)
            
            if self.filter_type.currentText() == "Butterworth":
                self.filter_order.setEnabled(True)
            else:
                self.filter_order.setEnabled(False)

    default_lower_bound = 0.0
    default_upper_bound = 250.0
    default_filter_type = "butter"
    default_filter_length = 1000
    default_filter_order = 2

    filter_type_to_name = {
        "butter": "Butterworth",
        "cfir": "cFIR"
    }
    filter_name_to_type = {v: k for k, v in filter_type_to_name.items()}

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Bandpass Filter")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._lower_bound = self.default_lower_bound
        self._upper_bound = self.default_upper_bound
        self._filter_type = self.default_filter_type
        self._filter_length = self.default_filter_length
        self._filter_order = self.default_filter_order
        self._adjust()
    
    def lowerBound(self):
        return self._lower_bound
    
    def upperBound(self):
        return self._upper_bound
    
    def filterType(self):
        return self._filter_type
    
    def filterLength(self):
        return self._filter_length
    
    def filterOrder(self):
        return self._filter_order
    
    def setFilterType(self, value, /):
        self._filter_type = value
        self._adjust()

    def setFilterLength(self, value, /):
        self._filter_length = value
        self._adjust()
    
    def setFilterOrder(self, value, /):
        self._filter_order = value
        self._adjust()

    def setLowerBound(self, value, /):
        self._lower_bound = value
        self._adjust()
    
    def setUpperBound(self, value, /):
        self._upper_bound = value
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        lower_bound = self.lowerBound()
        if self.lowerBound() is None:
            lower_bound = ""

        upper_bound = self.upperBound()
        if self.upperBound() is None:
            upper_bound = ""

        # Description
        if self.filterType() == "butter":
            filter_desc = f"Filter: {self.filter_type_to_name[self.filterType()]} (#{self.filterOrder()})\n"
        else:
            filter_desc = f"Filter: {self.filter_type_to_name[self.filterType()]}\n"

        self.setDescription(
            f"Range: {lower_bound}~{upper_bound} Hz\n" +
            filter_desc +
            f"Length: {self.filterLength()}"
        )

    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        signal["fBandpassLowHz"] = self.lowerBound()
        signal["fBandpassHighHz"] = self.upperBound()
        signal["fFFTWindowSize"] = float(self.filterLength())
        signal["sTemporalFilterType"] = self.filterType()
        signal["fTemporalFilterButterOrder"] = self.filterOrder()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["lower_bound"] = self.lowerBound()
        data["upper_bound"] = self.upperBound()
        data["filter_type"] = self.filterType()
        data["filter_length"] = self.filterLength()
        data["filter_order"] = self.filterOrder()

        return data
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = super().deserialize(data)
        obj.setLowerBound(data["lower_bound"])
        obj.setUpperBound(data["upper_bound"])
        obj.setFilterType(data["filter_type"])
        obj.setFilterLength(data["filter_length"])
        obj.setFilterOrder(data["filter_order"])

        return obj
