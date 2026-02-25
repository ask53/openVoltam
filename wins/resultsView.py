"""
resultsView.py

Shows a voltamogram graph of results to the user. Overlaps all
runs/reps that the user requests on the same axes.
"""
from external.globals import ov_globals as g

from embeds.voltamOGram import VoltamogramPlot

from PyQt6.QtCore import Qt
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

        print(self.tasks)

        self.voltamogram = VoltamogramPlot(self.parent)

        showraw = True
        if len(tasks) > 1:
            showraw = False
        try:
            self.voltamogram.plot_reps(tasks, showraw=showraw)
        except Exception as e:
            print(e)
        
        self.setCentralWidget(self.voltamogram)   

    def update_win(self):
        data = self.parent.data

    def closeEvent(self, event):
        self.accept_close(event)

    def accept_close(self, closeEvent):
        self.parent.children.remove(self)
        closeEvent.accept()
