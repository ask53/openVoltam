"""
calculate.py

A window that allows the user to use analyzed data, collected with
the potentiostat, to back-calculate the concentration of the
species of interest in the original sample.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)

class WindowCalculate(QMainWindow):
    def __init__(self, parent):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.status = self.statusBar()
        self.lay = 'right'
        

        self.set_layout()
    
        # Setup widgets, layout, and (if necessary) mode here

    def get_right_layout(self):
        l = QLabel('right label\nright label\nright label')
        v = QVBoxLayout()
        v.addWidget(l)
        v.addStretch()
        return v   

    def get_left_layout(self):
        l = QLabel('left LBL')
        v = QVBoxLayout()
        v.addStretch()
        v.addWidget(l)
        return v

    def get_full_layout(self):
        right = self.get_right_layout()
        b = QPushButton('click me to toggle!')
        b.clicked.connect(self.toggle)
        if self.lay == 'right':
            v = QVBoxLayout()
            v.addLayout(right)
            v.addWidget(b)
        else:
            left = self.get_left_layout()
            h = QHBoxLayout()
            h.addLayout(left)
            h.addLayout(right)
            v = QVBoxLayout()
            v.addLayout(h)
            v.addWidget(b)
        return v

    def set_layout(self):
        l = self.get_full_layout()
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def toggle(self):
        if self.lay == 'right': self.lay = 'left'
        else: self.lay = 'right'
        self.set_layout()






            
        
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
                                        
