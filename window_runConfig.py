"""
window_runConfig.py

This file defines a class WindowRunConfig which creates a window
object that can be used to set the configuration parameters for a
run. This is broader than sweep_config which just sets the sweep
profile. This window allows the user the select the sweep profile and
set a bunch of other parameters as well.
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from PyQt6.QtWidgets import (
    QDialog
)

class WindowRunConfig(QDialog):
    def __init__(self, parent):
        super().__init__()
