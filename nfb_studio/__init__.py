"""NFB experiment designer."""
# Big Sur OpenGL bug workaround (https://bugs.python.org/issue41100) ---------------------------------------------------
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
# ----------------------------------------------------------------------------------------------------------------------

import os
from pathlib import Path

dir = Path(__file__).parent

from .block import Block, BlockView
from .group import Group, GroupView

from .experiment import Experiment
from .experiment_view import ExperimentView
from .general_view import GeneralView
from .property_tree import PropertyTree
