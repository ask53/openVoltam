# import custom variables and functions
from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

# import custom window objects
from wins.sample import WindowSample
from wins.method import WindowMethod
from wins.main import WindowMain
from wins.settings import WindowSettings

# import other necessary python tools
from functools import partial
from pathlib import Path

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
    QGroupBox,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QMessageBox,
    QInputDialog
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
        
        # Load system-wide OV settings (settable by user)
        self.settings_path = Path(g.BASEDIR) / "external" / g.SET_FILE
        self.settings = get_data_from_file(self.settings_path)
        
        # Create the settings button
        but_set = QPushButton()
        but_set.setIcon(QIcon(g.ICON_SET))
        but_set.clicked.connect(self.open_settings)
        
        # Create the text intro label
        self.lbl_about = QLabel()
        self.lbl_about.setWordWrap(True)
        self.lbl_about.setOpenExternalLinks(True)

        # Create the graphic
        lbl_icon = QLabel()
        path_pixmap = Path(g.BASEDIR) / "external" / "icons" / "logo.png"
        lbl_icon.setPixmap(QPixmap(str(path_pixmap)))           # QPixmap only accepts string paths, not pathlib Path() objects
        
        # Create all buttons
        self.but_sample_new = QPushButton()
        self.but_sample_open = QPushButton()
        self.but_config_new = QPushButton()
        self.but_config_open = QPushButton()
        
        # Connect relevant button signals to functions ("slots")
        self.but_sample_new.clicked.connect(self.new_session)
        self.but_sample_open.clicked.connect(self.open_session)
        self.but_config_new.clicked.connect(self.new_method)
        self.but_config_open.clicked.connect(self.open_method)
        
        
        h1 = QHBoxLayout()      # Horizontal layout for settings button
        h1.addStretch()
        h1.addWidget(but_set)
        
        v1 = QVBoxLayout()      # Settings button and main text
        v1.addLayout(h1)
        v1.addWidget(self.lbl_about)
        
        
        h2 = QHBoxLayout()      # Upper half (icon, text, settings)
        h2.addWidget(lbl_icon)
        h2.addLayout(v1)

        # add sample buttons into 2nd layout, wrap them in groupbox that labels them both
        h3 = QHBoxLayout()
        h3.addWidget(self.but_sample_new)
        h3.addWidget(self.but_sample_open)
        self.g1 = QGroupBox()
        self.g1.setLayout(h3)

        # add config buttons into 3nd layout, wrap them in groupbox that labels them both
        h4 = QHBoxLayout()
        h4.addWidget(self.but_config_new)
        h4.addWidget(self.but_config_open)
        self.g2 = QGroupBox()
        self.g2.setLayout(h4)

        # add all three horizontal layouts to the vertical layout
        v2 = QVBoxLayout()
        v2.addLayout(h2)
        v2.addWidget(self.g1)
        v2.addWidget(self.g2)

        w = QWidget()
        w.setLayout(v2)
        
        self.set_text(self.settings[g.SET_LANG])
        
        
        
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

    def new_session(self):
        title = 'New lab session'
        text = 'Lab session name:'
        text, ok = QInputDialog.getText(self, title, text)

        if ok:
            try:
                path = self.save_new_session(text)
                if path:
                    self.open_session(path=path)
            except Exception as e:
                print(e)

    def save_new_session(self, name):
        data = {g.S_NAME: name,
                g.S_DATE_ENTERED: QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)}
        for key in g.S_BLANK_ARRAYS:
            data[key] = []
        initial_name = guess_filename(name)+g.SAMPLE_EXT
        path = QFileDialog.getSaveFileName(self, 'Save lab session', initial_name, g.SAMPLE_FILE_TYPES)[0]
        if path:
            path = Path(path)       # convert string path to pathlib Path() object
            write_status = write_data_to_file(path, data)
            if write_status:
                return path
            else:
                show_alert(self, 'Alert!', 'There was an error saving the new lab session.')
        return False      
                
    def open_session(self, path=False):
        try:
            if not path:                # if no path is passed, ask the user to pick a file path
                path = get_path_from_user(self, 'session')
            if path:                    # if the path is passed or if the user selected a valid path:
                self.new_win_one_with_value(WindowMain(self, path), 'path', path)
            # if user didn't select a path, do nothing
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def new_method(self):
        try:
            self.new_win_one_with_value(WindowMethod(self, g.WIN_MODE_NEW, False), 'mode', g.WIN_MODE_NEW)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            
    def open_method(self, path=False):
        try:
            if not path:
                path = get_path_from_user(self, 'method')
            if path:
                self.new_win_one_with_value(WindowMethod(self, g.WIN_MODE_EDIT, path), 'path', path)
        except Exception as e:
            print(e)
            
    def open_settings(self):
        self.new_win_one_of_type(WindowSettings(self))
     
    def set_text(self, lang):
        print('setting text on WELCOME')
        self.setWindowTitle(l.WEL_TITLE[lang])                 # Title of window (on header bar)
        txt(self.lbl_about, l.WEL_INFO, lang)                  # Info text with links, version, release, etc.
        self.g1.setTitle(l.WEL_SESH[lang])                     # Upper groupbox (lab session)
        txt(self.but_sample_new, l.WEL_NEW_SESH, lang)         # New lab session
        txt(self.but_sample_open, l.WEL_OPN_SESH, lang)        # Open lab session
        self.g2.setTitle(l.WEL_METH[lang])                     # Lower groupbox (Method)
        txt(self.but_config_new, l.WEL_NEW_METH, lang)         # New method
        txt(self.but_config_open, l.WEL_OPN_METH, lang)        # Open method

    def closeEvent(self, event):
        if self.children:       # if there are any sub-windows
            self.hide()         # hide the welcome window instead of closing it
            event.ignore()
        else:
            event.accept()      # if no sub windos, close! 


