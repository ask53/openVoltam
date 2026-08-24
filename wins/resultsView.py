"""
resultsView.py

Shows a voltamogram graph of results to the user. Overlaps all
runs/reps that the user requests on the same axes.
"""
from global_scripts import ov_globals as g
from global_scripts.ov_functions import *

from embeds.voltamOGram import VoltamogramPlot

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QMainWindow
)

class WindowResultsView(QMainWindow):
    def __init__(self, parent, tasks):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.tasks = tasks
        
        self.setWindowTitle(self.parent.data[g.S_NAME]+' | Results Viewer')

        self.voltamogram = VoltamogramPlot(self)

        showraw = True
        if len(tasks) > 1:
            showraw = False
        try:
            self.voltamogram.plot_reps(tasks, showsmoothed=True, showraw=showraw)
        except Exception as e:
            print('error here in resulltsView win!')
            print(e)
        
        self.setCentralWidget(self.voltamogram)   

    def update_win(self):
        data = self.parent.data
    
    def event(self, event):                                 # General purpose event handler
        if event.type() == QEvent.Type.ActivationChange:    # Check if the event is changing the activation status of the window
            if self.isActiveWindow():                       #   Check whether the event *activated* the window
                main = self.parent
                welcome = main.parent
                if not fileOkRoutine(welcome, main, self):      # Run routine to check if file is okay
                    return True
        return QMainWindow.event(self, event)               # Forward all events to appropriate QMainWindow event handler

    def closeEvent(self, event):
        self.accept_close(event)

    def accept_close(self, closeEvent):
        if self in self.parent.children:
            self.parent.children.remove(self)
        closeEvent.accept()
