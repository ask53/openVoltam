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
        self.path = Path(g.BASEDIR) / "external" / g.SET_FILE
        
        # Titles
        title = QLabel('<b>Settings</b>')
        self.setWindowTitle('OpenVoltam | Settings')
        
        #Language
        lang_lbl = QLabel('Language')
        self.lang = QComboBox()
        self.lang.currentIndexChanged.connect(self.language_changed)
        for i, lang in enumerate(g.LANGS):
            self.lang.addItem(lang, i)
        self.lang.model().sort(self.lang.modelColumn())                     # Sort A-Z
        
        
        
        
        
        # Set layout
        v1 = QVBoxLayout()
        v1.addWidget(title)
        v1.addLayout(horizontalize([lang_lbl, self.lang]))
        
        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)
        
        self.load_settings()
        self.loading = False                                                # Shut off loading flag to enable changes!
        
    def language_changed(self):
        ##############################################################3
        #
        #   HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE 
        #
        #   DO STUFF TO CHANGE THE LANGUAGE AS SOON AS NEW LANGUAGE IS SELECTED!
        #
        #
        #
        ###########################################################################3
        
        # 1. Save settings
        # 2. Set text on Welcome window (self.parent)
        # 3. Loop thru all children of Welcome window. (for child in self.parent.children)
        #   a. Set text for that window (child.set_text())
        #   b. If window has children (if child.children exists):
        #       i. Loop thru all children of main (for grandchild in child.children())
        #       ii. Set text for that window (grandchild.set_text())
        #        ^--- this can be done recursively woahhhhhhh a realworld applicaiton of recursionnnnn
        #
        # Proposed code
        #
        # self.save_settings()
        # self.set_text(self.parent)
        #
        #
         
        self.update_requires_reload()
        
    '''def set_text(self, win):
        win.set_text()                      # set text on that window
        If win has children:                # FIGURE OUT HOW TO CHECK THIS
            for each child:                 # REWRITE WITH REAL CODE
                self.set_text(child)        # CREATE A self.set_text() METHOD FOR EACH WINDOW AND ADD TO TEMPLATE
    '''    
        
        
    def update_requires_reload(self):
        if self.loading:
            return
        reload_required = True
        self.save_settings()
        
    def load_settings(self):
        data = get_data_from_file(self.path)
        lang = g.LANGS[int(data[g.SET_LANG])]
        self.lang.setCurrentText(lang)
        
        
    def save_settings(self):
        if self.loading:
            return

        # Bundle the data into a dictionary
        data = {}
        data[g.SET_LANG] = str(self.lang.itemData(self.lang.currentIndex()))
        
        # Write the settings file
        write_data_to_file(self.path, data)
        
        
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
        data = self.parent.data
        # update window widgets here
            
    
    def closeEvent(self, event):
        """
        Event handler for close event."""
        if self.force_close:
            self.accept_close(event)
        # add close/save logic here
        #
        self.accept_close(event)
        #
        ###########################
        
        
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        if self in self.parent.children:
            self.parent.children.remove(self)
        closeEvent.accept()
                                        
