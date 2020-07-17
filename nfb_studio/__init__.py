"""NFB experiment designer."""
import os

icons = os.path.dirname(__file__) + "/icons"

from .experiment import Experiment, ExperimentView
from .block import Block, BlockView
from .group import Group, GroupView

from .main_window import MainWindow
