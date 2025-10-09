"""
window_sample.py

This file defines a class WindowSample which creates a window object
that can be used to do a bunch of things. This is the main window that the
user will primarily use while operating the GUI.

The user can configure new runs, initiate runs, collect data, analyze data,
export data, view all past runs and analysis, and perhaps run calculations
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from window_viewSample import WindowViewSample

# import other necessary python tools
from os.path import join as joindir
from functools import partial
from tkinter.filedialog import askopenfilename as askOpenFileName
from json import dumps, loads

from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QFrame,
    QToolTip
    
)

# Define class for Home window
class WindowSample(QMainWindow):
    def __init__(self, path, parent):
        super().__init__()
        self.path = path
        self.parent = parent
        self.data = {}
        self.w_view_sample = False

        #print(self.data)
            

        #####################
        #                   #
        #   menu bar        #
        #                   #
        #####################
        menu = self.menuBar()

        # add labels ("actions") for menu bar
        action_new_sample = QAction(l.new_sample[g.L], self)
        action_open_sample = QAction(l.open_sample[g.L], self)
        action_edit_sample = QAction(l.edit_sample[g.L], self)
        action_new_config = QAction(l.new_config[g.L], self)
        action_open_config = QAction(l.open_config[g.L], self)
        action_edit_config = QAction(l.edit_config[g.L], self)

        # connect menu bar labels with slots 
        action_new_sample.triggered.connect(parent.new_sample)                      # this first group of menu functions come from the home window (parent)
        action_open_sample.triggered.connect(parent.open_sample)
        action_edit_sample.triggered.connect(partial(parent.edit_sample, False))
        action_new_config.triggered.connect(parent.new_config)
        action_open_config.triggered.connect(parent.open_config)
        action_edit_config.triggered.connect(parent.edit_config)

        # Add menu top labels then populate the menus with the above slotted labels
        file_menu = menu.addMenu(l.menu_sample[g.L])
        file_menu.addAction(action_new_sample)
        file_menu.addAction(action_open_sample)
        file_menu.addSeparator()
        file_menu.addAction(action_edit_sample)
        
        file_menu = menu.addMenu(l.menu_config[g.L])
        file_menu.addAction(action_new_config)
        file_menu.addAction(action_open_config)
        file_menu.addSeparator()
        file_menu.addAction(action_edit_config)

        file_menu = menu.addMenu(l.menu_run[g.L])

        #####################
        #                   #
        #   page layout     #
        #                   #
        #####################

        self.load_sample_info()

    def load_sample_info(self):                     # this grabs all data from file and lays it out on the window
                                                    # this can be called to update the window when the file has been updated
        if self.path:                                # if there is a path, read in the data
            with open(self.path, "r") as file:    
                self.data = loads(file.read())

        self.setWindowTitle(self.data[g.S_NAME])
                
        self.lbl_sample_name = TitleLbl(self.data)
        but_view = QPushButton('view info')
        but_edit = QPushButton('edit info')
        but_view.clicked.connect(self.view_sample_info)
        but_edit.clicked.connect(partial(self.parent.edit_sample, self.path))
        hline_1 = QHLine()
        
        layout_top = QHBoxLayout()
        layout_top.addWidget(self.lbl_sample_name)
        layout_top.addWidget(but_view)
        layout_top.addWidget(but_edit)
        layout_top.addStretch()

        but_back = QPushButton('button')
        layout_pane = QVBoxLayout()
        layout_pane.addLayout(layout_top)
        layout_pane.addWidget(but_back)
        w = QWidget()
        w.setLayout(layout_pane)
        self.setCentralWidget(w)

        self.w_view_sample = WindowViewSample(self.data)

    def view_sample_info(self):
        self.w_view_sample = WindowViewSample(self.data)
        self.w_view_sample.show()
        


class TitleLbl(QLabel):
    def __init__(self, data):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(data[g.S_NAME])
        self.data = data
                 
    def updateTitleLbl(self):
        self.setText(data[g.S_NAME])
        

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
