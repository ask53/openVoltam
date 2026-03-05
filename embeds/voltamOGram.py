"""
voltamOGram.py

Shows a voltamogram of passed runs. Gives user the option to
analyze for baselines and peak location/heigh or not.

There are two ways to add data to the plot:

- plot_reps:
    This takes in a list of reps (can correspond to any runs, including
    multiple reps of the same run). Plots all lines corresponding to the
    same run as the same color/style UNLESS there are only reps from a single
    run provided, in which case all reps are given distinct colors & styles.
    If a single rep is passed, raw data is also displayed.
    The legend that is displayed shows run ID UNLESS there are only reps
    from a single run provided, in which case it shows run ID and rep ID
- plot runs
    This takes in a list of runs. It plots all reps with data for those
    runs. All reps of the same run are styled (color and linestyle) the
    same. A legend is displayed that shows the styles for each run.

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
    def __init__(self, parent, width=5, height=4, dpi=100, title=False):
        fig = Figure(figsize=(width, height), dpi=dpi)
        if title:
            fig.suptitle(title)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class VoltamogramPlot(QMainWindow):
    def __init__(self, parent, title=False):
        try:
            super().__init__()

            self.parent = parent
            self.dragging_end = False
            self.dragging_peak = False
            self.drag_index = 0
            
            size_mm = g.APP.primaryScreen().physicalSize()
            width_in = size_mm.width() * g.MM2IN
            height_in = size_mm.height() * g.MM2IN

            self.canvas = VoltamogramCanvas(self, width=width_in,                               # Create figure on canvas
                                            height=height_in, dpi=100, title=title)    
            toolbar = SubsetToolbar(self.canvas, self)                                          # set canvas toolbar

            self.set_axis_labels()
            self.axes = self.canvas.axes

            self.colors = ['deeppink','limegreen','chocolate','mediumturquoise','gold','purple','red','blue']
            self.linestyles = ['solid', 'dotted', 'dashed', 'dashdot']
                
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

    def plot_rep(self, rep, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False, color='black', linestyle='solid', lbl=''):
        
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
                self.canvas.axes.plot(x, y_raw, 'lightgrey', linestyle=linestyle,
                                      linewidth=1, label='raw data')

            # 7. Show smoothed data
            self.smoothed, = self.canvas.axes.plot(x, y, color, linestyle=linestyle,
                                  linewidth=2, label=lbl, picker=2)          # then show smoothed, filtered data on top.

            if predictpeak:

                ###################################
                #
                #   REDO THIS BUT WITH [x0,y0] and [x1,y1] as np.ndarray types
                #
                self.x = x      # store x and y for access from mouseclick/move handlers
                self.y = y
                self.base_x = np.array([x[1], x[-2]])
                self.base_y = np.array([y[1], y[-2]])
                self.active_endpoint = 0
                
                #
                ep0, = self.canvas.axes.plot(self.base_x[0], self.base_y[0], 'o',
                                             mfc='#80008033',mec='black', mew=2,
                                             markersize='36', picker=40)

                ep1, = self.canvas.axes.plot(self.base_x[1], self.base_y[1], 'o',
                                             mfc='#80008033', mec='None', mew=2,
                                             markersize='36', picker=40)
                self.endpoints = (ep0,ep1)

                self.baseline, = self.canvas.axes.plot(self.base_x, self.base_y, '-',
                                                       color='#800080bb')

                tempxy = np.array([0,0])
                self.peakline, = self.canvas.axes.plot(tempxy, tempxy, '-', color='#00ddff')
                self.peakpoint, = self.canvas.axes.plot(0, 0, 'o', mfc='#013ea833',
                                                        mec='None',
                                                        markersize='18', picker=18)
                self.guess_peak()
                #
                #
                #   HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE HERE 
                #
                #####################################################
                
                self.canvas.callbacks.connect('pick_event', self.on_pick)
                self.canvas.mpl_connect('button_release_event', self.on_but_release)
                self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    







                
            self.canvas.draw()
            

            
            # 8. If predictpeak, show baseline (with adjustable handles) and peak location
                

    def toggle_endpoint(self):
        if self.active_endpoint == 0: self.active_endpoint = 1
        else: self.active_endpoint = 0
        for i,ep in enumerate(self.endpoints):
            if i == self.active_endpoint: ep.set_mec('black')
            else: ep.set_mec('None')
        self.canvas.draw_idle()
            
        
    

    def on_pick(self, event):
        ind = event.ind
        print('Artist picked: ')
        print(event.artist)
        if event.artist in self.endpoints:                              # if an endpoint was picked
            self.dragging_end = True                                        # set dragging flag
            self.drag_index = self.endpoints.index(event.artist)        # get index of picked endpoint
        elif event.artist == self.smoothed:                             # if a point on smoothed data curve picked
            if event.mouseevent.xdata:                                  
                i = (np.abs(self.x - event.mouseevent.xdata)).argmin()  # get index of picked point
                self.move_endpoint(self.active_endpoint,
                                   self.x[i], self.y[i])                # move the active endpoint to picked point
        elif event.artist == self.peakpoint:
            self.dragging_peak = True

    def on_but_release(self, event):
        self.dragging_end = False
        self.dragging_peak = False

    def on_mouse_move(self, event):
        if self.dragging_end:
            if event.xdata:
                i = (np.abs(self.x - event.xdata)).argmin() # get index
                self.move_endpoint(self.drag_index, self.x[i], self.y[i])
        elif self.dragging_peak:
            if event.xdata:
                print('snapping peak!')
                i = (np.abs(self.x - event.xdata)).argmin() # get index
                self.snap_peak(i)
                
                

    def move_endpoint(self, i, x, y):
        # move point with index i to position (x,y)
        self.base_x[i] = x
        self.base_y[i] = y

        self.endpoints[i].set_xdata([x])
        self.baseline.set_xdata(self.base_x)
        self.endpoints[i].set_ydata([y])
        self.baseline.set_ydata(self.base_y)

        self.guess_peak()

        self.canvas.draw_idle()

    def guess_peak(self):
        i_lo = np.argmin(self.base_x)
        i_hi = 1-i_lo

        x0 = self.base_x[i_lo]
        y0 = self.base_y[i_lo]
        x1 = self.base_x[i_hi]
        y1 = self.base_y[i_hi]

        if x0==x1:          # if the endpoints are on top of one another
            x_max = x0      # do this to avoid a divide-by-zero error
            y_max = y0
            y_max_base = y0
        
        else:
            m = float(y1-y0)/float(x1-x0)   # slope of baseline
            b = y0-m*x0                     # y intercept of baseline

            x_min_index = np.where(self.x == x0)[0][0]  # get data index of lower bound
            x_max_index = np.where(self.x == x1)[0][0]  # get data index of upper bound

            i_max = np.argmax(self.y[x_min_index:x_max_index]) + x_min_index    # get index of highest point between bounds

            y_max = self.y[i_max]
            x_max = self.x[i_max]
            y_max_base = m * x_max + b

        self.set_peak(x_max, y_max_base, y_max)

    def snap_peak(self, i):
        """Snaps the peak to nearest local max within a tolerance.
        If there isn't one, leaves it where the user left it."""
        tolerance = 3

        i_lo = np.argmin(self.base_x)
        i_hi = 1-i_lo

        x0 = self.base_x[i_lo]
        x1 = self.base_x[i_hi]

        if self.x[i] > x0 and self.x[i] < x1:
            
            ################################# HERE ########################################## HERE #########################
            #
            #
            #   If there is a local max within the tolerance of the selected x value,
            #       snap the peak to that local max
            #   Otherwise, put the peak wherever the user requested
            #
            #############################################
            pass
        
            
        


    def set_peak(self, x, y0, y1):
        
        self.peakline.set_xdata([x,x])
        self.peakline.set_ydata([y0,y1])
        self.peakpoint.set_xdata([x])
        self.peakpoint.set_ydata([y1])
        
        

        

        

        


        
        


    def plot_reps(self, reps, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False):
        # 1. Get data from file for specified reps
        all_data = get_data_from_file(self.parent.path)     # read file including all raw data
        
        reps_to_disp = []
        runs_to_disp = []
        for task in reps:
            (run_id, rep_id) = task
            if not run_id in runs_to_disp:      # Get list of unique run IDs
                runs_to_disp.append(run_id)
            found = False
            rep = {'run_uid':run_id,
                   'rep_uid':rep_id}
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
            reps_to_disp.append(rep)
            print(reps_to_disp)

        onerun = False
        if len(runs_to_disp) == 1: onerun=True
            

           

        
        
        
        # 2. Loop thru runs, plotting each rep
        run_colors = {}
        lstyles = {}
        runs_displayed = []
        for rep in reps_to_disp:
            if onerun: indexer = rep['rep_uid']
            else: indexer = rep['run_uid']
            
            if indexer in list(run_colors.keys()):
                color = run_colors[indexer]
                lstyle = lstyles[indexer]
            else:
                color = self.colors[len(run_colors)%len(self.colors)]
                lstyle = self.linestyles[len(lstyles)%len(self.linestyles)]
                run_colors[indexer] = color
                lstyles[indexer] = lstyle
            if indexer in runs_displayed:
                lbl = ''
            else:
                if onerun: lbl = rep['run_uid']+', '+rep['rep_uid']
                else: lbl = rep['run_uid']
                
            self.plot_rep(rep, subbackground=subbackground, smooth=smooth,
                          lopass=lopass, showraw=showraw, predictpeak=predictpeak,
                          color=color, linestyle=lstyle, lbl=lbl)
            runs_displayed.append(rep['run_uid'])

        # 3. Add legend
        if not predictpeak:
            self.canvas.axes.legend()
        
        

    def plot_runs(self, runs, subbackground=True, smooth=True, lopass=True, showraw=False, predictpeak=False):
        # 1. Get data from file for specified runs
        all_data = get_data_from_file(self.parent.path)     # read file including all raw data

        runs_to_show = []
        for run in runs:
            run_id = run[g.R_UID_SELF]
            found = False
            for fullrun in all_data[g.S_RUNS]:
                if fullrun[g.R_UID_SELF] == run_id:
                    runs_to_show.append(fullrun)
                    found = True
                    break
                
    
        # 2. Loop thru runs, plotting each rep
        for i,run in enumerate(runs_to_show):
            color = self.colors[i%len(self.colors)]
            lstyle = self.linestyles[i%len(self.linestyles)]
            for j,rep in enumerate(run[g.R_REPLICATES]):
                if j==0: lbl=run[g.R_UID_SELF]+' ('+run[g.R_TYPE]+')'
                else: lbl = ''
                self.plot_rep(rep, subbackground=subbackground, smooth=smooth,
                              lopass=lopass, showraw=showraw, predictpeak=predictpeak,
                              color=color, linestyle=lstyle, lbl=lbl)

        # 3. Add legend
        self.canvas.axes.legend()

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

    def get_line_count(self):
        return len(self.canvas.axes.get_lines())
        

    def get_analysis_results(self):
        return {g.A_PEAK_X: 'x-peak',
                g.A_PEAK_Y: 'y-peak',
                g.A_PEAK_HEIGHT: 'peak-height',
                g.A_BASE_0_X: 'base0-x',
                g.A_BASE_0_Y: 'base0-y',
                g.A_BASE_1_X: 'base1-x',
                g.A_BASE_1_Y: 'base1-y'}

