import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QListView, QWidget, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox

from nfb_studio.widgets.signal import SignalEditor, Scheme, Node, Input, Output, InfoMessage, WarningMessage, ErrorMessage, Toolbox
from nfb_studio import std_encoder as encoder
from nfb_studio.serial import xml

from .experiment import Experiment
from .block import Block
from .main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
