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

from functools import partial

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
        self.results = []

        self.setWindowTitle(self.parent.data[g.S_NAME]+' | Analyze')

        for task in self.tasks:     # fill results list with an empty dict 
            self.results.append({})  #   for each task



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


        
        self.buts = []
        for i, task in enumerate(tasks):
            but = QPushButton(task[0]+', '+task[1]+'  |  Pending')
            but.setObjectName('task-pending')
            ### USE but.setAttribute() here to add the task index to the button
            #
            #       HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE
            #
            #
            #
            but.clicked.connect(partial(self.go_to_rep, i))
            #
            #
            ##########################################################################
            self.buts.append(but)

        
        prog_lbl = QLabel('<b>Runs to analyze:</b>')
        v2 = QVBoxLayout()
        v2.addWidget(prog_lbl)
        for but in self.buts:
            v2.addWidget(but)

        h2 = QHBoxLayout()
        h2.addLayout(self.stack)
        h2.addWidget(QVLine())
        h2.addLayout(v2)
        
        self.but_skip = QPushButton('Skip')
        self.but_next = QPushButton()

        self.but_skip.clicked.connect(self.process_next)
        self.but_next.clicked.connect(self.next_click)

        h1 = QHBoxLayout()
        h1.addStretch()
        h1.addWidget(self.but_skip)
        h1.addWidget(self.but_next)
        
        v1 = QVBoxLayout()
        v1.addLayout(h2)
        v1.addStretch()
        v1.addLayout(h1)

        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)

    
    def next_click(self):
        # store current here ##############################
        #
        print('storing the results!')
        #
        #
        ##############################
        # Then process the next click
        self.process_next()



    def process_next(self):
        if self.stack.currentIndex() == len(self.tasks)-1:  # if we're on last task already
            saved = self.save()                             #   try to save
            if saved:                                       #   if saved,
                self.close()                                #       close the window! 
        else:                                               # if we're not on the last task,
            i = self.stack.currentIndex()                   #   go to the next task
            self.go_to_rep(i+1)                                          

    def go_to_rep(self, i):
        # go to rep with index i (ie. self.tasks[i])
        self.stack.setCurrentIndex(i)
        self.update_buttons(i)
        self.refresh_progress(i)
        # repaint taskbar (update highlights and which have been completed

    def update_buttons(self, i):
        if i == len(self.tasks)-1:  # if we are on the final task
            print('updating buttons to FINAL button configs')

        else:                       # if we are on any other task
            print('regular butts')
            

        
    def refresh_progress(self, i):
        print('refreshing progress pane!')
        
        
        

        
    def save(self):
        print('saving then closing!')
        return True

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
    

