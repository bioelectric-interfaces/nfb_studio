"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QCheckBox, QDoubleSpinBox, QHBoxLayout

from ..scheme import Node, Input, Output, DataType


class BandpassFilter(Node):
    class Config(QWidget):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent)

            # fBandpassLowHz -------------------------------------------------------------------------------------------
            self.fBandpassLowHz_enable = QCheckBox()
            self.fBandpassLowHz_enable.setChecked(True)
            self.fBandpassLowHz_enable.stateChanged.connect(self.on_fBandpassLowHz_toggled)

            self.fBandpassLowHz_label = QLabel("fBandpassLowHz")

            self.fBandpassLowHz_lwidget = QWidget()
            self.fBandpassLowHz_lwidget.setLayout(QHBoxLayout())
            self.fBandpassLowHz_lwidget.layout().addWidget(self.fBandpassLowHz_enable)
            self.fBandpassLowHz_lwidget.layout().addWidget(self.fBandpassLowHz_label)

            self.fBandpassLowHz_input = QDoubleSpinBox()
            self.fBandpassLowHz_input.valueChanged.connect(self.on_fBandpassLowHz_changed)
            self.fBandpassLowHz_input.setMinimum(0)
            self.fBandpassLowHz_input.setMaximum(250)
            self.fBandpassLowHz_input.setValue(0)

            # fBandpassHighHz ------------------------------------------------------------------------------------------
            self.fBandpassHighHz_enable = QCheckBox()
            self.fBandpassHighHz_enable.setChecked(True)
            self.fBandpassHighHz_enable.stateChanged.connect(self.on_fBandpassHighHz_toggled)

            self.fBandpassHighHz_label = QLabel("fBandpassHighHz")

            self.fBandpassHighHz_lwidget = QWidget()
            self.fBandpassHighHz_lwidget.setLayout(QHBoxLayout())
            self.fBandpassHighHz_lwidget.layout().addWidget(self.fBandpassHighHz_enable)
            self.fBandpassHighHz_lwidget.layout().addWidget(self.fBandpassHighHz_label)

            self.fBandpassHighHz_input = QDoubleSpinBox()
            self.fBandpassHighHz_input.valueChanged.connect(self.on_fBandpassHighHz_changed)
            self.fBandpassHighHz_input.setMinimum(self.fBandpassLowHz_input.value())
            self.fBandpassHighHz_input.setMaximum(250)
            self.fBandpassHighHz_input.setValue(250)

            # ----------------------------------------------------------------------------------------------------------
            form = QFormLayout()
            form.addRow(self.fBandpassLowHz_lwidget, self.fBandpassLowHz_input)
            form.addRow(self.fBandpassHighHz_lwidget, self.fBandpassHighHz_input)
            self.setLayout(form)

            # Disallow the widget window from expanding past the form's recommended size
            self.setMaximumHeight(form.sizeHint().height())

        def on_fBandpassLowHz_toggled(self):
            if self.fBandpassLowHz_enable.isChecked():
                self.fBandpassLowHz_input.setEnabled(True)

                # Update limits
                self.fBandpassHighHz_input.setMinimum(self.fBandpassLowHz_input.value())
            else:
                self.fBandpassLowHz_input.setEnabled(False)

                # Update limits
                self.fBandpassHighHz_input.setMinimum(0)

        def on_fBandpassHighHz_toggled(self):
            if self.fBandpassHighHz_enable.isChecked():
                self.fBandpassHighHz_input.setEnabled(True)

                # Update limits
                self.fBandpassLowHz_input.setMaximum(self.fBandpassHighHz_input.value())
            else:
                self.fBandpassHighHz_input.setEnabled(False)

                # Update limits
                self.fBandpassLowHz_input.setMaximum(250)

        def on_fBandpassLowHz_changed(self):
            # Update limits
            self.fBandpassHighHz_input.setMinimum(self.fBandpassLowHz_input.value())

        def on_fBandpassHighHz_changed(self):
            # Update limits
            self.fBandpassLowHz_input.setMaximum(self.fBandpassHighHz_input.value())

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Bandpass Filter")
        self.addInput(Input("Input", DataType.Unknown))
        self.addOutput(Output("Output", DataType.Unknown))

        self.setConfigWidget(self.Config())
