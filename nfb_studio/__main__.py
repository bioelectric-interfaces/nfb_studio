"""Startup script for nfb_studio."""
# Big Sur workaround
try:
    import OpenGL as ogl
    try:
        import OpenGL.GL   # this fails in <=2020 versions of Python on OS X 11.x
    except ImportError:
        from ctypes import util
        orig_util_find_library = util.find_library
        def new_util_find_library( name ):
            res = orig_util_find_library( name )
            if res: return res
            return '/System/Library/Frameworks/'+name+'.framework/'+name
        util.find_library = new_util_find_library
except ImportError:
    pass

import sys
import multiprocessing
from PySide2.QtWidgets import QApplication, QStyleFactory

from nfb_studio.experiment_view import ExperimentView
# Note: When using relative import in __main__.py, frozen executable fails to start with error:
# ImportError: attempted relative import with no known parent package

def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setApplicationName("nfb-studio")
    app.setApplicationDisplayName("NFB Studio")
    app.setStyle(QStyleFactory.create("fusion"))

    main_window = ExperimentView()
    main_window.show()

    # If a file was passed as a command-line argument, load it
    if len(sys.argv) > 1:
        main_window.fileOpen(sys.argv[1])

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
