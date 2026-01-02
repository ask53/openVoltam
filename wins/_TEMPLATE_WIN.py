"""
_TEMPLATE_WIN.py

A template with necessary functions for any window in the OpenVoltam project.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow
)

class WindowName(QMainWindow):
    def __init__(self, path, parent, *args):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.status = self.statusBar()

        # Setup widgets, layout, and (if necessary) mode here
        
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
        data = self.parent.data
        # update window widgets here
            
    
    def closeEvent(self, event):
        """
        Event handler for close event."""
        # add close/save logic here
        self.accept_close(event)
                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()
                                        
