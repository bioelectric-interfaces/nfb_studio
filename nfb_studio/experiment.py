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
        self.dc = False  # TODO: A more descriptive name?
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
    
    def serialize(self) -> dict:
        return {
            "name": self.name,
            "lsl_stream_name": self.lsl_stream_name,
            "inlet": self.inlet,
            "raw_data_path": self.raw_data_path,
            "hostname_port": self.hostname_port,
            "dc": self.dc,
            "prefilter_band_lower_bound": self.prefilter_band[0],
            "prefilter_band_upper_bound": self.prefilter_band[1],
            "plot_raw": self.plot_raw,
            "plot_signals": self.plot_signals,
            "show_subject_window": self.show_subject_window,
            "discard_channels": self.discard_channels,
            "reference_sub": self.reference_sub,
            "show_proto_rectangle": self.show_proto_rectangle,
            "show_notch_filters": self.show_notch_filters,
            "signal_scheme": self.signal_scheme,
            "sequence_scheme": self.sequence_scheme,
            "blocks": list(self.blocks),
            "groups": list(self.groups),
        }
    
    def deserialize(self, data: dict):
        self.name = data["name"]
        self.lsl_stream_name = data["lsl_stream_name"]
        self.inlet = data["inlet"]
        self.raw_data_path = data["raw_data_path"]
        self.hostname_port = data["hostname_port"]
        self.dc = data["dc"]
        self.prefilter_band = (data["prefilter_band_lower_bound"], data["prefilter_band_upper_bound"])
        self.plot_raw = data["plot_raw"]
        self.plot_signals = data["plot_signals"]
        self.show_subject_window = data["show_subject_window"]
        self.discard_channels = data["discard_channels"]
        self.reference_sub = data["reference_sub"]
        self.show_proto_rectangle = data["show_proto_rectangle"]
        self.show_notch_filters = data["show_notch_filters"]
        self.signal_scheme = data["signal_scheme"]
        self.sequence_scheme = data["sequence_scheme"]
        self.blocks = set(data["blocks"])
        self.groups = set(data["groups"])

    def nfb_export_data(self) -> dict:
        """Export data in a dict format for encoding to XML and usage in NFBLab."""
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
                node.add_nfb_export_data(signal)
            
            signals[i] = signal

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

    def save(self) -> str:
        encoder = json.JSONEncoder(separator="\n", indent="\t", hooks=hooks.qt)

        return encoder.encode(self)