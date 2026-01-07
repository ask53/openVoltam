# import custom variables and functions
import ov_globals as g
import ov_lang as l
from ov_functions import *

# import custom window objects
from wins.sample import WindowSample
from wins.method import WindowMethod
from wins.main import WindowMain

# import other necessary python tools
from os.path import join as joindir
from functools import partial

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

#######
#   FOR TESTING ONLY
import sys, os
#
###########

# Define class for Welcome window
class WindowWelcome(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = {}
        self.children = []
        
        # set the window parameters
        self.setWindowTitle(l.window_home[g.L])
        
        # define possible popup windows (not modals)
        '''self.w_new_sample = WindowSample(False, self)
        self.w_edit_config = WindowMethod(False)
        self.w_samples = []
        self.ws_view_config = []'''
        
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
        but_config_new.clicked.connect(self.new_method)
        but_config_open.clicked.connect(self.open_method)

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

    def new_win_one_of_type(self, obj):
        """Checks whether window already exists of obj type.
        Only allows 1 window of obj type.
        If it already exists, activates it (brings it to front) and returns it.
        If it doesn't exist, creates it, shows it, and returns it.
        Returns: window object with same type as obj."""
        for win in self.children:       
            if type(win) == type(obj):  # If there is already a child window with matching type
                win.activateWindow()    # activate it and return it
                return win
        self.children.append(obj)       # If there isn't already one, append the new window to the list of children
        self.children[-1].show()        # Show the window
        return self.children[-1]        # And return it

    def new_win_one_with_value(self, obj, key, value):
        """Checks whether window already exists of obj type AND that has self.key==value.
        Only allows 1 window of type that also matches value.
        If it already exists, activates it (brings it to front) and returns it.
        If it doesn't exist, creates it, shows it, and returns it.
        Returns: window object with same type as obj."""
        for win in self.children:
            if type(win) == type(obj):
                if win.__dict__[key] == value:
                    win.activateWindow()
                    return win
        self.children.append(obj)
        self.children[-1].show()
        return self.children[-1]

    def new_sample(self):
        self.new_win_one_of_type(WindowSample(self, g.WIN_MODE_NEW))
                
    def open_sample(self, path=False):
        if not path:                # if no path is passed, ask the user to pick a file path
            path = get_path_from_user('sample')
        if path:                    # if the path is passed or if the user selected a valid path:
            self.new_win_one_with_value(WindowMain(self, path), 'path', path)
            self.close()
        # if user didn't select a path, do nothing

    def new_method(self):
        self.new_win_one_with_value(WindowMethod(self, g.WIN_MODE_NEW, False), 'mode', g.WIN_MODE_NEW)

    def open_method(self, path=False):
        try:
            if not path:
                path = get_path_from_user('method')
            if path:
                self.new_win_one_with_value(WindowMethod(self, g.WIN_MODE_EDIT, path), 'path', path)
        except Exception as e:
            print(e)




