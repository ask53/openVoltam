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

from external.globals.ov_functions import *

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel
)

class WindowAnalyze(QMainWindow):
    def __init__(self, parent, tasks):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.status = self.statusBar()
        self.parent = parent
        self.tasks = tasks
        self.saved = False
        self.close_on_save = False
        
        print(self.tasks)

        tasklbl = QLabel(str(self.tasks))
        self.setCentralWidget(tasklbl)

    

    def start_save(self):
        print('saving!')
        #################################
        #
        #   DO SAVE HERE
        #
        #
        ########################################
        self.saved = True
        if self.close_on_save:
            print('about to close!')
            self.close()

            ######################################3 HERE HERE HERE HERE HERE HERE HERE HERE HERE
            #
            #   FIGURE OUT WHY THIS self.close() doesn't go to the closeEvent
            #   event handler. Like wtffffffffff
            #
            ##
            #
            #
            #
            #
            #
            #
            #
            #
            #################################################################################################################




    def update_win(self):
        return
        # update window widgets here

    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.set_enabled_children(False)
        self.setEnabled(True)
        event.accept()      
    
    def closeEvent(self, event):
        """Event handler for close event."""
        print('and here we are in the close handler!')
        if not self.saved:
            confirm = saveMessageBox()
            resp = confirm.exec()
            if resp == QMessageBox.StandardButton.Save:
                event.ignore()
                self.close_on_save = True
                self.start_save()
            elif resp == QMessageBox.StandardButton.Discard:
                self.accept_close(event)
            else:
                event.ignore()  
        else:
            self.accept_close(event)

                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""

        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.parent.children.remove(self)
        closeEvent.accept()
    

