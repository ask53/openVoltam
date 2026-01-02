# import custom variables and functions
import ov_globals as g
import ov_lang as l
from ov_functions import *

# import custom window objects
from wins.sample import WindowSample
from wins.method import WindowMethod
from wins.main2 import WindowMain

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

    '''def activate_single_window(self, winObj):
        found = False
        for win in self.children:
            if type(win) == type(winObj):
                win.activateWindow()
                found = True
                break
        if not found:
            self.children.append(winObj)
            self.children[-1].show()'''

    def new_win_one_of_type(self, obj):
        """Takes in a new object to create as child window of self.
        Checks whether a window with matching type already exists.
        If it does, activates (bring-to-front) that window and returns it.
        If not, creates that window, show, it and returns it.
        Returns: window object."""
        for win in self.children:       
            if type(win) == type(obj):  # If there is already a child window with matching type
                win.activateWindow()    # activate it and return it
                return win
        self.children.append(obj)       # If there isn't already one, append the new window to the list of children
        self.children[-1].show()        # Show the window
        return self.children[-1]        # And return it

    def new_win_one_with_value(self, obj, key, value):
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
                
        '''    
        if (self.w_new_sample.isHidden()):      # check if winow is hidden. If so:
            self.w_new_sample.show()            #   and show it!
        else:                                   # if window is already showing
            self.w_new_sample.activateWindow()  #   bring it to front of screen'''

    def open_sample(self, path=False):
        
        if not path:                # if no path is passed, ask the user to pick a file path
            path = get_path_from_user('sample')
        if path:                    # if the path is passed or if the user selected a valid path:
            found = False                               
            for win in self.children:
                if type(win) == type(WindowMain(path, self)):
                    if win.path == path:
                        found = True
                        win.activateWindow()
                        break
            if not found:
                self.children.append(WindowMain(path, self))
                self.children[-1].show()
            self.close()
        # if user didn't select a path, do nothing
            

            '''

            if len(self.w_samples) > 0:             # if there are current sample windows
                for w_sample in self.w_samples:     #   loop through them 
                    if w_sample.path == path:       #   if we find one where the path matches our current path
                        w = w_sample                #   store the object in our placeholder
            if w:                                   # if we found a matching window
                try:
                    w.update_main()                 #   update sample info
                except Exception as e:
                    print(e)
                    error = True
                w.activateWindow()                  #   and activate window
            else:                                   # if we didn't find a match
                try:
                    self.create_sample_window(path) #   create a sample window from the path
                except Exception as e:
                    print(e)
                    error = True
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    show_alert(self, "Error", "Uh oh, there was an issue opening the selected file, please try again. If the problem persists, the file may be corrupted.")
                    
            if not error:
                self.close()                            # close the home window if open
            '''
            

    def create_sample_window(self, path):
        try:
            self.w_samples.append(WindowMain(path, self))     # create new window for sample, append to list
            print(self.w_samples)
            self.w_samples[len(self.w_samples)-1].show()        # show most recently added sample window
            print('thur')
        except Exception as e:
            print(e)

    def new_config(self):
        if (self.w_edit_config.isHidden()):                 # check if winow is hidden. If so:
            self.w_edit_config = WindowMethod(False)    #   Create a new empty edit config window
            self.w_edit_config.show()                       #   and show it!
        else:                                               # if window is already showing
            self.w_edit_config.activateWindow()             #   bring it to front of screen

    def open_config(self, path=False, data=False, editable=True):
        if data:
            try:       
                self.ws_view_config.append(WindowMethod(data=data, view_only=True, parent=self, view_only_edit=editable))
                self.ws_view_config[-1].show()
            except Exception as e:
                print(e)
        elif not path:
            path = get_path_from_user('method')

        if not data and path:
                try:
                    
                    self.ws_view_config.append(WindowMethod(path=path, view_only=True, parent=self, view_only_edit=editable))
                    self.ws_view_config[-1].show()
                except Exception as e:
                    print(e)

    def edit_config(self, path=False):
        try:
            if (self.w_edit_config.isHidden()):                 # check if winow is hidden. If so:
                if not path:                                    # if no path is passed, ask the user to pick a file path
                    path = get_path_from_user('method')
                    
                if path:                                    # if the path is passed or if the user selected a valid path:                        
                    try:
                        self.w_edit_config = WindowMethod(path)   #   Create a new empty edit config window
                        self.w_edit_config.show()                           #   and show it!
                    except Exception as e:
                        print(e)
                        show_alert(self, "Error", "Uh oh, there was an issue opening the selected file, please try again. If the problem persists, the file may be corrupted.")      
            else:                                               # if window is already showing
                self.w_edit_config.activateWindow()             #   bring it to front of screen
        except Exception as e:
            print(e)

    def go_back(self):
        self.setCentralWidget(self.homeWidget())
        self.showNormal()




