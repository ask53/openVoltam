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
from scipy.signal import savgol_filter, butter, filtfilt

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
            # 1. Convert rep signal and background data to 1D numpy arrays then resize
            # 1a. Convert to numpy array
            x = np.array(pd.DataFrame(rep[g.R_DATA])[[g.R_DATA_VOLT]].values)
            x = x.reshape(x.shape[0])
            y = np.array(pd.DataFrame(rep[g.R_DATA])[[g.R_DATA_CURR]].values)
            y = y.reshape(y.shape[0])
            x_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_VOLT]].values)
            x_back = x_back.reshape(x_back.shape[0])
            y_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_CURR]].values)
            y_back = y_back.reshape(y_back.shape[0])
            
            # 1b. Resize
            x = self.resize_data(x, g.VOG_RESIZE)
            y = self.resize_data(y, g.VOG_RESIZE)

            if x_back.size != 0 and y_back.size != 0:
                x_back = self.resize_data(x_back, g.VOG_RESIZE)
                y_back = self.resize_data(y_back, g.VOG_RESIZE)

            # 2. If background is present & subbackground==True, interpolate background and subtract
            if x_back.size != 0 and y_back.size != 0 and subbackground:
                y_back = np.interp(x, x_back, y_back)   # interpolate background to match voltage of signal
                y = y - y_back                          # subtrack background from signal
            
            # 3. If smooth, smooth result
            y_raw = y.copy()                        # store copy of y as y_raw in case we want to display it to user    

            if smooth:
                y = savgol_filter(y, window_length=g.VOG_SG_WINDOW_LEN,
                                  polyorder=g.VOG_SG_POLYORDER, mode='nearest')

            # 4. If lopass, pass result thru lopass filter
            if lopass:
                y = self.butter_lowpass_filter(y, g.VOG_LP_CUTOFF, g.VOG_LP_FS,
                                               order=g.VOG_LP_ORDER)
                

            # 5. If predictpeak, guess baseline and peak locations, store as vars in self
            #
            #
            #
            #
            ########################################################################3
            
            # 6. Show final result
            if showraw:                                 # first, show raw data if requested
                self.canvas.axes.plot(x, y_raw, 'lightgrey', linewidth=0.5)

            self.canvas.axes.plot(x, y, color, linewidth=2)          # then show smoothed, filtered data on top.

            self.canvas.draw()
            

            # 7. If showraw, show unfiltered, unsmoothed data (post-subtraction)

            # 8. If predictpeak, show baseline (with adjustable handles) and peak location
                

            
            

            

            

            

            

            
        
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
        for i,run in enumerate(runs):
            color = self.colors[i%len(self.colors)]
            for rep in run[g.R_REPLICATES]:
                ##### FOR TESTING ONLY
                #
                #subbackground = False
                #showraw=True
                #
                ##############################
                self.plot_rep(rep, subbackground=subbackground, smooth=smooth, lopass=lopass, showraw=showraw, predictpeak=predictpeak, color=color)

    def resize_data(self, file_in, n):
        #  file_in = 1D numpy array of arbitrary length
        #  file_out = 1D numpy array of length n
        m = file_in.shape[0]  #length of input file
        file_out = np.zeros(n)

        file_out[0] = file_in[0]
        file_out[-1] = file_in[-1]
          
        for i in range(1, n-1):
            out_frac = i/(n-1)
            #    print ('i, out_frac = ', i, out_frac)
            in_offset = out_frac*(m-1)
            index1 = int(in_offset)
            index2 = index1 + 1
            #    print ('in_offset, indeces = ', in_offset, index1, index2)
            f1 = float(file_in[index1])
            f2 = float(file_in[index2])
            file_out[i] = f1 + (f2-f1)*(in_offset-index1)
          
        return file_out

    def butter_lowpass_filter(self, data, cutoff_freq, fs, order=5):
        """
        Applies a Butterworth low-pass filter to the input data.

        Args:
            data (numpy.array): The input signal.
            cutoff_freq (float): The cutoff frequency of the filter (in Hz).
            fs (float): The sampling frequency of the signal (in Hz).
            order (int): The order of the filter.

        Returns:
            numpy.array: The filtered signal.
        """
        nyquist = 0.5 * fs
        normal_cutoff = cutoff_freq / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        filtered_data = filtfilt(b, a, data) # Use filtfilt for zero phase distortion
        return filtered_data
            

