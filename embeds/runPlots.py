"""
runVoltagePlot.py


"""
import ov_globals as g
import ov_lang as l
from ov_functions import *

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg  
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class SubsetToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ('Home', 'Pan', 'Zoom')]

class RunPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes_v = fig.add_subplot(211)
        self.axes_I = fig.add_subplot(212, sharex=self.axes_v)
        super().__init__(fig)

class RunPlots(QMainWindow):
    def __init__(self):
        super().__init__()

        size_mm = g.APP.primaryScreen().physicalSize()                          # get desired dimensions of plots
        width_in = size_mm.width() * g.MM2IN
        height_in = size_mm.height() * g.MM2IN
        
        self.canvas = RunPlotCanvas(self, width=width_in, height=height_in, dpi=100)    # Create figure w both subplots
        toolbar = SubsetToolbar(self.canvas, self)                                      # Create toolbar for figure
        self.set_axis_labels()
        self.axes = [self.canvas.axes_v, self.canvas.axes_I]                            # ADD ADITIONAL AXES HERE (FOR LOOP CLEARING)
        
        layout = QVBoxLayout()          # Add toolbar and canvas to vertical layout
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)

        widget = QWidget()              # Add layout to central widget of QMainWindow and show!
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def init_plot(self, method):
        self.method = method
        duration = get_method_duration(method[g.M_STEPS])
        [v_min, v_max] = get_method_v_extremes(method[g.M_STEPS])
        measurement_bounds = get_method_measurement_bounds(method[g.M_STEPS])
        overhang = 0.05 * (v_max - v_min)
        
        self.clear_axes()
        self.set_axis_labels()
        self.canvas.axes_v.set_xlim(left=0, right=1.02*duration)
        self.canvas.axes_v.set_ylim(bottom=v_min-overhang, top=v_max+overhang)

        for t_step in measurement_bounds:
            self.canvas.axes_v.axvspan(t_step[0],t_step[1],facecolor='#f6e3fc')
            self.canvas.axes_I.axvspan(t_step[0],t_step[1],facecolor='#f6e3fc')

        self.canvas.draw()

        

    def set_axis_labels(self):
        self.canvas.axes_v.set_ylabel('Voltage [V]')
        self.canvas.axes_I.set_ylabel('Current [mA]')
        self.canvas.axes_I.set_xlabel('Time [s]')
        
    def update_plots(self, t, v, I):
        
        #for line in list(self.canvas.axes_v.lines):     # remove all existing lines from plot
        #    line.remove()

        self.remove_all_lines()
            
        self.canvas.axes_v.plot(t, v, 'grey')
        self.canvas.axes_I.plot(t, I, 'black')
        self.canvas.draw()

    def clear_axes(self):
        self.remove_all_lines()
        for axes in self.axes:
            axes.cla()
        self.canvas.draw()

    def remove_all_lines(self):
        for axes in self.axes:
            for line in list(axes.lines):
                line.remove()
        
