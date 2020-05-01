"""NFB Experiment."""
from PySide2.QtCore import Qt, Signal, QObject, QAbstractItemModel, QModelIndex
from PySide2.QtWidgets import QTreeView
from sortedcontainers import SortedDict

from nfb_studio.serial import xml, hooks

from .property_tree import PropertyTree
from .widgets.signal import SignalEditor
from .block import Block
from .group import Group


class Experiment(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "Experiment"
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

        self.blocks = set()
        self.groups = set()
        self.sequence = []
    
    def nfb_export_data(self) -> dict:
        data = {}

        data["sExperimentName"] = self.name
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

        return data

    def export(self) -> str:
        data = {"NeurofeedbackSignalSpecs": self}

        enc_hooks = {
            Experiment: Experiment.nfb_export_data,
            Block: Block.nfb_export_data,
            Group: Group.nfb_export_data,
            bool: lambda x: {"#text": int(x)}
        }

        encoder = xml.XMLEncoder(separator="\n", indent="\t", metadata=False, hooks=enc_hooks)

        return encoder.encode(data)
