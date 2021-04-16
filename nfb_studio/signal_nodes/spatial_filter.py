"""NFB main source signal."""
from PySide2.QtWidgets import QWidget, QComboBox, QLabel, QFormLayout, QLineEdit, QRadioButton, QFileDialog

from ..scheme import Node, Input, Output, DataType
from .signal_node import SignalNode
from .lsl_input import LSLInput
from nfb_studio.pathedit import PathEdit


class SpatialFilter(SignalNode):
    input_type = LSLInput.output_type
    output_type = DataType(101)

    class Config(SignalNode.Config):
        """Config widget displayed for LSLInput."""
        def __init__(self, parent=None):
            super().__init__(parent=parent)

            layout = QFormLayout()
            self.setLayout(layout)

            self.vector = QLineEdit()
            self.vector.setPlaceholderText("Fp1=1;Cz=-1;...")
            self.vector.editingFinished.connect(self.updateModel)

            self.vector_path = PathEdit()
            dialog = QFileDialog(self, "Open")
            dialog.setFileMode(dialog.AnyFile)
            self.vector_path.setDialog(dialog)
            self.vector_path.pathChanged.connect(self.updateModel)

            # Vector data can be contained in a file or inputted directly from a file
            self.vector_radio_button = QRadioButton("Filter vector")
            self.vector_radio_button.toggled.connect(self.vector.setEnabled)
            self.vector_radio_button.clicked.connect(self.updateModel)
            self.vector_path_radio_button = QRadioButton("Filter vector file")
            self.vector_path_radio_button.toggled.connect(self.vector_path.setEnabled)
            self.vector_path_radio_button.clicked.connect(self.updateModel)

            layout.addRow(self.vector_radio_button, self.vector)
            layout.addRow(self.vector_path_radio_button, self.vector_path)

            self.vector_radio_button.setChecked(True)
            self.vector_path.setEnabled(False)
        
        def updateModel(self):
            n = self.node()
            if n is None:
                return
            
            if self.vector.isEnabled():
                n.setVector(self.vector.text())
            else:
                n.setVectorPath(self.vector_path.text())
        
        def updateView(self):
            n = self.node()
            if n is None:
                return
            
            self.vector.blockSignals(True)
            self.vector_path.blockSignals(True)

            if n.vector() is not None:
                self.vector.setText(n.vector())
                self.vector_radio_button.setChecked(True)
            else:
                self.vector_path.setText(n.vectorPath())
                self.vector_path_radio_button.setChecked(True)

            self.vector.blockSignals(False)
            self.vector_path.blockSignals(False)

    default_vector = ""
    default_vector_path = None

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Spatial Filter")
        self.addInput(Input("Input", self.input_type))
        self.addOutput(Output("Output", self.output_type))

        self._vector = self.default_vector
        self._vector_path = self.default_vector_path
        self._adjust()

    def vector(self) -> str:
        return self._vector
    
    def vectorPath(self) -> str:
        return self._vector_path
    
    def setVector(self, vector: str, /):
        self._vector = vector
        self._vector_path = None
        self._adjust()

    def setVectorPath(self, vector_path: str, /):
        self._vector_path = vector_path
        self._vector = None
        self._adjust()

    def _adjust(self):
        """Adjust visuals in response to changes."""
        self.updateView()

        if self.vector() is not None:
            if self.vector() == "":
                self.setDescription("No Matrix")
            else:
                self.setDescription(self.vector())
        else:
            if self.vectorPath() == "":
                self.setDescription("No Matrix")
            else:
                self.setDescription(self.vectorPath())


    # Serialization ====================================================================================================
    def add_nfb_export_data(self, signal: dict):
        """Add this node's data to the dict representation of the signal."""
        if self.vector() is not None:
            signal["SpatialFilterMatrix"] = self.vector()
        else:
            signal["SpatialFilterMatrix"] = self.vectorPath()
    
    def serialize(self) -> dict:
        data = super().serialize()

        data["vector"] = self.vector()
        data["vector_path"] = self.vectorPath()
        return data
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = super().deserialize(data)
        if data["vector"] is not None:
            obj.setVector(data["vector"])
        else:
            obj.setVectorPath(data["vector_path"])

        return obj
