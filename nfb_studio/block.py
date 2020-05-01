"""NFB Experiment block."""
from enum import Enum, auto

from PySide2.QtCore import QObject, Signal


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
    
    def nfb_export_data(self) -> dict:
        """Export this block into a dict to be encoded as XML for NFBLab.
        Bool items are written as-is. The encoder is responsible for converting them into int format.
        """
        data = {}

        data["sProtocolName"] = self.name
        data["bUpdateStatistics"] = self.update_statistics
        data["iDropOutliers"] = 0
        data["bSSDInTheEnd"] = self.start_data_driven_filter_designer
        data["fDuration"] = self.duration
        data["sFb_type"] = self.feedback_type
        data["cString"] = ""
        data["bUseExtraMessage"] = 0
        data["cString2"] = ""
        data["fBlinkDurationMs"] = 50
        data["fBlinkThreshold"] = 0
        data["sMockSignalFilePath"] = self.mock_signal_path
        data["sMockSignalFileDataset"] = self.mock_signal_dataset
        data["iMockPrevious"] = self.mock_previous
        data["bReverseMockPrevious"] = self.mock_previous_reverse
        data["bRandomMockPrevious"] = self.mock_previous_random
        data["bRewardThreshold"] = 0
        data["bShowReward"] = 0
        data["bPauseAfter"] = self.pause
        data["bBeepAfter"] = self.beep
        data["iRandomBound"] = self.random_bound
        data["sVideoPath"] = self.video_path
        data["sMSignal"] = "None"
        data["fMSignalThreshold"] = 1

        if self.feedback_source is self.FeedbackSourceAll:
            data["fbSource"] = "All"
        else:
            # TODO: What to export when feedback_source is not "All"?
            raise NotImplementedError

        return data
    
    def nfb_import_data(self, data: dict):
        """Import this block from a dict from NFBLab.
        Since the XML file stores everything as a string, this function is responsible for converting items to their
        proper types.
        """

        self.name = data["sProtocolName"]
        self.update_statistics = bool(int(data["bUpdateStatistics"]))
        self.start_data_driven_filter_designer = bool(int(data["bSSDInTheEnd"]))
        self.duration = float(data["fDuration"])
        self.feedback_type = int(data["sFb_type"])
        self.mock_signal_path = data["sMockSignalFilePath"]
        self.mock_signal_dataset = data["sMockSignalFileDataset"]
        self.mock_previous = int(data["iMockPrevious"])
        self.mock_previous_reverse = bool(int(data["bReverseMockPrevious"]))
        self.mock_previous_random = bool(int(data["bRandomMockPrevious"]))
        self.pause = bool(int(data["bPauseAfter"]))
        self.beep = bool(int(data["bBeepAfter"]))
        self.random_bound = int(data["iRandomBound"])
        self.video_path = data["sVideoPath"]

        if data["fbSource"] == "All":
            self.feedback_source = self.FeedbackSourceAll
        else:
            # TODO: What to import when feedback_source is not "All"?
            raise NotImplementedError
