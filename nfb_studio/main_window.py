from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QMainWindow, QDockWidget, QStackedWidget, QAction
from .experiment import Experiment
from .widgets.signal import SignalEditor
from .property_tree import PropertyTree
from .widgets.config import BlockConfig, GroupConfig, ExperimentConfig
from .block import Block
from .group import Group
from .widgets.signal_nodes import *
from nfb_studio.util.qt.tree_model import TreeModelItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.experiment = Experiment()

        # Property tree ------------------------------------------------------------------------------------------------
        self.property_tree = PropertyTree()
        self.property_tree_view = self.property_tree.view()
        self.property_tree_view.clicked.connect(self.setCurrentIndex)

        self.property_tree_dock = QDockWidget("Properties", self)
        self.property_tree_dock.setWidget(self.property_tree_view)
        self.property_tree_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.property_tree_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.property_tree_dock)

        # Editing widgets ----------------------------------------------------------------------------------------------
        self.experiment_config = ExperimentConfig(self.experiment)
        
        self.signal_editor = SignalEditor()
        self.signal_editor.toolbox.addItem("LSL Input", LSLInput())
        self.signal_editor.toolbox.addItem("Spatial Filter", SpatialFilter())
        self.signal_editor.toolbox.addItem("Bandpass Filter", BandpassFilter())
        self.signal_editor.toolbox.addItem("Envelope Detector", EnvelopeDetector())
        self.signal_editor.toolbox.addItem("Standardise", Standardise())
        self.signal_editor.toolbox.addItem("Signal Export", DerivedSignalExport())

        self.block_stack = QStackedWidget()
        self.group_stack = QStackedWidget()

        # Central widget -----------------------------------------------------------------------------------------------
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.experiment_config)
        self.central_widget.addWidget(self.signal_editor)
        self.central_widget.addWidget(self.block_stack)
        self.central_widget.addWidget(self.group_stack)

        # Signals ------------------------------------------------------------------------------------------------------
        self.property_tree_view.blocktree_menu_add_action.triggered.connect(self.addBlock)
        self.property_tree_view.grouptree_menu_add_action.triggered.connect(self.addGroup)

        # Menu bar -----------------------------------------------------------------------------------------------------
        menubar = self.menuBar()
        filemenu = menubar.addMenu("File")
        export = filemenu.addAction("Export")
        export.triggered.connect(self.export)


    def setCurrentIndex(self, index: QModelIndex):
        """Set central widget in the main window to display config info for item at `index` in the property tree."""
        self.property_tree_view.setCurrentIndex(index)

        item = self.property_tree.item(index)
        
        if item is self.property_tree.general_item:
            self.central_widget.setCurrentIndex(0)
        if item is self.property_tree.signals_item:
            self.central_widget.setCurrentIndex(1)
        elif item.parent() is self.property_tree.blocks_item:
            self.central_widget.setCurrentIndex(2)
            self.block_stack.setCurrentIndex(index.row())
        elif item.parent() is self.property_tree.groups_item:
            self.central_widget.setCurrentIndex(3)
            self.group_stack.setCurrentIndex(index.row())

    def addBlock(self):
        block = Block()
        block_config = BlockConfig(block)

        self.experiment.blocks.add(block)

        tree_item = TreeModelItem()
        tree_item.setText(block.name)
        self.property_tree.blocks_item.addItem(tree_item)

        self.block_stack.addWidget(block_config)
    
    def addGroup(self):
        group = Group()
        group_config = GroupConfig(group)

        self.experiment.groups.add(group)

        tree_item = TreeModelItem()
        tree_item.setText(group.name)
        self.property_tree.groups_item.addItem(tree_item)

        self.group_stack.addWidget(group_config)

    def export(self):
        for i in range(self.block_stack.count()):
            block_config: BlockConfig = self.block_stack.widget(i)
            block: Block = block_config.data

            block.duration = block_config.duration.value()
            block.feedback_source = block_config.feedback_source.text()
            block.feedback_type = block_config.feedback_type.currentText()
            block.random_bound = block_config.random_bound.currentText()
            block.video_path = block_config.video_path.text()
            block.mock_signal_path = block_config.mock_signal_path.text()
            block.mock_signal_dataset = block_config.mock_signal_dataset.text()
            block.mock_previous = block_config.mock_previous.value()
            block.mock_previous_reverse = block_config.mock_previous_reverse.isChecked()
            block.mock_previous_random = block_config.mock_previous_random.isChecked()
            block.start_data_driven_filter_designer = block_config.start_data_driven_filter_designer.isChecked()
            block.pause = block_config.pause.isChecked()
            block.beep = block_config.beep.isChecked()
            block.update_statistics = block_config.update_statistics.isChecked()
        
        for i in range(self.group_stack.count()):
            group_config: GroupConfig = self.group_stack.widget(i)
            group: Group = group_config.data

            group.name = group_config.name.text()
            group.random_order = group_config.random_order.isChecked()
            if group_config.blocks.text() == "":
                group.blocks = []
                group.repeats = []
            else:
                group.blocks = group_config.blocks.text().split(" ")
                group.repeats = [int(number) for number in group_config.repeats.text().split(" ")]

        self.experiment.name = self.experiment_config.name.text()
        self.experiment.inlet = self.experiment_config.inlet_type_export_values[self.experiment_config.inlet_type_selector.currentText()]
        self.experiment.lsl_stream_name = self.experiment_config.lsl_stream_name.currentText()
        self.experiment.raw_data_path = self.experiment_config.lsl_filename.text()
        self.experiment.hostname_port = self.experiment_config.hostname_port.text()
        self.experiment.dc = self.experiment_config.dc.isChecked()
        
        if self.experiment_config.prefilterBandLow_enable.isChecked():
            prefilterBandLow = self.experiment_config.prefilterBandLow_input.value()
        else:
            prefilterBandLow = None
        
        if self.experiment_config.prefilterBandHigh_enable.isChecked():
            prefilterBandHigh = self.experiment_config.prefilterBandHigh_input.value()
        else:
            prefilterBandHigh = None
        
        self.experiment.prefilter_band = (prefilterBandLow, prefilterBandHigh)
        self.experiment.plot_raw = self.experiment_config.plot_raw.isChecked()
        self.experiment.plot_signals = self.experiment_config.plot_signals.isChecked()
        self.experiment.show_subject_window = self.experiment_config.show_subject_window.isChecked()
        self.experiment.discard_channels = self.experiment_config.discard_channels.text()
        self.experiment.reference_sub = self.experiment_config.reference_sub.text()
        self.experiment.show_proto_rectangle = self.experiment_config.show_proto_rectangle.isChecked()
        self.experiment.show_notch_filters = self.experiment_config.show_notch_filters.isChecked()

        self.experiment.sequence = self.experiment_config.sequence.text().split(" ")

        signals = []
        for node in self.signal_editor.scheme.graph.nodes:
            if isinstance(node, DerivedSignalExport):
                signal = []
                n = node

                while(True):
                    signal.append(n)

                    if len(n.inputs) == 0:
                        break
                    else:
                        n = list(n.inputs[0].edges)[0].sourceNode()
                
                signals.append(signal)
        
        for i in range(len(signals)):
            data = {}

            for node in signals[i]:
                if isinstance(node, LSLInput):
                    pass  # TODO: What to export for LSLInput?
                elif isinstance(node, SpatialFilter):
                    data["SpatialFilterMatrix"] = node.configWidget().matrix_path.text()
                elif isinstance(node, BandpassFilter):
                    data["fBandpassLowHz"] = None
                    if node.configWidget().fBandpassLowHz_enable.isChecked():
                        data["fBandpassLowHz"] = node.configWidget().fBandpassLowHz_input.value()

                    data["fBandpassHighHz"] = None
                    if node.configWidget().fBandpassHighHz_enable.isChecked():
                        data["fBandpassHighHz"] = node.configWidget().fBandpassHighHz_input.value()
                elif isinstance(node, EnvelopeDetector):
                    data["fSmoothingFactor"] = node.configWidget().fSmoothingFactor_input.value()
                elif isinstance(node, Standardise):
                    data["fAverage"] = node.configWidget().fAverage_input.value()
                    data["fStdDev"] = node.configWidget().fStdDev_input.value()
                elif isinstance(node, DerivedSignalExport):
                    data["sSignalName"] = node.configWidget().signalName_input.text()
            
            signals[i] = data
        
        self.experiment.signals = signals

        print(self.experiment.export())

        