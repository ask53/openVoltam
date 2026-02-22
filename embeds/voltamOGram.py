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
from scipy.signal import savgol_filter

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

            self.colors = ['deeppink','limegreen','chocolate','mediumturquoise','gold','purple','red','blue']
                
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

    def plot_rep(self, rep, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False, color='black'):
        
        
        if rep[g.R_DATA]:
            # 1. Convert rep signal and background data to 1D numpy arrays
            x = np.array(pd.DataFrame(rep[g.R_DATA])[[g.R_DATA_VOLT]].values)
            x = x.reshape(x.shape[0])
            y = np.array(pd.DataFrame(rep[g.R_DATA])[[g.R_DATA_CURR]].values)
            y = y.reshape(y.shape[0])
            x_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_VOLT]].values)
            x_back = x_back.reshape(x_back.shape[0])
            y_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_CURR]].values)
            y_back = y_back.reshape(y_back.shape[0])

            # 2. If background is present & subbackground==True, interpolate background and subtract
            if x_back.size != 0 and y_back.size != 0 and subbackground:
                y_back = np.interp(x, x_back, y_back)   # interpolate background to match voltage of signal
                y = y - y_back                          # subtrack background from signal
            
            # 3. If smooth, smooth result
            y_raw = y.copy()                        # store copy of y as y_raw in case we want to display it to user
                
            if smooth:
                polyorder = 3
                wl = min(15, len(y))
                if wl % 2 == 0: wl -= 1
                if wl <= polyorder: wl = polyorder + 2
                y = savgol_filter(y, window_length=wl, polyorder=polyorder)

            # 4. If lopass, pass result thru lopass filter
            if lopass:
                pass
                # DO LO-PASS FILTERING HERE ###################
                #
                #
                #
                ###################################################

            # 5. If predictpeak, guess baseline and peak locations, store as vars in self
            #
            #
            #
            #
            ########################################################################3

            # 6. Show final result
            if showraw:                                 # first, show raw data if requested
                self.canvas.axes.plot(x,y_raw,'lightgrey', linewidth=0.5)

            self.canvas.axes.plot(x,y,color, linewidth=2)          # then show smoothed, filtered data on top.
            

            # 7. If showraw, show unfiltered, unsmoothed data (post-subtraction)

            # 8. If predictpeak, show baseline (with adjustable handles) and peak location

            print(x)
            print(y_raw)
            print(y)
            print('--------------')
                

            
            

            

            

            

            

            
        
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
        print('color len',str(len(self.colors)))
        for i,run in enumerate(runs):
            modded = i%len(self.colors)
            print(modded)
            color = self.colors[modded]
            for rep in run[g.R_REPLICATES]:
                self.plot_rep(rep, subbackground=subbackground, smooth=smooth, lopass=lopass, showraw=showraw, predictpeak=predictpeak, color=color)
        
        ############ FOR TESTING ONLY
        # DELETE THIS AND UNCOMMENT ABOVE SECTION TO ACTUALLY RUN!
        #
        #for rep in runs[0][g.R_REPLICATES]:
        #    self.plot_rep(rep, subbackground=subbackground, smooth=smooth, lopass=lopass, showraw=showraw, predictpeak=predictpeak)
        #
        ##########################################
            

