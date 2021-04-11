"""Startup script for nfb_studio."""
import sys
import platform
import multiprocessing
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QStyleFactory

from nfb_studio.experiment_view import ExperimentView
import nfb_studio as package
# Note: When using relative import in __main__.py, frozen executable fails to start with error:
# ImportError: attempted relative import with no known parent package

def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setApplicationName("nfb-studio")
    app.setApplicationDisplayName("NFB Studio")
    app.setStyle(QStyleFactory.create("fusion"))

    if platform.system() == "Darwin":
        icon_dir = package.dir / "assets/window-icon/macos"
    else:
        icon_dir = package.dir / "assets/window-icon/generic"
        
    icon = QIcon()
    for file in icon_dir.glob("*"):
        icon.addFile(str(file))
    app.setWindowIcon(icon)

    main_window = ExperimentView()
    main_window.show()

    # If a file was passed as a command-line argument, load it
    if len(sys.argv) > 1:
        main_window.fileOpen(sys.argv[1])

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
