"""
analyze.py

A window that displays as many graphs, one by one, for the user
to analyze.

Whenever possible, an autoanalysis is generated. However, the user
always has the option to modify as they see fit.

The following controls are provided:
    - Prev: Brings user to previous plot
    - Next: Brings user to next plot
    - Skip: Brings user to next plot without saving analysis from
            current plot
    - Save: Saves all analysis conducted so far to file
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow
)

class WindowAnalyze(QMainWindow):
    def __init__(self, parent, tasks):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.status = self.statusBar()
        self.parent = parent
        self.tasks = tasks
        self.saved = False
        print(self.tasks)

    def update_win(self):
        return
        # update window widgets here
            
    
    def closeEvent(self, event):
        """Event handler for close event."""
        # add close/save logic here
        #   on close, if saved = False, confirm!!
        #
        ############################################################################################
        try:
            self.accept_close(event)
        except Exception as e:
            print(e)
                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()
    

