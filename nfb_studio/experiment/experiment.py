"""NFB Experiment."""
import re

from nfb_studio.block import Block, BlockDict
from nfb_studio.group import Group, GroupDict
from nfb_studio.serial import json, xml, hooks
from nfb_studio.widgets.scheme import Scheme
from nfb_studio.widgets.signal_nodes import *
from nfb_studio.widgets.sequence_nodes import *


class Experiment:
    """NFB Experiment: the main class of nfb_studio.
    An instance of Experiment represents a collection
    """
    inlet_type_export_values = {
        "LSL stream": "lsl",
        "LSL file stream": "lsl_from_file",
        "LSL generator": "lsl_generator",
        "Field trip buffer": "ftbuffer"
    }
    inlet_type_import_values = {v: k for k, v in inlet_type_export_values.items()}

    def __init__(self):
        self.name = "Experiment"
        self.lsl_stream_name = "NVX136_Data"
        self.inlet = "lsl"
        self.raw_data_path = ""
        self.hostname_port = ""
        self.dc = False  # TODO: A more descriptive name?
        self.prefilter_band = [None, None]
        self.plot_raw = True
        self.plot_signals = True
        self.show_subject_window = True
        self.discard_channels = ""
        self.reference_sub = ""
        self.show_proto_rectangle = False
        self.show_notch_filters = False

        self.signal_scheme = Scheme()
        self.sequence_scheme = Scheme()
        self.blocks = BlockDict()
        self.groups = GroupDict()

        self.blocks.setExperiment(self)
        self.groups.setExperiment(self)

        self._view = None
    
    def checkName(self, name: str):
        """Check if a name is appropriate for adding a new block or group.
        Returns a bool (name good or not) and a reason why the name is not good (or None).
        """
        if name == "":
            return (False, "Name cannot be blank.")
        
        if " " in name:
            return (False, "Name cannot contain spaces.")

        match = re.search(r"([^A-Za-z0-9_])", name)
        if match:
            return (False, "Illegal character '{}'".format(match.group(0)))

        if name in self.blocks or name in self.groups:
            return (False, "Name already in use.")
        
        return (True, None)

    # Access functions =================================================================================================
    def view(self):
        return self._view
    
    def setView(self, view, /):
        view.setModel(self)
    
    # Serialization ====================================================================================================
    def export(self) -> str:
        data = {"NeurofeedbackSignalSpecs": self}

        enc_hooks = {
            Experiment: Experiment.nfb_export_data,
            Block: Block.nfb_export_data,
            Group: Group.nfb_export_data,
            bool: lambda x: int(x)
        }

        encoder = xml.XMLEncoder(separator="\n", indent="\t", metadata=False, hooks=enc_hooks)

        return encoder.encode(data)

    def save(self) -> str:
        encoder = json.JSONEncoder(separator="\n", indent="\t", hooks=hooks.qt)

        return encoder.encode(self)
    
    @classmethod
    def load(cls, data: str):
        decoder = json.JSONDecoder(hooks=hooks.qt)
        return decoder.decode(data)

    @classmethod
    def import_xml(cls, xml_string: str):
        """Decode an XML string containing an exported file into an nfb_studio experiment.
        Decoding xml files is an imperfect science, since nfb_studio has more information, like node position, their
        connections, and so on. This function does it's best to at least produce the correct experiment flow.
        """
        ex = cls()

        # Decode the string --------------------------------------------------------------------------------------------
        decoder = xml.XMLDecoder(force_list=("DerivedSignal", "CompositeSignal", "FeedbackProtocol", "PGroup", "s"))
        root = decoder.decode(xml_string)
        data = next(iter(root.values()))  # Get first (and only) value in root

        # Add empty signal/block/group/sequence lists if they are missing ----------------------------------------------
        if data["vSignals"] is None:
            data["vSignals"] = {
                "DerivedSignal": [],
                "CompositeSignal": [],
            }
        else:
            if "DerivedSignal" not in data["vSignals"]:
                data["vSignals"]["DerivedSignal"] = []
            if "CompositeSignal" not in data["vSignals"]:
                data["vSignals"]["CompositeSignal"] = []
        
        if data["vProtocols"] is None:
            data["vProtocols"] = {"FeedbackProtocol": []}
        if data["vPGroups"] is None:
            data["vPGroups"] = {"PGroup": []}
        if data["vPSequence"] is None:
            data["vPSequence"] = {"s": []}

        # Decode main experiment properties ----------------------------------------------------------------------------
        ex.name = data["sExperimentName"]
        ex.lsl_stream_name = data["sStreamName"]

        if "sPrefilterBand" in data:
            prefilter_band_values = data["sPrefilterBand"].split(" ")
            if prefilter_band_values[0] == "None":
                ex.prefilter_band[0] = None
            else:
                ex.prefilter_band[0] = float(prefilter_band_values[0])

            if prefilter_band_values[1] == "None":
                ex.prefilter_band[1] = None
            else:
                ex.prefilter_band[1] = float(prefilter_band_values[1])

        ex.dc = bool(float(data["bDC"]))
        ex.inlet = data["sInletType"]
        ex.raw_data_path = data["sRawDataFilePath"]
        ex.hostname_port = data["sFTHostnamePort"]
        ex.plot_raw = bool(float(data["bPlotRaw"]))
        ex.plot_signals = bool(float(data["bPlotSignals"]))
        ex.show_subject_window = bool(float(data.get("bShowSubjectWindow", ex.show_subject_window)))
        ex.discard_channels = data["sReference"]
        ex.reference_sub = data["sReferenceSub"]
        ex.show_proto_rectangle = bool(float(data.get("bShowPhotoRectangle", ex.show_proto_rectangle)))
        ex.show_notch_filters = bool(float(data.get("sVizNotchFilters", ex.show_notch_filters)))

        # Decode signals -----------------------------------------------------------------------------------------------
        node_pos = [0, 0]
        node_xdiff = -100  # TODO: Change to a size dependent on node default width
        node_ydiff = 100

        for signal_data in data["vSignals"]["DerivedSignal"]:
            # Assemble the signal front to back, starting with the signal name.
            # Some nodes may not be present, this loop accounts for it.
            if "sSignalName" in signal_data:
                # Create the node and set variables from data
                n = DerivedSignalExport()
                n.setSignalName(signal_data["sSignalName"])

                # Set position and add to scheme
                n.setPos(*node_pos)
                node_pos[0] += node_xdiff

                ex.signal_scheme.addItem(n)
            if (signal_data.get("fAverage") is not None) or (signal_data.get("fStdDev") is not None):
                last = n
                n = Standardise()
                n.setAverage(float(signal_data.get("fAverage", n.default_average)))
                n.setStandardDeviation(float(signal_data.get("fStdDev", n.default_standard_deviation)))

                n.setPos(*node_pos)
                node_pos[0] += node_xdiff

                ex.signal_scheme.addItem(n)
                ex.signal_scheme.connect_nodes(n.outputs[0], last.inputs[0])
            if ("fSmoothingFactor" in signal_data) or ("method" in signal_data):
                last = n
                n = EnvelopeDetector()
                n.setSmoothingFactor(float(signal_data.get("fSmoothingFactor", n.default_smoothing_factor)))
                n.setMethod(signal_data.get("method", n.default_method))

                n.setPos(*node_pos)
                node_pos[0] += node_xdiff

                ex.signal_scheme.addItem(n)
                ex.signal_scheme.connect_nodes(n.outputs[0], last.inputs[0])
            if ("fBandpassLowHz" in signal_data) or ("fBandpassHighHz" in signal_data):
                last = n
                n = BandpassFilter()
                n.setLowerBound(float(signal_data.get("fBandpassLowHz", n.default_lower_bound)))
                n.setUpperBound(float(signal_data.get("fBandpassHighHz", n.default_upper_bound)))

                n.setPos(*node_pos)
                node_pos[0] += node_xdiff

                ex.signal_scheme.addItem(n)
                ex.signal_scheme.connect_nodes(n.outputs[0], last.inputs[0])
            if "SpatialFilterMatrix" in signal_data:
                last = n
                n = SpatialFilter()
                n.setMatrixPath(signal_data["SpatialFilterMatrix"])

                n.setPos(*node_pos)
                node_pos[0] += node_xdiff

                ex.signal_scheme.addItem(n)
                ex.signal_scheme.connect_nodes(n.outputs[0], last.inputs[0])
            # Unconditionally add LSLInput
            last = n
            n = LSLInput()

            n.setPos(*node_pos)
            node_pos[0] += node_xdiff

            ex.signal_scheme.addItem(n)
            ex.signal_scheme.connect_nodes(n.outputs[0], last.inputs[0])

            # Bump vertial coordinates to prepare for a new signal
            node_pos[0] = 0
            node_pos[1] += node_ydiff

        # Add composite signals separately
        for comp_data in data["vSignals"]["CompositeSignal"]:
            n = CompositeSignalExport()
            n.setSignalName(comp_data["sSignalName"])
            n.setExpression(comp_data["sExpression"])

            # Set position and add to scheme
            n.setPos(*node_pos)
            node_pos[0] = 0
            node_pos[1] += node_ydiff

            ex.signal_scheme.addItem(n)

        # Decode blocks ------------------------------------------------------------------------------------------------
        for block_data in data["vProtocols"]["FeedbackProtocol"]:
            block = Block.nfb_import_data(block_data)
            name = block_data["sProtocolName"]
            ex.blocks[name] = block
        
        # Decode groups ------------------------------------------------------------------------------------------------
        for group_data in data["vPGroups"]["PGroup"]:
            group = Group.nfb_import_data(group_data)
            name = group_data["sName"]
            ex.groups[name] = group
        
        # Decode sequence ----------------------------------------------------------------------------------------------
        node = None
        node_pos = [0, 0]
        node_xdiff = 100

        for name in data["vPSequence"]["s"]:
            last = node

            if name in ex.blocks:
                node = BlockNode()
            else:
                node = GroupNode()

            node.setTitle(name)
            node.setPos(*node_pos)
            node_pos[0] += node_xdiff

            ex.sequence_scheme.addItem(node)

            if last is not None:
                ex.sequence_scheme.connect_nodes(last.outputs[0], node.inputs[0])

        # --------------------------------------------------------------------------------------------------------------
        return ex

    def updateView(self):
        view = self.view()
        if view is None:
            return

        # General properties -------------------------------------------------------------------------------------------
        general = view.general_view
        
        general.name.setText(self.name)
        general.inlet_type.setCurrentText(general.inlet_type_import_values[self.inlet])
        general.lsl_stream_name.setCurrentText(self.lsl_stream_name)
        general.lsl_filename.setText(self.raw_data_path)
        general.hostname_port.setText(self.hostname_port)
        general.dc.setChecked(self.dc)

        if self.prefilter_band[0] is None:
            general.prefilterBandLow_enable.setChecked(False)
            general.prefilterBandLow_input.setValue(0)
        else:
            general.prefilterBandLow_enable.setChecked(True)
            general.prefilterBandLow_input.setValue(self.prefilter_band[0])
        
        if self.prefilter_band[1] is None:
            general.prefilterBandHigh_enable.setChecked(False)
            general.prefilterBandHigh_input.setValue(0)
        else:
            general.prefilterBandHigh_enable.setChecked(True)
            general.prefilterBandHigh_input.setValue(self.prefilter_band[1])
        
        general.plot_raw.setChecked(self.plot_raw)
        general.plot_signals.setChecked(self.plot_signals)
        general.show_subject_window.setChecked(self.show_subject_window)
        general.discard_channels.setText(self.discard_channels)
        general.reference_sub.setText(self.reference_sub)
        general.show_proto_rectangle.setChecked(self.show_proto_rectangle)
        general.show_notch_filters.setChecked(self.show_notch_filters)

        # Blocks and groups --------------------------------------------------------------------------------------------
        while view.tree.blocks.rowCount() > 0:
            name = view.tree.blocks.child(0).text(0)
            view.tree.blocks.takeChild(0)
            view.blocks.removeWidget(name)
            view.sequence_editor.toolbox().removeItem(name)
        
        while view.tree.groups.rowCount() > 0:
            name = view.tree.groups.child(0).text(0)
            view.tree.groups.takeChild(0)
            view.groups.removeWidget(name)
            view.sequence_editor.toolbox().removeItem(name)

        for name in self.blocks:
            self.blocks.itemAdded.emit(name)
        
        for name in self.groups:
            self.groups.itemAdded.emit(name)

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
            "blocks": self.blocks,
            "groups": self.groups,
        }
    
    @classmethod
    def deserialize(cls, data: dict):
        obj = cls()

        obj.name = data["name"]
        obj.lsl_stream_name = data["lsl_stream_name"]
        obj.inlet = data["inlet"]
        obj.raw_data_path = data["raw_data_path"]
        obj.hostname_port = data["hostname_port"]
        obj.dc = data["dc"]
        obj.prefilter_band = (data["prefilter_band_lower_bound"], data["prefilter_band_upper_bound"])
        obj.plot_raw = data["plot_raw"]
        obj.plot_signals = data["plot_signals"]
        obj.show_subject_window = data["show_subject_window"]
        obj.discard_channels = data["discard_channels"]
        obj.reference_sub = data["reference_sub"]
        obj.show_proto_rectangle = data["show_proto_rectangle"]
        obj.show_notch_filters = data["show_notch_filters"]
        obj.signal_scheme = data["signal_scheme"]
        obj.sequence_scheme = data["sequence_scheme"]
        obj.blocks = data["blocks"]
        obj.groups = data["groups"]

        obj.blocks.setExperiment(obj)
        obj.groups.setExperiment(obj)

        return obj

    def nfb_export_data(self) -> dict:
        """Export data in a dict format for encoding to XML and usage in NFBLab."""
        data = {}

        # General ------------------------------------------------------------------------------------------------------
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

        # Blocks -------------------------------------------------------------------------------------------------------
        data["vProtocols"] = {
            "FeedbackProtocol": []
        }

        for name in self.blocks:
            block = self.blocks[name]

            data["vProtocols"]["FeedbackProtocol"].append(block.nfb_export_data())  # Add other information
            data["vProtocols"]["FeedbackProtocol"][-1]["sProtocolName"] = name  # Add name

        # Groups -------------------------------------------------------------------------------------------------------
        data["vPGroups"] = {
            "PGroup": list(self.groups)
        }

        for name in self.groups:
            group = self.groups[name]

            data["vProtocols"]["FeedbackProtocol"].append(group.nfb_export_data())  # Add other information
            data["vProtocols"]["FeedbackProtocol"][-1]["sName"] = name  # Add name

        # Derived Signals ----------------------------------------------------------------------------------------------
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

        # Composite signals --------------------------------------------------------------------------------------------
        signals = []

        for node in self.signal_scheme.graph.nodes:
            if isinstance(node, CompositeSignalExport):
                signal = {}
                node.add_nfb_export_data(signal)
                signals.append(signal)
        
        data["vSignals"]["CompositeSignal"] = signals

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
