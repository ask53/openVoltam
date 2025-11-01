"""
window_editSweepProfile.py

This file defines a class WindowEditConfig which creates a window object
that can be used to create a new sweep profile (if blank) or to edit
an existing profile. There are two ways to edit an existing profile because
there are two places a profile may be stored:
    1. In a standalone sweep profile file (with .ovp extention for 'Open Voltam Profile')
    2. Embedded in an Open Voltam sample file (.ovs).
In the first case, this window is passed a path to the .ovp file. If so,
it loads the sweep profile info which can be edited and either saved back to the
same file or Save-as'd to a new file name/location.
In the second case, both the path of the .ovs file as well as the unique ID of
the stored sweep profile is passed. As this is not being imported from a standalone
file, when "save" is pressed, it prompts the user to select a location and name
for the new file.

Both .ovs and .ovp files use tabular json format (an extension of json that allows
for tabular, comma-separated-value type data to be embedded within a json.

"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QScrollArea,
    QTabWidget
    
    )

class WindowEditSweepProfile(QMainWindow):
    def __init__(self, path=False, uid=False):
        super().__init__()
        self.path = False

        if path:
            self.path = path
        if self.path:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_edit[g.L])
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_new[g.L])

        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()
        

        self.graph = QScrollArea()
        name_lbl = QLabel('Name')
        self.name = QLineEdit()
        
        ################################33 HEREEEE DEBUG THISSSSS
        
        
        w_custom = QWidget()
        w_custom.setLayout()    # update this with custom layout! 
        w_standard = QLabel('nothing here yet...')

        self.builder = QTabWidget()
        self.builder.setTabPosition(QTabWidget.TabPosition.North)
        self.builder.addTab(w_custom, 'custom')
        self.builder.addTab(w_standard, 'standard')

        ############################################################
        
        but_save = QPushButton('Save')

        v2.addWidget(name_lbl)
        v2.addWidget(self.name)
        v2.addStretch()
        
        h1.addLayout(v2)
        h1.addWidget(self.graph)
        
        v1.addLayout(h1)
        v1.addWidget(self.builder)
        v1.addWidget(but_save)
        
        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)
