"""
stdAddFitter.py

Shows selected points and draws a best-fit line. Returns y=mx+b format of line
as well as R^2 value of fit.


"""
from global_scripts import ov_globals as g

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.stats import linregress, t
from math import sqrt

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

class SubsetToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if t[0] in ('Home', 'Pan', 'Zoom')]

class StdAddCanvas(FigureCanvasQTAgg):
    def __init__(self, parent, width=5, height=4, dpi=100, title=False):
        fig = Figure(figsize=(width, height), dpi=dpi)
        if title:
            fig.suptitle(title)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class StdAddFitterPlot(QMainWindow):
    def __init__(self, parent, title=False):

        super().__init__()
        
        self.parent = parent
        self.type = None
        self.points = None
        self.results = False

        # Data to return to user 
        self.eqn = None
        self.slope = None
        self.intercept = None
        self.c_sample = None
        self.r2 = None
        self.stderr = None
        self.c_pre_dilution = None
        self.points_simple = None
        self.archived = False
        self.reg_type = None
        self.intervals = None

        self.color_avg = 'deeppink'
        self.color_rep = '#800080'
            
        size_mm = g.APP.primaryScreen().physicalSize()
        width_in = size_mm.width() * g.MM2IN
        height_in = size_mm.height() * g.MM2IN

        self.canvas = StdAddCanvas(self, width=width_in,                               # Create figure on canvas
                                            height=height_in, dpi=100, title=title)    
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

    def set_view_only(self):
        self.color_avg = 'grey'
        self.color_rep = 'grey'
        

    def set_axis_labels(self):
        self.canvas.axes.set_xlabel('Concentration of added standard [mg/L]')
        y_lbls = {g.C_TYPE_PEAKBASE: 'Peak height (from baseline) [uA]',
                  g.C_TYPE_PEAKZERO: 'Peak height (from zero) [uA]',
                  g.C_TYPE_SLOPE_L: 'Max |slope| on left side of peak [uA/V]',
                  g.C_TYPE_SLOPE_R: 'Max |slope| on right side of peak [uA/V]',
                  g.C_TYPE_SLOPE_AVG: 'Mean of max |slope| on both sides of peak [uA/V]'}
        if self.type:
            self.canvas.axes.set_ylabel(y_lbls[self.type])
            self.canvas.axes.yaxis.label.set_color('black')
            
        else:
            self.canvas.axes.set_ylabel('Please select a calculation type')
            self.canvas.axes.yaxis.label.set_color('red')
        self.canvas.draw()
        

    def update_type(self, calc_type):
        self.type = calc_type
        self.set_axis_labels()
        self.update_points(self.points)

    def update_reg_type(self, reg_type):
        self.reg_type = reg_type
        self.update_points(self.points)

    def update_points(self, points):
        self.points = points
        if not self.type:       # if there is no type, can't get y values!
            return
        if not self.points:     # if there are no points selected, nothing to update!
            return

        x_all = np.zeros(0)     # init arrays to hold data
        y_all = np.zeros(0)
        x_avg = np.zeros(0)
        y_avg = np.zeros(0)

        V_tot = 0
        N_tot = 0
        v0_sample = None
        v0_total = None
        self.points_simple = []
        for point in self.points:       # loop thru all points
            actual_points = 0
            y_sum = 0
            x = 0
            if point:
                self.points_simple.append([])
                actual_points = actual_points + 1
                run = point[0][2]       # grab the total volume, total mols As, and x value
                if run[g.R_TYPE] == g.R_TYPE_SAMPLE:        # based on the first run 
                    V_tot = V_tot + run[g.R_TOTAL_VOL]      # attached to this point
                    x = 0
                    v0_sample = run[g.R_SAMPLE_VOL]
                    v0_total = run[g.R_TOTAL_VOL]
                elif run[g.R_TYPE] == g.R_TYPE_STDADD:
                    V_tot = V_tot + run[g.R_STD_ADDED_VOL]
                    N_tot = N_tot + (run[g.R_STD_CONC] * run[g.R_STD_ADDED_VOL])            # As long as all vols and concs are in consistent units
                    x = N_tot / V_tot                                                       # The result will be in the standard concentration unit
                for replicate in point:                     # for each replicate in this point
                    (run_id, rep_id, run) = replicate
                    rep = self.get_rep_from_run(rep_id, run)
                    x_all = np.append(x_all, x)             
                    y = self.get_y(rep)                     # get y based on self.type             
                    y_sum = y_sum + y                       # sum ys for averaging later
                    y_all = np.append(y_all, y)
                    self.points_simple[-1].append({g.C_RUN_ID: run_id,
                                                   g.C_REP_ID: rep_id,
                                                   g.C_X: x,
                                                   g.C_Y: y})
                x_avg = np.append(x_avg, x)
                y_avg = np.append(y_avg, y_sum / len(point))# average ys

        self.plot_points(x_all, y_all, x_avg, y_avg, v0_sample, v0_total)

    def update_archived(self, calc):
        print('updating graph from archived!')
        m = calc[g.C_SLOPE]
        b = calc[g.C_INT]
        r_sq = calc[g.C_R2]
        std_err = calc[g.C_STDERR]
        self.eqn = f'y = {round(m,4)} * x + {round(b,4)}'
        self.slope = float(m)
        self.intercept = float(b)
        self.c_sample = float(b/m)
        self.r2 = float(r_sq)
        self.stderr = float(std_err)
        self.c_sample = float(calc[g.C_CONC_SAMPLE])
        self.c_pre_dilution = float(calc[g.C_CONC_ORIGINAL])
        self.archived = True
        self.calc_id = calc[g.R_UID_SELF]
        self.type = calc[g.C_TYPE]
        self.points_simple = calc[g.C_POINTS]
        self.intervals = calc[g.C_ERROR_MARGINS]

        x_all = np.zeros(0)     # init arrays to hold data
        y_all = np.zeros(0)
        x_avg = np.zeros(0)
        y_avg = np.zeros(0)

        for point in self.points_simple:
            print(point)
            print()
            y_sum = 0
            for rep in point:
                x = rep[g.C_X]
                y = rep[g.C_Y]
                x_all = np.append(x_all, x)
                y_all = np.append(y_all, y)
                y_sum = y_sum + y
            x_avg = np.append(x_avg, x)
            y_avg = np.append(y_avg, y_sum/len(point))
        
        self.plot_regression_line(x_avg, m, b, self.color_avg)
        self.label_regression_line(x_avg, y_avg, m, b, r_sq, self.color_avg)

        
        
        
            
        

    def get_rep_from_run(self, rep_id, run):
        """ returns a rep object from a run object and rep_id, the unique ID of the rep.
        If rep_id is not found in run[g.R_REPLICATES], returns False"""
        for rep in run[g.R_REPLICATES]:
            if rep[g.R_UID_SELF] == rep_id:
                return rep
        return False


    def get_y(self, rep):
        """Returns a floating point value from the dict, rep, based on which type
        of analysis has been selected in self.type by the user"""
        if self.type == g.C_TYPE_PEAKBASE:
            return rep[g.R_ANALYSIS][g.A_PEAK_HEIGHT]
        elif self.type == g.C_TYPE_PEAKZERO:
            return rep[g.R_ANALYSIS][g.A_PEAK_Y]
        elif self.type == g.C_TYPE_SLOPE_L:
            print('Not ready to run SLOPE_L calcs yet!')
            return 0
        elif self.type == g.C_TYPE_SLOPE_R:
            print('Not ready to run SLOPE_R calcs yet!')
            return 0
        elif self.type == g.C_TYPE_SLOPE_AVG:
            print('Not ready to run SLOPE_AVG calcs yet!')
            return 0
                
                
                
    def plot_points(self, x, y, x_avg, y_avg, v_sam, v_tot):
        """Takes in:
            x      -- numpy array of all x values
            y      -- numpy array of all y values
            x_avg  -- numpy array of mean x values
            y_avg  -- numpy array of mean y values
            v_sam  -- the volume of water sample added
            v_tot  -- the total volume of liquid in the initial solution analyzed as a 'sample'
        Plots the x v. y in one color, x_avg v. y_avg, in another color. If there are at least
        three data points on the average plot, it adds a linear regression trendline, displays
        the r-squared value, and stores the results on self."""
        
        self.canvas.axes.cla()                                                      # Clear the axes
        self.set_axis_labels()                                                      # Add axes labels back in
        self.allpts, = self.canvas.axes.plot(x,y, 'o', color=self.color_rep)            # Plot all data points in purple
        self.avgpts, = self.canvas.axes.plot(x_avg, y_avg, 'D', color=self.color_avg)   # Add averages as diamont points in pink
        
        if x_avg.size < 3:
            self.results = False
        else:                                                   # If there are enough points to do a linear regression
            if self.reg_type == g.C_REG_TYPE_PTS:               # if all points have same # of samples
                x_reg, y_reg = (x,y)
                color = self.color_rep
            elif self.reg_type == g.C_REG_TYPE_AVG:             # if some points have more data than others, to avoid skew:
                x_reg, y_reg = (x_avg, y_avg)      
                color = self.color_avg
                
            m, b, r_value, p_value, std_err = linregress(x_reg, y_reg)  # Calculate the regression!

            y_reg = self.plot_regression_line(x_avg, m, b, color)       #Add regression model to plot
                                                                        # Set up regression label
            self.label_regression_line(x_avg, y_reg, m, b, r_value*r_value, color)
            
            intervals = self.get_confidence_intervals(x_reg, y, m, b)
            
            # Store calculated values on the self variable
            
            self.eqn = f'y = {round(m,4)} * x + {round(b,4)}'
            self.slope = float(m)
            self.intercept = float(b)
            self.c_sample = float(b/m)
            self.r2 = float(r_value*r_value)
            self.stderr = float(std_err)
            self.c_pre_dilution = float(self.c_sample * v_tot / v_sam)
            self.intervals = intervals
            self.results = True
                   
        self.canvas.draw()

    def plot_regression_line(self, x_avg, m, b, color):
        y_reg = np.zeros(0)
        for x in np.nditer(x_avg, order='C'):                                   # Use regression to calculate y values for all displayed x
            y_reg = np.append(y_reg, m * x + b)
        self.reg, = self.canvas.axes.plot(x_avg, y_reg, '-', color=color)  # Add regression to plot
        return y_reg
        
    def label_regression_line(self, x, y, m, b, r_squared, color):
        (y0,y1) = self.canvas.axes.get_ylim()
        (x0,x1) = self.canvas.axes.get_xlim()
        yrange = y1-y0
        xrange = x1-x0
        textstart_x = float(x[0]) + 0.025*xrange
        textstart_y = m*textstart_x + b + 0.02*yrange
        angle_rad = np.arctan((float(y[-1]) - float(y[0])) / (float(x[-1]) - float(x[0])))
        angle_deg = 180 * angle_rad / np.pi
        lbl = 'R^2: '+str(round(r_squared, 4))
        self.canvas.axes.text(textstart_x, textstart_y, lbl, fontsize=11,
                                  rotation=angle_deg, rotation_mode='anchor', color=color,
                                  transform_rotates_text=True)

    def get_confidence_intervals(self, x_array, y_array, m, b):
        """Returns the 95% and 99% confidence interval +/- ranges for the x intercept
        of the regression line y = m * x + b, taking in the following arguments:
            - x_array   a numpy array of the x data to which the regression was fitted
            - y_array   a numpy array of the y data to which the regression was fitted
            - m   slope of the fit
            - b   y-intercept of the fit
        Returns: (95% value, 99% value)"""

        # get the standard deviation of y as a function of x (s_y)
        # s_y = sqrt(sum of squares of the regression / degrees of freedom) = sqrt(ssr/df)
        n = x_array.size
        ssr = 0
        for i,y in enumerate(y_array):
            y_reg = m * x_array[i] + b
            sr_i = (y-y_reg)*(y-y_reg)
            ssr = ssr + sr_i
        df = n - 2
        s_y = sqrt(ssr / df)

        # get mean values for x and y and sum of squares in x
        y_bar = np.mean(y_array)
        x_bar = np.mean(x_array)

        ssx = 0
        for x in x_array:
            ssx = ssx + (x-x_bar)*(x-x_bar)

        s_x = (s_y / abs(m)) * sqrt( (1/n) + (y_bar*y_bar / (m*m*ssx)) )

        # get student's t-value for various confidence levels

        confs = {}
        for i, conf in enumerate(g.M_CONFS_DATA):
            t_val = t.ppf((1+conf)/2, df)
            margin_of_error = float(t_val * s_x)
            confs[g.M_CONFS[i]] = margin_of_error

        return confs

    def get_results(self):
        if not self.results:
            return None
        
        res = {g.C_EQN: self.eqn,
               g.C_SLOPE: self.slope,
               g.C_INT: self.intercept,
               g.C_CONC_SAMPLE: self.c_sample,
               g.C_CONC_ORIGINAL: self.c_pre_dilution,
               g.C_R2: self.r2,
               g.C_STDERR: self.stderr,
               g.C_TYPE: self.type,
               g.C_REG_TYPE: self.reg_type,
               g.C_POINTS: self.points_simple,
               g.C_ERROR_MARGINS: self.intervals,
               g.C_ARCHIVED: self.archived}
            
        return res
            
        
