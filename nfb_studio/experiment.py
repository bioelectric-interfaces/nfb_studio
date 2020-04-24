from enum import Enum, auto
from collections import MutableSequence

from PySide2.QtCore import Qt, Signal, QObject, QAbstractItemModel, QModelIndex
from PySide2.QtWidgets import QTreeView
from sortedcontainers import SortedDict

from .property_tree import PropertyTree

from .widgets.signal import SignalEditor


class Block(QObject):
    """A single step of an experiment.
    Experiment consists of a sequence of blocks and block groups that are executed in some order.
    """

    FeedbackSourceAll = object()
    """A sentinel object marking that self.feedback_source is all sources."""

    class FeedbackType(Enum):
        """Possible values for self.feedback_type."""
        Baseline = 0
        Feedback = auto()
    
    class RandomBound(Enum):
        """Possible values for self.random_bound."""
        SimCircle = 0
        RandomCircle = auto()
        Bar = auto()

    attrchanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # General ------------------------------------------------------------------------------------------------------
        self.name = "Block"
        self.duration = 10.0
        self.feedback_source = self.FeedbackSourceAll
        self.feedback_type = self.FeedbackType.Baseline
        self.random_bound = self.RandomBound.SimCircle
        self.video_path = ""

        # Mock signal --------------------------------------------------------------------------------------------------
        self.mock_signal_path = ""
        self.mock_signal_dataset = ""
        self.mock_previous = 0
        self.mock_previous_reverse = False
        self.mock_previous_random = False

        # After block actions ------------------------------------------------------------------------------------------
        self.start_data_driven_filter_designer = False
        self.pause = False
        self.beep = False
        self.update_statistics = False


class Group(QObject, MutableSequence):
    """A group of experiment blocks.
    Experiment consists of a sequence of blocks and block groups that are executed in some order. A group consists of
    a sequence of blocks. Each block can be repeated one or more times, and can be set to execute in random order.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.name = "Group"
        self.blocks = []
        self.repeats = []

        self.random_order = False

    # MutableSequence method implementations ---------------------------------------------------------------------------
    def __getitem__(self, index):
        return (self.blocks[index], self.repeats[index])
    
    def __setitem__(self, index, value):
        del self[index]
        self.insert(index, value)
    
    def __delitem__(self, index):
        del self.blocks[index]
        del self.repeats[index]
    
    def __len__(self):
        assert len(self.blocks) == len(self.repeats)
        return len(self.blocks)
    
    def insert(self, index, value):
        if isinstance(value, Block):
            value = (value, 1)
        
        self.blocks.insert(index, value[0])
        self.repeats.insert(index, value[1])


class Experiment(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "Experiment"
        self.inlet = "nvx"
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
