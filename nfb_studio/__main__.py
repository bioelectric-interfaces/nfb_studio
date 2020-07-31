"""Startup script for nfb_studio."""
import sys
from PySide2.QtWidgets import QApplication

from .experiment_view import ExperimentView

def main():
    app = QApplication(sys.argv)

    main_window = ExperimentView()
    main_window.show()

    # If a file was passed as a command-line argument, load it
    if len(sys.argv) > 1:
        main_window.fileOpen(sys.argv[1])

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
