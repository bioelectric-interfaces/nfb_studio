"""Startup script for nfb_studio."""
import sys
from PySide2.QtWidgets import QApplication
from nfb_studio.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
