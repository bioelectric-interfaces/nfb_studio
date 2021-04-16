"""NFB Experiment block."""
from PySide2.QtCore import QObject


class Block(QObject):
    """A single step of an experiment.
    Experiment consists of a sequence of blocks and block groups that are executed in some order.
    """
    random_bound_types = ["SimCircle", "RandomCircle", "Bar"]

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # General ------------------------------------------------------------------------------------------------------
        self.duration = 10.0
        self.duration_deviation = 0.0
        self.feedback_source = "All"
        self.feedback_type = "Baseline"
        self.random_bound = "SimCircle"
        self.video_path = ""
        self.message = ""
        self.voiceover = False

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
        self.statistics_type = "meanstd"


    def nfb_export_data(self) -> dict:
        """Export this block into a dict to be encoded as XML for NFBLab.
        Bool items are written as-is. The encoder is responsible for converting them into int format.
        """
        data = {}

        data["bUpdateStatistics"] = self.update_statistics
        data["iDropOutliers"] = 0
        data["bSSDInTheEnd"] = self.start_data_driven_filter_designer
        data["fDuration"] = self.duration - self.duration_deviation
        data["fRandomOverTime"] = self.duration_deviation * 2
        data["fbSource"] = self.feedback_source
        data["sFb_type"] = self.feedback_type
        data["cString"] = self.message
        data["bVoiceover"] = self.voiceover
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
        data["iRandomBound"] = self.random_bound_types.index(self.random_bound)
        data["sVideoPath"] = self.video_path
        data["sStatisticsType"] = self.statistics_type
        data["sMSignal"] = "None"
        data["fMSignalThreshold"] = 1

        return data
    
    def serialize(self) -> dict:
        return {
            "duration": self.duration,
            "duration_deviation": self.duration_deviation,
            "feedback_source": self.feedback_source,
            "feedback_type": self.feedback_type,
            "random_bound": self.random_bound,
            "video_path": self.video_path,
            "message": self.message,
            "voiceover": self.voiceover,

            "mock_signal_path": self.mock_signal_path,
            "mock_signal_dataset": self.mock_signal_dataset,
            "mock_previous": self.mock_previous,
            "mock_previous_reverse": self.mock_previous_reverse,
            "mock_previous_random": self.mock_previous_random,

            "start_data_driven_filter_designer": self.start_data_driven_filter_designer,
            "pause": self.pause,
            "beep": self.beep,
            "update_statistics": self.update_statistics,
            "statistics_type": self.statistics_type,
        }

    @classmethod
    def deserialize(cls, data: dict):
        obj = cls()

        obj.duration = data["duration"]
        obj.duration_deviation = data["duration_deviation"]
        obj.feedback_source = data["feedback_source"]
        obj.feedback_type = data["feedback_type"]
        obj.random_bound = data["random_bound"]
        obj.video_path = data["video_path"]
        obj.message = data["message"]
        obj.voiceover = data.get("voiceover", False)

        obj.mock_signal_path = data["mock_signal_path"]
        obj.mock_signal_dataset = data["mock_signal_dataset"]
        obj.mock_previous = data["mock_previous"]
        obj.mock_previous_reverse = data["mock_previous_reverse"]
        obj.mock_previous_random = data["mock_previous_random"]

        obj.start_data_driven_filter_designer = data["start_data_driven_filter_designer"]
        obj.pause = data["pause"]
        obj.beep = data["beep"]
        obj.update_statistics = data["update_statistics"]
        obj.statistics_type = data["statistics_type"]

        return obj

    @classmethod
    def nfb_import_data(cls, data: dict):
        """Import this block from a dict from NFBLab.
        Since the XML file stores everything as a string, this function is responsible for converting items to their
        proper types.
        """
        b = cls()

        b.update_statistics = bool(float(data["bUpdateStatistics"]))
        b.start_data_driven_filter_designer = bool(float(data["bSSDInTheEnd"]))

        if data.get("fRandomOverTime", None) is None:
            b.duration = float(data["fDuration"])
            b.duration_deviation = 0.0
        else:
            b.duration = float(data["fDuration"]) + float(data["fRandomOverTime"]) / 2
            b.duration_deviation = float(data["fRandomOverTime"]) / 2
        
        b.feedback_source = data["fbSource"]
        b.feedback_type = data["sFb_type"]
        b.mock_signal_path = data["sMockSignalFilePath"]
        b.mock_signal_dataset = data["sMockSignalFileDataset"]
        b.mock_previous = int(float(data["iMockPrevious"]))
        b.mock_previous_reverse = bool(float(data["bReverseMockPrevious"]))
        b.mock_previous_random = bool(float(data["bRandomMockPrevious"]))
        b.pause = bool(float(data["bPauseAfter"]))
        b.beep = bool(float(data["bBeepAfter"]))
        b.random_bound = b.random_bound_types[int(float(data["iRandomBound"]))]
        b.video_path = data["sVideoPath"]
        b.message = data["cString"]
        b.voiceover = bool(float(data.get("bVoiceover", 0)))
        b.statistics_type = data["sStatisticsType"]

        return b
