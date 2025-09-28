"""
window_editConfig.py

This file defines a class WindowEditConfig which creates a window object
that can be used to create a new run configuration (if blank) or to edit
an existing configuration (if passed the path of the config file).

The sample file can be saved anywhere on the local directory.

All files are in .ovconfig format. 
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from PyQt6.QtWidgets import (
    QMainWindow
    )

class WindowEditConfig(QMainWindow):
    def __init__(self, path):
        super().__init__()
        self.path = False
        if path:
            self.path = path
        if self.path:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_edit[g.L])
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_new[g.L])
