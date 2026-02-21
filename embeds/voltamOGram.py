"""
voltamOGram.py

Shows a voltamogram of passed runs. Gives user the option to
analyze for baselines and peak location/heigh or not.

"""

from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class SubsetToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ('Home', 'Pan', 'Zoom')]

class VoltamogramCanvas(FigureCanvasQTAgg):
    def __init__(self, parent, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.suptitle('Voltam-O-Gram')
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class VoltamogramPlot(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            
            size_mm = g.APP.primaryScreen().physicalSize()
            width_in = size_mm.width() * g.MM2IN
            height_in = size_mm.height() * g.MM2IN

            self.canvas = VoltamogramCanvas(self, width=width_in, height=height_in, dpi=100)    # Create figure on canvas
            toolbar = SubsetToolbar(self.canvas, self)                                          # set canvas toolbar

            self.set_axis_labels()
            self.axes = self.canvas.axes
                
            layout = QVBoxLayout()          # Add toolbar and canvas to vertical layout
            layout.addWidget(toolbar)
            layout.addWidget(self.canvas)

            widget = QWidget()              # Add layout to central widget of QMainWindow and show!
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.show()
        except Exception as e:
            print(e)

    def set_axis_labels(self):
        self.canvas.axes.set_xlabel('Voltage [V]')
        self.canvas.axes.set_ylabel('Current [uA]')
        
            

