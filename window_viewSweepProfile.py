"""
window_viewConfig.py

This file defines a class WindowViewConfig which creates a window object
that can be used to view a run configuration that is read in from a
.ovconfig file at the passed path.
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from PyQt6.QtWidgets import (
    QMainWindow
    )

class WindowViewSweepProfile(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.view_config_full[g.L])
