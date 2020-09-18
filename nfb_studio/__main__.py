"""Startup script for nfb_studio."""
import sys
import multiprocessing
from PySide2.QtWidgets import QApplication

from nfb_studio.experiment_view import ExperimentView
# Note: When using relative import in __main__.py, frozen executable fails to start with error:
# ImportError: attempted relative import with no known parent package

def main():
    app = QApplication(sys.argv)

    main_window = ExperimentView()
    main_window.show()

    # If a file was passed as a command-line argument, load it
    if len(sys.argv) > 1:
        main_window.fileOpen(sys.argv[1])

    return app.exec_()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
