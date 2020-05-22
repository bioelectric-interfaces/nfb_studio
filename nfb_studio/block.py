"""NFB Experiment block."""
import itertools
from enum import Enum, auto

from PySide2.QtCore import QObject, Signal


class Block(QObject):
    """A single step of an experiment.
    Experiment consists of a sequence of blocks and block groups that are executed in some order.
    """
    newid = itertools.count()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # General ------------------------------------------------------------------------------------------------------
        self.name = "Block" + str(next(self.newid))
        self.duration = 10.0
        self.feedback_source = "All"
        self.feedback_type = "Baseline"
        self.random_bound = "SimCircle"
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

        # --------------------------------------------------------------------------------------------------------------
        self._view = None
    
    def view(self):
        """Return the view (config widget) for this block."""
        return self._view

    def setView(self, view, /):
        view.setModel(self)

    def sync(self):
        view = self.view()
        if view is None:
            return
        
        view.name.setText(self.name)
        view.duration.setValue(self.duration)
        view.feedback_source.setText(self.feedback_source)
        view.feedback_type.setCurrentText(self.feedback_type)
        view.mock_signal_path.setText(self.mock_signal_path)
        view.mock_signal_dataset.setText(self.mock_signal_dataset)
        view.mock_previous.setValue(self.mock_previous)
        view.mock_previous_reverse.setChecked(self.mock_previous_reverse)
        view.mock_previous_random.setChecked(self.mock_previous_random)
        view.pause.setChecked(self.pause)
        view.beep.setChecked(self.beep)
        view.start_data_driven_filter_designer.setChecked(self.start_data_driven_filter_designer)
        view.update_statistics.setChecked(self.update_statistics)
        view.random_bound.setCurrentText(self.random_bound)
        view.video_path.setText(self.video_path)

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
        data["fbSource"] = self.feedback_source
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

        return data
    
    def serialize(self) -> dict:
        return {
            "name": self.name,
            "duration": self.duration,
            "feedback_source": self.feedback_source,
            "feedback_type": self.feedback_type,
            "random_bound": self.random_bound,
            "video_path": self.video_path,

            "mock_signal_path": self.mock_signal_path,
            "mock_signal_dataset": self.mock_signal_dataset,
            "mock_previous": self.mock_previous,
            "mock_previous_reverse": self.mock_previous_reverse,
            "mock_previous_random": self.mock_previous_random,

            "start_data_driven_filter_designer": self.start_data_driven_filter_designer,
            "pause": self.pause,
            "beep": self.beep,
            "update_statistics": self.update_statistics,
        }

    def deserialize(self, data: dict):
        self.name = data["name"]
        self.duration = data["duration"]
        self.feedback_source = data["feedback_source"]
        self.feedback_type = data["feedback_type"]
        self.random_bound = data["random_bound"]
        self.video_path = data["video_path"]

        self.mock_signal_path = data["mock_signal_path"]
        self.mock_signal_dataset = data["mock_signal_dataset"]
        self.mock_previous = data["mock_previous"]
        self.mock_previous_reverse = data["mock_previous_reverse"]
        self.mock_previous_random = data["mock_previous_random"]

        self.start_data_driven_filter_designer = data["start_data_driven_filter_designer"]
        self.pause = data["pause"]
        self.beep = data["beep"]
        self.update_statistics = data["update_statistics"]

    def nfb_import_data(self, data: dict):
        """Import this block from a dict from NFBLab.
        Since the XML file stores everything as a string, this function is responsible for converting items to their
        proper types.
        """

        self.name = data["sProtocolName"]
        self.update_statistics = bool(int(data["bUpdateStatistics"]))
        self.start_data_driven_filter_designer = bool(int(data["bSSDInTheEnd"]))
        self.duration = float(data["fDuration"])
        self.feedback_source = data["fbSource"]
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
