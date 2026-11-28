"""
runPlots.py

Realtime viewer of voltage and current data from a potentiostat
Includes two plots stacked vertically, Voltage v. time on the top,
Current v. time on the bottom. Designed to be embedded in a PyQt
application. Enjoy :)

"""


from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg  
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

import numpy as np

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class SubsetToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ('Home', 'Pan', 'Zoom')]

class RunPlotCanvas(FigureCanvasQTAgg):
    def __init__(self, parent, width=5, height=4, dpi=100):
        self.parent = parent
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes_v = self.fig.add_subplot(211)
        self.axes_I = self.fig.add_subplot(212, sharex=self.axes_v)
        self.set_text()
        super().__init__(self.fig)
    
    def get_settings(self):
        self.settings = self.parent.settings
        
    def set_text(self):
        self.get_settings()
        lang = get_lang(self)
        print('Setting text for RUN PLOT CANVAS in '+lang)
        self.fig.suptitle(get_text(l.LRD_TTL, lang))
        

class RunPlots(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = self.parent.settings

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

        self.set_text()
        
        widget = QWidget()              # Add layout to central widget of QMainWindow and show!
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()

    def init_plot(self, method):
        self.method = method
        duration = get_method_duration(method[g.M_STEPS])
        [v_min, v_max] = get_method_v_extremes(method[g.M_STEPS])
        (signal_bounds, background_bounds) = get_method_measurement_bounds(method[g.M_STEPS])
        overhang = 0.05 * (v_max - v_min)
        
        self.clear_axes()
        self.set_axis_labels()
        self.canvas.axes_v.set_xlim(left=0, right=1.02*duration)
        self.canvas.axes_v.set_ylim(bottom=v_min-overhang, top=v_max+overhang)

        for t_step in signal_bounds:
            self.canvas.axes_v.axvspan(t_step[0],t_step[1],facecolor='#edbdfc')
            self.canvas.axes_I.axvspan(t_step[0],t_step[1],facecolor='#edbdfc')
        for t_step in background_bounds:
            self.canvas.axes_v.axvspan(t_step[0],t_step[1],facecolor='#f6e3fc')
            self.canvas.axes_I.axvspan(t_step[0],t_step[1],facecolor='#f6e3fc')

        self.canvas.draw()

    def set_axis_labels(self):
        lang = get_lang(self)
        self.canvas.axes_v.set_ylabel(get_text(l.LRD_VOLT, lang))
        self.canvas.axes_I.set_ylabel(get_text(l.LRD_CURR, lang))
        self.canvas.axes_I.set_xlabel(get_text(l.LRD_TIME, lang))

    def update_plots(self, t, v, I):
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
                
    def get_settings(self):
        self.settings = self.parent.settings
        
    def set_text(self):
        self.get_settings()
        lang = get_lang(self)
        print('Setting text for RUN PLOTS in '+lang)
        
        self.canvas.set_text()
        self.set_axis_labels()
        self.canvas.draw_idle()