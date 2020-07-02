"""Startup script for nfb_studio."""
import sys
from PySide2.QtWidgets import QApplication
from nfb_studio.main_window import MainWindow
from nfb_studio.experiment import Experiment

def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    # If a file was passed as a command-line argument, load it
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            data = file.read()
        
        ex = Experiment.load(data)
        main_window.setExperiment(ex)

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
