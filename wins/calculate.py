"""
calculate.py

A window that allows the user to use analyzed data, collected with
the potentiostat, to back-calculate the concentration of the
species of interest in the original sample.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow
)

class WindowCalculate(QMainWindow):
    def __init__(self, parent):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.status = self.statusBar()

        # Setup widgets, layout, and (if necessary) mode here
        
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
        return

    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.set_enabled_children(False)
        self.setEnabled(True)
        event.accept() 
            
    
    def closeEvent(self, event):
        """
        Event handler for close event."""
        # add close/save logic here
        try:
            self.accept_close(event)
        except Exception as e:
            print(e)
                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.parent.children.remove(self)
        closeEvent.accept()
                                        
