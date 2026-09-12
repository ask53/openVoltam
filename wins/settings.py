"""
settings.py

A window in which the user can set any settings
"""
from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

from pathlib import Path

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox
)

class WindowSettings(QMainWindow):
    def __init__(self, parent):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.status = self.statusBar()
        self.force_close = False
        self.reload_required = False
        self.loading = True
        self.path = self.parent.settings_path
        self.data = None
        
        # Titles
        self.lbl_title = QLabel('...')
        
        #Language
        self.lbl_lang = QLabel('...')
        self.lang = QComboBox()
        self.lang.currentIndexChanged.connect(self.language_changed)
        for key in g.LANGS.keys():
            self.lang.addItem(key, g.LANGS[key])
        self.lang.model().sort(self.lang.modelColumn())                     # Sort A-Z
        
        
        
        
        
        # Set layout
        v1 = QVBoxLayout()
        v1.addWidget(self.lbl_title)
        v1.addLayout(horizontalize([self.lbl_lang, self.lang]))
        
        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)
        
        self.load_settings()
        self.set_text(self.data[g.SET_LANG])
        self.loading = False                                                # Shut off loading flag to enable changes!
        
    def language_changed(self):
        if self.loading:
            return
        self.save_settings()                            # save all the settings
        self.set_text_all_descendants_from(self.parent) # update text on parent (welcome) and all its descendants
                                                        #   based on selected language (updates all windows)
        
    def set_text_all_descendants_from(self, win):
        """Takes in a starting window. Calls the that window's set_text method,
        win.set_text(). Then recursively calls the set_text method on all descendents
        of that starting window"""
        lang = self.data[g.SET_LANG]
        win.set_text(lang)                  # set text on that window
        try:
            win.children                    # if that window has children
        except:
            pass
        else:
            for child in win.children:      # loop thru all children
                child.set_text(lang)        # set text on each one
        
    def load_settings(self):
        self.data = self.parent.settings
        lang = list(g.LANGS.keys())[list(g.LANGS.values()).index(self.data[g.SET_LANG])]
        self.lang.setCurrentText(lang)
        
        
    def save_settings(self):
        if self.loading:
            return

        # Bundle the data into a dictionary
        self.data = {}
        self.data[g.SET_LANG] = str(self.lang.itemData(self.lang.currentIndex()))
        
        # Write!
        self.parent.settings = self.data            # update the settings on Welcome win
        write_data_to_file(self.path, self.data)    # Save settings to file 
        
        
        
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
        data = self.parent.data
        
    def set_text(self, lang):
        """ Sets all text in window to label in the provided language, lang"""
        self.setWindowTitle(l.SET_WIN_TITLE[lang])              # Title of window (on header bar)
        txt(self.lbl_title, l.SET_TITLE, lang)                  # In-window title
        txt(self.lbl_lang, l.SET_LANG, lang)                    # Language label
            
    
    def closeEvent(self, event):
        self.accept_close(event)
        
        
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        if self in self.parent.children:
            self.parent.children.remove(self)
        closeEvent.accept()
                                        
