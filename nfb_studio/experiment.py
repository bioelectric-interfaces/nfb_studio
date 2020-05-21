"""NFB Experiment."""
from PySide2.QtCore import Qt, Signal, QObject, QAbstractItemModel, QModelIndex
from PySide2.QtWidgets import QTreeView
from sortedcontainers import SortedDict

from nfb_studio.serial import json, xml, hooks

from .property_tree import PropertyTree
from .widgets.scheme import SchemeEditor, Scheme
from .block import Block
from .group import Group
from .widgets.signal_nodes import *
from .widgets.sequence_nodes import *


class Experiment(QObject):
    inlet_type_export_values = {
        "LSL stream": "lsl",
        "LSL file stream": "lsl_from_file",
        "LSL generator": "lsl_generator",
        "Field trip buffer": "ftbuffer"
    }
    inlet_type_import_values = {v: k for k, v in inlet_type_export_values.items()}

    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "Experiment"
        self.lsl_stream_name = "NVX136_Data"
        self.inlet = "lsl"
        self.raw_data_path = ""
        self.hostname_port = ""
        self.dc = False
        self.prefilter_band = (None, None)
        self.plot_raw = False
        self.plot_signals = False
        self.show_subject_window = False
        self.discard_channels = ""
        self.reference_sub = ""
        self.show_proto_rectangle = False
        self.show_notch_filters = False

        self.signal_scheme = Scheme()
        self.sequence_scheme = Scheme()
        self.blocks = set()
        self.groups = set()
    
    def nfb_export_data(self) -> dict:
        data = {}

        data["sExperimentName"] = self.name
        data["sStreamName"] = self.lsl_stream_name
        data["sPrefilterBand"] = str(self.prefilter_band[0]) + " " + str(self.prefilter_band[1])
        data["bDC"] = self.dc
        data["sInletType"] = self.inlet
        data["sRawDataFilePath"] = self.raw_data_path
        data["sFTHostnamePort"] = self.hostname_port
        data["bPlotRaw"] = self.plot_raw
        data["bPlotSignals"] = self.plot_signals
        data["bPlotSourceSpace"] = 0
        data["bShowSubjectWindow"] = self.show_subject_window
        data["fRewardPeriodS"] = 0.25
        data["sReference"] = self.discard_channels
        data["sReferenceSub"] = self.reference_sub
        data["bUseExpyriment"] = 0
        data["bShowPhotoRectangle"] = self.show_proto_rectangle
        data["sVizNotchFilters"] = self.show_notch_filters

        data["vProtocols"] = {
            "FeedbackProtocol": list(self.blocks)
        }

        data["vPGroups"] = {
            "PGroup": list(self.groups)
        }

        # Signals ------------------------------------------------------------------------------------------------------
        signals = []

        # Build a list of lists of nodes (e.g. list of sequences)
        for node in self.signal_scheme.graph.nodes:
            if isinstance(node, DerivedSignalExport):
                signal = []
                n = node

                while True:
                    signal.append(n)

                    if len(n.inputs) == 0:
                        break
                    
                    n = list(n.inputs[0].edges)[0].sourceNode()
                
                signals.append(signal)
        
        # Convert list of lists of nodes to a list of serialized signals
        for i in range(len(signals)):
            signal = {}

            for node in signals[i]:
                if isinstance(node, LSLInput):
                    pass  # TODO: What to export for LSLInput?
                elif isinstance(node, SpatialFilter):
                    signal["SpatialFilterMatrix"] = node.configWidget().matrix_path.text()
                elif isinstance(node, BandpassFilter):
                    signal["fBandpassLowHz"] = None
                    if node.configWidget().fBandpassLowHz_enable.isChecked():
                        signal["fBandpassLowHz"] = node.configWidget().fBandpassLowHz_input.value()
                    
                    signal["fBandpassHighHz"] = None
                    if node.configWidget().fBandpassHighHz_enable.isChecked():
                        signal["fBandpassHighHz"] = node.configWidget().fBandpassHighHz_input.value()
                elif isinstance(node, EnvelopeDetector):
                    signal["fSmoothingFactor"] = node.configWidget().smoothing_factor.value()
                    signal["method"] = node.configWidget().method.currentText()
                elif isinstance(node, Standardise):
                    signal["fAverage"] = node.configWidget().fAverage_input.value()
                    signal["fStdDev"] = node.configWidget().fStdDev_input.value()
                elif isinstance(node, DerivedSignalExport):
                    signal["sSignalName"] = node.configWidget().signalName_input.text()
            
            signals[i] = signal
            print(signal)

        data["vSignals"] = {
            "DerivedSignal": signals
        }

        # Experiment sequence ------------------------------------------------------------------------------------------
        sequence = []
        
        # Determine the start node of the sequence and put it in `n`
        n = next(iter(self.sequence_scheme.graph.nodes))
        while len(n.inputs[0].edges) > 0:
            n = list(n.inputs[0].edges)[0].sourceNode()
        
        # For each node in sequence, append it's title as next item in sequence
        sequence.append(n.title())
        while len(n.outputs[0].edges) > 0:
            n = list(n.outputs[0].edges)[0].targetNode()
            sequence.append(n.title())

        data["vPSequence"] = {
            "s": sequence
        }

        return data

    def export(self) -> str:
        data = {"NeurofeedbackSignalSpecs": self}

        enc_hooks = {
            Experiment: Experiment.nfb_export_data,
            Block: Block.nfb_export_data,
            Group: Group.nfb_export_data,
            bool: lambda x: {"#text": str(int(x))}
        }

        encoder = xml.XMLEncoder(separator="\n", indent="\t", metadata=False, hooks=enc_hooks)

        return encoder.encode(data)
