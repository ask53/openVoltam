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
from external.globals import ov_globals as g

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QStackedLayout,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
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

        self.setWindowTitle(self.parent.data[g.S_NAME]+' | Analyze')

        self.stack = QStackedLayout()

        for task in self.tasks:
            lbl = QLabel(str(task))
            lbl2 = QLabel(str(task))
            v = QVBoxLayout()
            v.addWidget(lbl)
            v.addWidget(lbl2)
            
            w = QWidget()
            w.setLayout(v)
            self.stack.addWidget(w)
        
        but_prev = QPushButton('Prev')
        but_skip = QPushButton('Skip')
        self.but_next = QPushButton()

        but_prev.clicked.connect(self.prev_click)
        self.but_next.clicked.connect(self.next_click)

        h1 = QHBoxLayout()
        h1.addWidget(but_prev)
        h1.addStretch()
        h1.addWidget(but_skip)
        h1.addStretch()
        h1.addWidget(self.but_next)
        
        v1 = QVBoxLayout()
        v1.addLayout(self.stack)
        v1.addStretch()
        v1.addLayout(h1)

        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)

    def prev_click(self):
        i = self.stack.currentIndex()
        if i>0:
            self.stack.setCurrentIndex(i-1)

    def next_click(self):
        i = self.stack.currentIndex()
        if i<len(self.tasks)-1:
            self.stack.setCurrentIndex(i+1)
    

    def save_from_close(self, event):
        print('saving!')
        #################################
        #
        #   DO SAVE HERE
        #
        #
        ########################################
        self.saved = True
        if self.close_on_save and self.saved:
            self.accept_close(event)
        else:
            event.ignore()

            


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
        if not self.saved:
            confirm = saveMessageBox()
            resp = confirm.exec()
            if resp == QMessageBox.StandardButton.Save:
                self.close_on_save = True
                self.save_from_close(event)
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
    

