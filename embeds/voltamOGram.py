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
import pandas as pd

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
    def __init__(self, parent):
        try:
            super().__init__()

            self.parent = parent
            
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

    def plot_rep(self, rep, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False):
        
        
        if rep[g.R_DATA]:
            # 1. Convert rep signal and background data to numpy arrays (col0 = voltage, co11 = current)
            np_data = np.array(pd.DataFrame(rep[g.R_DATA])[[g.R_DATA_VOLT, g.R_DATA_CURR]].values)
            np_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_VOLT, g.R_DATA_CURR]].values)

            # 2. If background is present & subbackground, interpolate it to match voltage of signal
            ### HERE!!!! ################################3
            #
            #
            #
            #
            ##########################################

            # 3. If background is present & subbackground, subtract background from signal

            # 4. If smooth, smooth result

            # 5. If lopass, pass result thru lopass filter

            # 6. If predictpeak, guess baseline and peak locations, store as vars in self

            # 7. Show final result

            # 8. If showraw, show unfiltered, unsmoothed data (post-subtraction)

            # 9. If predictpeak, show baseline (with adjustable handles) and peak location
        
        return

    def plot_reps(self, reps, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False):
        # 1. Get data from file for specified reps
        #
        #
        #
        # 2. Loop thru runs, plotting each rep
        for rep in reps:
            self.plot_rep(rep, subbackground=subbackground, smooth=smooth, lopass=lopass, showraw=showraw, predictpeak=predictpeak)
        
        

    def plot_runs(self, runs, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False):
        # 1. Get data from file for specified runs
        all_data = get_data_from_file(self.parent.path)     # read file including all raw data
        for run in runs:
            for rep in run[g.R_REPLICATES]:
                run_id = run[g.R_UID_SELF]
                rep_id = rep[g.R_UID_SELF]
                found = False
                for fullrun in all_data[g.S_RUNS]:
                    if fullrun[g.R_UID_SELF] == run_id:
                        for fullrep in fullrun[g.R_REPLICATES]:
                            if fullrep[g.R_UID_SELF] == rep_id:
                                found = True
                                try: 
                                    rep[g.R_DATA] = fullrep[g.R_DATA]
                                except Exception as e:
                                    print(e)
                                    rep[g.R_DATA] = []
                                try:
                                    rep[g.R_BACKGROUND] = fullrep[g.R_BACKGROUND]
                                except Exception as e:
                                    print(e)
                                    rep[g.R_BACKGROUND] = []
                                break
                        if found: break
    
        # 2. Loop thru runs, plotting each rep
        for run in runs:
            for rep in run[g.R_REPLICATES]:
                self.plot_rep(rep, subbackground=subbackground, smooth=smooth, lopass=lopass, showraw=showraw, predictpeak=predictpeak)
        
            

