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
        from a single run provided, in which case it shows run ID and rep ID.
    IF a single rep is passed AND predictpeak==True, then no legend is displayed.
        instead, baselines and peaklines are displayed and the user can
        interact with these plot features to get peak height.
- plot runs
    This takes in a list of runs. It plots all reps with data for those
    runs. All reps of the same run are styled (color and linestyle) the
    same. A legend is displayed that shows the styles for each run.

"""

from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, butter, filtfilt, argrelextrema

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
            x = self.resize_data(x, g.VOG_RESIZE)
            y = self.resize_data(y, g.VOG_RESIZE)

            if rep[g.R_BACKGROUND]:
                x_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_VOLT]].values)
                x_back = x_back.reshape(x_back.shape[0])
                y_back = np.array(pd.DataFrame(rep[g.R_BACKGROUND])[[g.R_DATA_CURR]].values)
                y_back = y_back.reshape(y_back.shape[0])

                ###### DO NOT RESIZE EITHER SIGNAL OR BACKGROUND
                #
                '''
                if x.size > x_back.size:
                    x_back = self.resize_data(x_back, x.size)
                    y_back = self.resize_data(y_back, x.size)
                elif x.size < x_back.size:
                    x = self.resize_data(x, x_back.size)
                    y = self.resize_data(y, x_back.size)
                '''
                #
                ##################################################

            else:
                x_back, y_back = (np.zeros(0), np.zeros(0))

            # 2. If background is present & subbackground==True, interpolate background and subtract
            if x_back.size and subbackground:
                y_back = np.interp(x, x_back, y_back)   # interpolate background to match voltage of signal
                y = y - y_back                          # subtrack background from signal

            
            # 3. If smooth, smooth result
            y_raw = y.copy()                        # store copy of y as y_raw in case we want to display it to user    
            method = rep[g.R_UID_METHOD]            # get method from rep
            window = method[g.M_SG_WINDOW]
            order = method[g.M_SG_ORDER]
            
            if method[g.M_SG]:
                y = savgol_filter(y, window_length=window,
                                  polyorder=order, mode='nearest')

            # 4. If lopass, pass result thru lopass filter
            if method[g.M_LP]:
                y = self.butter_lowpass_filter(y, method)


            # 5. If predictpeak, guess baseline and peak locations, store as vars in self
            if predictpeak:
                peak, base = self.get_predicted_basepoints(x, y, method)
            
            # 6. Show final result
            if showraw:                                 # first, show raw data if requested
                self.canvas.axes.plot(x, y_raw, 'lightgrey', linestyle=linestyle,
                                      linewidth=1, label='raw data')

            # 7. Show smoothed data
            self.smoothed, = self.canvas.axes.plot(x, y, color, linestyle=linestyle,
                                  linewidth=2, label=lbl, picker=2)          # then show smoothed, filtered data on top.

            # 8. If predictpeak, show baseline (with adjustable handles) and peak location
            if predictpeak:
                self.x = x      # store x and y for access from mouseclick/move handlers
                self.y = y
                self.base_x = np.array(base[0])
                self.base_y = np.array(base[1])
                self.active_endpoint = 0
                self.peak_x = peak[0]
                self.peak_y = peak[1]
                
                ep0, = self.canvas.axes.plot(self.base_x[0], self.base_y[0], 'o',               # set the left baseline endpoint
                                             mfc='#80008033',mec='black', mew=2,
                                             markersize='36', picker=40)

                ep1, = self.canvas.axes.plot(self.base_x[1], self.base_y[1], 'o',               # set the right baseline endpoint
                                             mfc='#80008033', mec='None', mew=2,
                                             markersize='36', picker=40)
                
                self.baseline, = self.canvas.axes.plot(self.base_x, self.base_y, '-',           # draw the baseline between the endpoints
                                                       color='#800080bb')

                tempxy = np.array([self.peak_x,self.peak_x]) 
                self.peakline, = self.canvas.axes.plot(tempxy, tempxy, '-', color='#00ddff')    # draw the line from baseline to peak
                self.peakpoint, = self.canvas.axes.plot(self.peak_x, self.peak_y, 'o',          # draw the peak marker
                                                        mfc='#013ea833', mec='None',
                                                        markersize='18', picker=18)
                self.endpoints = (ep0,ep1)                                                      # store the endpoint graphs on self

                self.guess_peak()                                                               # guess the peak between the endpoints

                # Connect callback handlers for picking the graph, clicking the graph, and moving the mouse
                self.canvas.callbacks.connect('pick_event', self.on_pick)
                self.canvas.mpl_connect('button_release_event', self.on_but_release)
                self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
                
            self.canvas.draw()


    #####################################################
    #                                                   #
    #   PEAK FINDING FUNCTIONS AND THEIR FRIENDS        #
    #           (BETWEEN REVOLUTIONS :P )               #
    #                                                   #
    #   1. get_local_extremes()                         #
    #   2. get_x_y_valules()                            #
    #   3. get_index_of_closest_vaule(l, val)           #
    #   4. get_predicted_basepoints()                   #
    #                                                   #
    #####################################################

    def get_local_extremes_i(self, data):
        data = np.gradient(data)
        prev_d = None
        mins = []
        maxes = []
        for i,d in enumerate(data):
            if d == 0:
                pass
            elif prev_d:
                if d*prev_d < 0:  # if this and the previous data point are on oposite sides of zero
                    if prev_d > 0:
                        if abs(d)<abs(prev_d): maxes.append(i)
                        else: maxes.append(i-1)
                    else:
                        if abs(d)<abs(prev_d): mins.append(i)
                        else: mins.append(i-1)
                prev_d = d
            else:
                prev_d = d
    
        return mins, maxes

    def get_x_y_values(self, x, y, iz):
        """Takes in:
        - x, a numpy array of x values
        - y, a numpy array of y values
        - iz, a list of indices such that all indices in iz are on both x and y
        ALGORITHM:
        For each index, grab the corresponding x and y values.
        Returns:
          - [0], a list of the x values at the indices
          - [1], a list of the y values at the indices"""
        ext_x = []
        ext_y = []
        for i in iz:
            ext_x.append(float(x[i]))
            ext_y.append(float(y[i]))
        return ext_x, ext_y

    def get_index_of_closest_value(self, l, val):
        """takes in a list of floats or ints, l, and a vaule (float or int).
        Returns the index of the value in l which is closest to val"""
        difs = []
        for el in l:
            dif = abs(float(val)-float(el))
            difs.append(dif)
        min_dif = min(difs)
        return difs.index(min_dif)

    def get_predicted_basepoints(self, x, y, method):
        base = ((x[0], x[-1]), (y[0], y[-1]))               # set defaullt basepoints to ends of curve
        peak = (0,0)
        
        I_d1 = np.gradient(y, x)                            # 1st deriv
        I_d2 = np.gradient(I_d1, x)                         # 2nd deriv
        I_d3 = np.gradient(I_d2, x)                         # 3rd deriv
             
        mins0_i, maxes0_i = self.get_local_extremes_i(y)         # maxes/mins of originall function
        mins2_i, maxes2_i = self.get_local_extremes_i(I_d2)      # maxes/mins of 2nd deriv
        mins3_i, maxes3_i = self.get_local_extremes_i(I_d3)      # maxes/mins of 3rd deriv

        # 1. Guess the peak
        peaks_x, peaks_y = self.get_x_y_values(x, y, maxes0_i)   # get x and y vaules of the local maxes of y

        if len(peaks_x) == 0:                               # no peaks id'd, set baseline endpoints to end of run values
            return peak, base 
                                                    
        vmin = method[g.M_PEAK_V_MIN]                       # if there is at least 1 identified peak    
        vmax = method[g.M_PEAK_V_MAX]                       # grab the index of the peak closest to the middle
        x_mid = vmin + (vmax-vmin)/2.                       # of the user-set expected peak voltage range
        i = self.get_index_of_closest_value(peaks_x, x_mid)

        peak = (peaks_x[i],peaks_y[i])
        peak_i = maxes0_i[i]

        # 2. Guess the basepoints 
        bp_candidates_i = mins0_i + maxes2_i + maxes3_i     # Start with all possible basepoints (mins of y or maxes of y'' or y''')
        bps_left_i = []
        bps_right_i = []
        n = x.size
        cutoff_i = 0.075*n                                  # define a cutoff (nearness to the end for which we'll ignore possible basepoints)
        
        for bp_i in bp_candidates_i:
            if bp_i > cutoff_i and bp_i < n - cutoff_i:     # discard any possible basepoints that are too close to ends of data
                if bp_i < peak_i:                           # if basepoint to the left of peak
                    bps_left_i.append(bp_i)                 #   add it to the list of possible basepoints left of peak
                elif bp_i > peak_i:                         # if its to the right of the peak (ok to discard peak)
                    bps_right_i.append(bp_i)                #   add it to the list of possible basepoints right of peak

        bp_pairs_i = []                                     # Build a list of possible basepoints, inculde distance between them
        for i in bps_left_i:
            for j in bps_right_i:
                bp_pairs_i.append({'left': i,
                                   'right': j,
                                   'dif': j-i})
                                            
        bp_pairs_i = list(reversed(sorted(bp_pairs_i, key=lambda x: x['dif'])))     # sort the list from largest to smallest difference
        bp_found = False
        for pair in bp_pairs_i:                             # loop through all possible pairs (from furthest apart to closest)
            i1, i2 = pair['left'], pair['right']            # as soon as we find a pair whose baseline doesn't intersect the curve
            x1, y1, x2, y2 = x[i1], y[i1], x[i2], y[i2]     # at all, those are our baselines!
            m = (y2 - y1) / (x2 - x1)                       # slope
            b = y2 - m*x2                                   # intercept

            blx = x[i1+1:i2]                                # array of x vaules for baseline (exculde actual baseline points where baseline for sure intersects
            bly = []                
            for val in blx:
                bly.append(m*val+b)                         # for each baseline x value, get the corresponding baseline y value (y = mx+b)

            y_sub = y[i1+1:i2]                              # subset of y that matchest range of this particular baseilne

            bly = np.array(bly)                             # convert to np arrays for intersection comparison
            y_sub = np.array(y_sub)

            intersections = np.argwhere(np.diff(np.sign(y_sub-bly))).flatten() # get list of indices of intersection points between baseline and curve

            if len(intersections) == 0:                     # if the lines don't cross
                bp_found = True                             # we found our suggested baseline!
                break

        if bp_found:                                        # if a baseline was found, 
            base = ((x1, x2), (y1,y2))                      #   overwrite the default baselines with our new found baseline

        return peak, base

            
    #################################################
    #                                               #
    #   Interactivity handlers (and their friends)  #
    #                                               #
    #   1. on_pick                                  #
    #   2. on_but_release                           #
    #   3. on_mouse_move                            #
    #   4. move_endpoint                            #
    #   5. guess_peak                               #
    #   6. drag_peak                                #
    #   7. set_peak                                 #
    #   8. get_baseline_params                      #
    #                                               #
    #################################################

    def on_pick(self, event):
        """Handler for when a pick event is registered on plot"""
        
        ind = event.ind
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
        """Handler for when a mouse button is released"""
        
        self.dragging_end = False
        self.dragging_peak = False

    def on_mouse_move(self, event):
        """Handler for every time a mouse-moved event is regisered on plot"""
        
        if self.dragging_end:
            if event.xdata:
                i = (np.abs(self.x - event.xdata)).argmin() # get index
                self.move_endpoint(self.drag_index, self.x[i], self.y[i])
        elif self.dragging_peak:
            if event.xdata:
                i = (np.abs(self.x - event.xdata)).argmin() # get index
                self.drag_peak(i)
                
                

    def move_endpoint(self, i, x, y):
        """moves baseline endpoint with index i to position (x,y).
        Updates peakline position to match adjusted baseline."""
        
        self.base_x[i] = x
        self.base_y[i] = y

        self.endpoints[i].set_xdata([x])
        self.baseline.set_xdata(self.base_x)
        self.endpoints[i].set_ydata([y])
        self.baseline.set_ydata(self.base_y)

        self.guess_peak()

        self.canvas.draw_idle()

    def guess_peak(self):
        """Guesses where the peak should be and moves the peakline
        and the peakpoint to that position.
        ALGORITHM: picks highest point between the two endpoints
            of the baseline."""
        
        (x0, y0, x1, y1, m, b) = self.get_baseline_params()

        if x0==x1:          # if the endpoints are on top of one another
            x_max = x0      # do this to avoid a divide-by-zero error
            y_max = y0
            y_max_base = y0
        else:
            x_min_index = np.where(self.x == x0)[0][0]  # get data index of lower bound
            x_max_index = np.where(self.x == x1)[0][0]  # get data index of upper bound
            
            i_max = np.argmax(self.y[x_min_index:x_max_index]) + x_min_index    # get index of highest point between bounds

            y_max = self.y[i_max]
            x_max = self.x[i_max]
            y_max_base = m * x_max + b

        self.set_peak(x_max, y_max_base, y_max)

    def drag_peak(self, i):
        """Drags the peak to the selected location, within the bounds
        of the baseline.
        
        ***Possible future expansion***: a feature that
        auto-snaps the peakline to local maxima, that can be toggled
        on and off from the settings."""
        (x0, y0, x1, y1, m, b) = self.get_baseline_params()
        if self.x[i] > x0 and self.x[i] < x1:
            x = self.x[i]
            y_base = m*x+b
            y = self.y[i]

            self.set_peak(x,y_base,y)
            self.canvas.draw_idle()
     

    def set_peak(self, x, y0, y1):
        """Moves the peakline  as a vertical line extending
        up from (x, y0) to (x, y1) and moves peakpoint accordingly."""
        
        self.peak_x = x
        self.peak_y = y1
        self.peakline.set_xdata([x,x])
        self.peakline.set_ydata([y0,y1])
        self.peakpoint.set_xdata([x])
        self.peakpoint.set_ydata([y1])

    def get_baseline_params(self):
        """lower bound of baseline: (x0, y0)
        upper bound of baseline: (x1, y1)
        slope of baseline: m
        y-intercetp of baseline: b

        returns (x0, y0, x1, y1, m, b)"""
        
        i_lo = np.argmin(self.base_x)
        i_hi = 1-i_lo

        x0 = self.base_x[i_lo]
        y0 = self.base_y[i_lo]
        x1 = self.base_x[i_hi]
        y1 = self.base_y[i_hi]

        if x0==x1:                      # avoid divide-by-zero error
            return (x0, y0, x1, y1, 0, 0)
        
        m = float(y1-y0)/float(x1-x0)   # slope of baseline
        b = y0-m*x0                     # y intercept of baseline
        return (x0, y0, x1, y1, m, b)

    def get_derivs(self):
        (x0, y0, x1, y1, m, b) = self.get_baseline_params()
        x0i = np.where(self.x==x0)[0][0]
        x1i = np.where(self.x==x1)[0][0]
        peakxi = np.where(self.x==self.peak_x)[0][0]

        x_left = self.x[x0i:peakxi]
        y_left = self.y[x0i:peakxi]
        x_right = self.x[peakxi:x1i]
        y_right = self.y[peakxi:x1i]

        d_left = np.gradient(y_left, x_left)
        d_right = np.gradient(y_right, x_right)

        l_max = abs(float(max(d_left)))
        r_max = abs(float(min(d_right)))
        mean_max = (l_max + r_max) / 2.

        return l_max, r_max, mean_max        
        

    #####################################
    #                                   #
    #   Run and rep pre-plot functions  #
    #                                   #
    #   1. plot_reps                    #
    #   2. plot_runs                    #
    #                                   #
    #####################################

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

                    # grab method details for this run to pass to plotter
                    run = get_run_from_file_data(all_data, run_id)
                    method_id = run[g.R_UID_METHOD]
                    method = get_method_from_file_data(all_data, method_id)
                    



                    for fullrep in fullrun[g.R_REPLICATES]:
                        if fullrep[g.R_UID_SELF] == rep_id:
                            found = True
                            try: 
                                rep[g.R_DATA] = fullrep[g.R_DATA]               # grab data if there is any
                            except Exception as e:
                                print(e)
                                rep[g.R_DATA] = []
                            try:
                                rep[g.R_BACKGROUND] = fullrep[g.R_BACKGROUND]   # grab background data if there is any
                            except Exception as e:
                                print(e)
                                rep[g.R_BACKGROUND] = []
                            break
                    if found: break
            if rep[g.R_DATA] or rep[g.R_BACKGROUND]:
                rep[g.R_UID_METHOD] = method
                reps_to_disp.append(rep)

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
        if reps_to_disp:
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
        any_display = False
        for i,run in enumerate(runs_to_show):
            color = self.colors[i%len(self.colors)]
            lstyle = self.linestyles[i%len(self.linestyles)]
            run_displayed = False
            for j,rep in enumerate(run[g.R_REPLICATES]):
                if rep[g.R_DATA] or rep[g.R_BACKGROUND]:
                    if not run_displayed: lbl=run[g.R_UID_SELF]+' ('+run[g.R_TYPE]+')'
                    else: lbl = ''
                    run_displayed = True
                    any_display = True
                    self.plot_rep(rep, subbackground=subbackground, smooth=smooth,
                                  lopass=lopass, showraw=showraw, predictpeak=predictpeak,
                                  color=color, linestyle=lstyle, lbl=lbl)

        # 3. Add legend
        if any_display:
            self.canvas.axes.legend()


    #############################################
    #                                           #
    #   Helper functions for data processing    #
    #                                           #
    #   1. resize_data                          #
    #   2. butter_lowpass_filter                #
    #                                           #
    #############################################

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

    def butter_lowpass_filter(self, data, method):
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
        order = method[g.M_LP_ORDER]
        freq = method[g.M_LP_FREQ]
        b, a = butter(order, freq, btype='low', analog=False)
        filtered_data = filtfilt(b, a, data) # Use filtfilt for zero phase distortion
        return filtered_data


    #####################################
    #                                   #
    #   Fns to be called by external    #
    #                                   #
    #   1. get_line_count               #
    #   2. toggle_endpoint              #
    #   3. get_analysis_results         #
    #                                   #
    #####################################

    def get_line_count(self):
        return len(self.canvas.axes.get_lines())

    def toggle_endpoint(self):
        if self.active_endpoint == 0: self.active_endpoint = 1
        else: self.active_endpoint = 0
        for i,ep in enumerate(self.endpoints):
            if i == self.active_endpoint: ep.set_mec('black')
            else: ep.set_mec('None')
        self.canvas.draw_idle()

    def set_analysis(self, data):
        try:
            x0 = data[g.A_BASE_0_X]
            y0 = data[g.A_BASE_0_Y]
            x1 = data[g.A_BASE_1_X]
            y1 = data[g.A_BASE_1_Y]
            xp = data[g.A_PEAK_X]
            yp = data[g.A_PEAK_Y]
            yp_base = yp - data[g.A_PEAK_HEIGHT]

            self.move_endpoint(0, x0, y0)
            self.move_endpoint(1, x1, y1)
            self.set_peak(xp, yp_base, yp)
            
        except Exception as e:
            print(e)
            return
        
    def get_analysis_results(self):
        (x0, y0, x1, y1, m, b) = self.get_baseline_params()
        y_base = m*self.peak_x+b
        ht = self.peak_y-y_base
        deriv_l, deriv_r, deriv_avg = self.get_derivs()
        
        return {g.A_PEAK_X: float(self.peak_x),
                g.A_PEAK_Y: float(self.peak_y),
                g.A_PEAK_HEIGHT: float(ht),
                g.A_BASE_0_X: float(x0),
                g.A_BASE_0_Y: float(y0),
                g.A_BASE_1_X: float(x1),
                g.A_BASE_1_Y: float(y1),
                g.A_DERIV_LEFT: deriv_l,
                g.A_DERIV_RIGHT: deriv_r,
                g.A_DERIV_MEAN: deriv_avg}
