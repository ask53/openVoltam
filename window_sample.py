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
from window_runConfig import WindowRunConfig

# import other necessary python tools
from os.path import join as joindir
from functools import partial
from tkinter.filedialog import askopenfilename as askOpenFileName
from json import dumps, loads

from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QWidget,
    QLabel,
    QFrame,
    QToolTip,
    QHeaderView
    
)

# Define class for Home window
class WindowSample(QMainWindow):
    def __init__(self, path, parent):
        super().__init__()
        self.path = path
        self.parent = parent
        self.data = {}
        self.w_view_sample = False
        self.config_pane_displayed = False

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
        action_new_config = QAction(l.new_config[g.L], self)
        action_open_config = QAction(l.open_config[g.L], self)
        action_edit_config = QAction(l.edit_config[g.L], self)

        # connect menu bar labels with slots 
        action_new_sample.triggered.connect(parent.new_sample)                      # this first group of menu functions come from the home window (parent)
        action_open_sample.triggered.connect(parent.open_sample)
        action_new_config.triggered.connect(parent.new_config)
        action_open_config.triggered.connect(parent.open_config)
        action_edit_config.triggered.connect(parent.edit_config)

        # Add menu top labels then populate the menus with the above slotted labels
        file_menu = menu.addMenu(l.menu_sample[g.L])
        file_menu.addAction(action_new_sample)
        file_menu.addAction(action_open_sample)
        
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
        but_config = QPushButton('new run')
        but_view.clicked.connect(self.view_sample_info)
        but_edit.clicked.connect(partial(self.parent.edit_sample, self.path))
        but_config.clicked.connect(self.config_run)
        
        hline = QHLine()
        vline = QVLine()
        
        l_top_inner = QHBoxLayout()
        l_top_inner.addWidget(self.lbl_sample_name)
        l_top_inner.addWidget(but_view)
        l_top_inner.addWidget(but_edit)
        l_top_inner.addWidget(vline)
        l_top_inner.addWidget(but_config)
        l_top_inner.addStretch()
        l_top_outer = QVBoxLayout()
        l_top_outer.addLayout(l_top_inner)
        l_top_outer.addWidget(hline)

        run_history_table = self.getRunHistoryAsTable()
        

        layout_pane = QVBoxLayout()
        layout_pane.addLayout(l_top_outer)
        layout_pane.addWidget(run_history_table)
        
        self.w = QWidget()
        self.w.setLayout(layout_pane)
        self.setCentralWidget(self.w)

        self.w_view_sample = WindowViewSample(self.data)

    def view_sample_info(self):
        self.w_view_sample = WindowViewSample(self.data)
        self.w_view_sample.show()

    def config_run(self):
        w = WindowRunConfig(self)
        w.exec()

    def getRunHistoryAsTable(self):

        table = QTableWidget()
        cols = 9
        rows = 4
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels(["Type", "Name", "Sweep configuration", "Run began", "Note", "Analysis", "Results", "Export CSV", "View sweep configuration"])
        for i in range(0,rows):

            table.setCellWidget(i,0,QLabel("run type"+str(i)))
            table.setCellWidget(i,1,QLabel("run name"+str(i)))
            table.setCellWidget(i,2,QLabel("config used"+str(i)))
            table.setCellWidget(i,3,QLabel("run datetime"+str(i)))
            table.setCellWidget(i,4,QLabel("CommentCommentCommentComment"+str(i)))
            but1 = QPushButton()
            but1.setIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))
            but2 = QPushButton()
            but2.setIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))
            but3 = QPushButton()
            but3.setIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))
            but4 = QPushButton()
            but4.setIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))
            table.setCellWidget(i,5,but1)
            table.setCellWidget(i,6,but2)
            table.setCellWidget(i,7,but3)
            table.setCellWidget(i,8,but4)
            
        table.setAlternatingRowColors(True)                                     # alternate row colors
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)   # when any cell is selected, entire row is selected
        table.verticalHeader().setVisible(False)                                # hide left index column
        table.setShowGrid(False)                                                # hide gridlines
        for col in range(0,cols):                                               # loop thru all columns, resizing to contents (prevents user from adjusting width)
            table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) # then add stretch to comments column

        return table


        


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

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
