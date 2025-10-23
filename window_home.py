# import custom variables and functions
import ov_globals as g
import ov_lang as l
from ov_functions import *

# import custom window objects
from window_editSample import WindowEditSample
from window_editConfig import WindowEditConfig
from window_viewConfig import WindowViewConfig
from window_sample import WindowSample

# import other necessary python tools
from os.path import join as joindir
from functools import partial
from tkinter.filedialog import askopenfilename as askOpenFileName
from json import dumps, loads

# import necessary tools from PyQt6
from PyQt6.QtGui import QAction, QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt, QDateTime, QDate
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QGroupBox,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QMessageBox,
    QFrame
)

##############3
#
#   FOR TESTING ONLY
#
##############

import traceback






# Define class for Home window
class WindowHome(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = {}
        
        # set the window parameters
        self.setWindowTitle(l.window_home[g.L])
        
        # define possible popup windows (not modals)
        self.w_edit_sample = WindowEditSample(False, self)
        self.w_edit_config = WindowEditConfig(False)
        self.w_samples = []
        self.ws_view_config = []
        
        # Create the text intro label
        lbl_about = QLabel(l.info_msg[g.L])
        lbl_about.setWordWrap(True)
        lbl_about.setOpenExternalLinks(True)

        # Create the graphic
        lbl_icon = QLabel()
        lbl_icon.setPixmap(QPixmap(joindir(g.BASEDIR,"external/icons/logo.png")))

        # Create all buttons
        but_sample_new = QPushButton(l.new_sample[g.L])
        but_sample_open = QPushButton(l.open_sample[g.L])
        but_config_new = QPushButton(l.new_config[g.L])
        but_config_open = QPushButton(l.open_config[g.L])

        # Connect relevant button signals to functions ("slots")
        but_sample_new.clicked.connect(self.new_sample)
        but_sample_open.clicked.connect(self.open_sample)
        but_config_new.clicked.connect(self.new_config)
        but_config_open.clicked.connect(self.open_config)

        # layout screen into three horizontal layouts grouped together vertically
        layout_pane = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_sample = QHBoxLayout()
        layout_config = QHBoxLayout()
        
        # add icon and intro text message into 1st layout
        layout_top.addWidget(lbl_icon)
        layout_top.addWidget(lbl_about)

        # add sample buttons into 2nd layout, wrap them in groupbox that labels them both
        layout_sample.addWidget(but_sample_new)
        layout_sample.addWidget(but_sample_open)
        groupbox_sample = QGroupBox(l.menu_sample[g.L])
        groupbox_sample.setLayout(layout_sample)

        # add config buttons into 3nd layout, wrap them in groupbox that labels them both
        layout_config.addWidget(but_config_new)
        layout_config.addWidget(but_config_open)
        groupbox_config = QGroupBox(l.menu_config[g.L])
        groupbox_config.setLayout(layout_config)

        # add all three horizontal layouts to the vertical layout
        layout_pane.addLayout(layout_top)
        layout_pane.addWidget(groupbox_sample)
        layout_pane.addWidget(groupbox_config)

        w = QWidget()
        w.setLayout(layout_pane)
        self.setCentralWidget(w)

    def new_sample(self):
        if (self.w_edit_sample.isHidden()):                 # check if winow is hidden. If so:
            self.w_edit_sample = WindowEditSample(False, self)    #   Create a new empty edit sample window, with this as parent
            self.w_edit_sample.show()                       #   and show it!
        else:                                               # if window is already showing
            self.w_edit_sample.activateWindow()             #   bring it to front of screen'''

    def open_sample(self, path=False):
        if not path:                # if no path is passed, ask the user to pick a file path
            path = askOpenFileName(filetypes = [(l.filetype_lbl[g.L], g.FILE_TYPES)])
        if path:                    # if the path is passed or if the user selected a valid path:
            w = False                               # placeholder for the current sample window
            if len(self.w_samples) > 0:             # if there are current sample windows
                for w_sample in self.w_samples:     #   loop through them 
                    if w_sample.path == path:       #   if we find one where the path matches our current path
                        w = w_sample                #   store the object in our placeholder
            if w:                                   # if we found a matching window
                try:
                    w.update_displayed_info()           #   update sample info
                except Exception as e:
                    print(e)
                w.activateWindow()                  #   and activate window
            else:                                   # if we didn't find a match
                try:
                    self.create_sample_window(path)     #   create a sample window from the path
                except Exception as e:
                    print(e)
                
            self.close()                            # close the home window if open
            

    def create_sample_window(self, path):
        self.w_samples.append(WindowSample(path, self))     # create new window for sample, append to list
        self.w_samples[len(self.w_samples)-1].show()        # show most recently added sample window
        
               

    def edit_sample(self, path):
        if (self.w_edit_sample.isHidden()):                 # check if window is hidden. If so:
            if path:                                        # if a path has been passed
                self.edit_sample_from_file(path)                 #   open the sample from the given path
            else:                                           # if a path has not been passed, ask the user to select a file
                path = askOpenFileName(filetypes = [(l.filetype_lbl[g.L], g.FILE_TYPES)])
                if path:                                    # if the user has selected a file (instead, say, of selecting "cancel")
                    self.edit_sample_from_file(path)        # load the sample from the selected file       
        else:                                               # if window is already showing
            self.w_edit_sample.activateWindow()             #   bring it to front of screen
        
    def edit_sample_from_file(self, path):
        self.w_edit_sample = WindowEditSample(path, self)   #   Create a new edit sample window with data from path
        self.w_edit_sample.show()                       #   and show it!

    def new_config(self):
        if (self.w_edit_config.isHidden()):                 # check if winow is hidden. If so:
            self.w_edit_config = WindowEditConfig(False)    #   Create a new empty edit config window
            self.w_edit_config.show()                       #   and show it!
        else:                                               # if window is already showing
            self.w_edit_config.activateWindow()             #   bring it to front of screen

    def open_config(self):
        self.ws_view_config.append(WindowViewConfig())
        self.ws_view_config[-1].show()

    def edit_config(self):
        ### HOWEVER WE SORTED "edit_sample(self, path) PLEASE UPDATE
        ### THIS FUNCTION TO MATCH FUNCTIONALLY
        if (self.w_edit_config.isHidden()):                 # check if winow is hidden. If so:
            self.w_edit_config = WindowEditConfig("path")   #   Create a new empty edit config window
            self.w_edit_config.show()                       #   and show it!
        else:                                               # if window is already showing
            self.w_edit_config.activateWindow()             #   bring it to front of screen

    def go_back(self):
        self.setCentralWidget(self.homeWidget())
        self.showNormal()




