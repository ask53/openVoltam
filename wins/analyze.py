"""
analyze.py

A window that displays as many graphs, one by one, for the user
to analyze.

Whenever possible, an autoanalysis is generated. However, the user
always has the option to modify as they see fit.

The following controls are provided:
    - Next: Brings user to next plot
    - Save: Saves all analysis conducted so far to file (only visible from last task)
    - Progress pane: clickable links to jump to any task
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

        #################### FILL RESULTS ARRAY HERE
        #
        #
        for task in self.tasks:     # fill results list with an empty dict 
            self.results.append({})  #   for each task
        #
        #
        #######################################################################3
        self.results[0] = True
        self.results[2] = 'hi!'
        self.results[5] = True



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
            but = QPushButton()
            but.clicked.connect(partial(self.go_to_rep, i))
            self.buts.append(but)

        
        prog_lbl = QLabel('<b>Runs to analyze:</b>')
        v2 = QVBoxLayout()
        v2.addWidget(prog_lbl)
        for but in self.buts:
            v2.addWidget(but)

        h2 = QHBoxLayout()
        h2.addLayout(v2)
        h2.addWidget(QVLine())
        h2.addLayout(self.stack)
        
        self.but_next = QPushButton()

        self.but_next.clicked.connect(self.next_click)

        h1 = QHBoxLayout()
        h1.addStretch()
        h1.addWidget(self.but_next)
        
        v1 = QVBoxLayout()
        v1.addLayout(h2)
        v1.addStretch()
        v1.addWidget(QHLine())
        v1.addLayout(h1)

        # set form
        starting_index = self.stack.currentIndex()
        self.update_buttons(starting_index)
        self.refresh_progress(starting_index)

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
        self.store_results()
        self.process_next()

    def store_results(self):
        return
        



    def process_next(self):
        if self.stack.currentIndex() == len(self.tasks)-1:  # if we're on last task already
            saved = self.save()                             #   try to save
            if saved:                                       #   if saved,
                self.close()                                #       close the window! 
        else:                                               # if we're not on the last task,
            i = self.stack.currentIndex()                   #   go to the next task
            self.go_to_rep(i+1)                                          

    def go_to_rep(self, i):
        self.stack.setCurrentIndex(i)
        self.update_buttons(i)
        self.refresh_progress(i)
        

    def update_buttons(self, i):
        if i == len(self.tasks)-1:  # if we are on the final task
            self.but_next.setText('Save all')
        else:                       # if we are on any other task
            self.but_next.setText('Accept && next')
            
        
    def refresh_progress(self, i):
        for j,but in enumerate(self.buts):
            # set progress pane element color/border
            if j==i: but.setObjectName('task-selected') 
            elif self.results[j]: but.setObjectName('task-complete')
            else: but.setObjectName('task-pending')

            # Set progress pane element text
            (run_id, rep_id) = self.tasks[j]
            if self.results[j]: but.setText(run_id+', '+rep_id+'  |  Complete')
            else: but.setText(run_id+', '+rep_id)       
        applyStyles()
        
        
        
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
    

