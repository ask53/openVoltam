"""
runVoltagePlot.py


"""
import ov_globals as g
import ov_lang as l
from ov_functions import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

class RunVoltagePlot(Canvas):
    def __init__(self):

        size_mm = g.APP.primaryScreen().physicalSize()
        width_in = size_mm.width() * g.MM2IN
        height_in = size_mm.height() * g.MM2IN

        self.fig = plt.figure(figsize=(width_in, height_in))
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        
        self.steps = []
        self.line = False
        #self.update_plot(self.steps)

    def init_plot(self, method):
        self.method = method
        duration = get_method_duration(method[g.M_STEPS])
        [v_min, v_max] = get_method_v_extremes(method[g.M_STEPS])
        overhang = 0.05 * (v_max - v_min)
        
        self.axes.cla()
        self.axes.set_title('Voltage [V] vs. time [s]')
        self.axes.set_xlim(left=0, right=1.02*duration)
        self.axes.set_ylim(bottom=v_min-overhang, top=v_max+overhang)
        self.draw()    

    def update_plot(self, t, v):
        
        for line in list(self.axes.lines):     # remove all existing lines from plot
            line.remove()
            
        self.axes.plot(t, v, 'pink')
        self.draw()
        '''self.axes.cla()
        

        t = []
        v = []
        lbls = []
        t_ticks = [0]
        v_ticks = []
        segs = {g.M_STIR:[],
                g.M_VIBRATE:[],
                g.M_DATA_COLLECT:[]
                }
        v_ticks_lbl = []

        for rep in range(0,reps):
            for step in steps:
                if not t:
                    t0 = 0
                    t1 = step[g.M_T]
                else:
                    t0 = t[-1]
                    t1 = t[-1]+step[g.M_T]

                step_type = step[g.M_TYPE]
                if step_type == g.M_CONSTANT:
                    v0 = step[g.M_CONST_V]
                    v1 = v0
                elif step_type == g.M_RAMP:
                    v0 = step[g.M_RAMP_V1]
                    v1 = step[g.M_RAMP_V2]
                else:
                    show_alert(self, "Error!", "There was an issue plotting this method.")
                    return

                lbls.append(step[g.M_STEP_NAME])

                t.append(t0)
                t.append(t1)
                v.append(v0)
                v.append(v1)

                if t1 not in t_ticks:
                    t_ticks.append(t1)
                if v0 not in v_ticks:
                    v_ticks.append(v0)
                    v_ticks_lbl.append(str(v0)+'V')
                if v1 not in v_ticks:
                    v_ticks.append(v1)
                    v_ticks_lbl.append(str(v1)+'V')

                
                for key in segs:
                    if step[key]:
                        segs[key].append((t0,t1))
                    
        try:
            self.axes.plot(t, v, 'black')
            self.axes.set_title('Applied voltage [V] vs. time [s]')
            
        
            
            
            adj = self.get_indicator_adjustment()
            [ymin, ymax] = self.axes.get_ylim()
            seg_props = {g.M_STIR:{'pos':ymin-adj, 'color':'pink', 'lbl':'stir'},
                g.M_VIBRATE:{'pos':ymin-2*adj, 'color':'green', 'lbl':'vibrate'},
                g.M_DATA_COLLECT:{'pos':ymin-4*adj, 'color':'purple', 'lbl':'measure'}}
            for k in seg_props:
                v_ticks.append(seg_props[k]['pos'])
                v_ticks_lbl.append(seg_props[k]['lbl'])
            for k in segs:
                for seg in segs[k]:
                    y = seg_props[k]['pos']
                    c = seg_props[k]['color']
                    self.axes.plot(seg, [y, y], color=c, linewidth=4)

            if show_labels:
                v_max = self.get_step_name_position()
                lbl_x_adj = self.get_x_adj()
                for i, time in enumerate(t):
                    if i%2 == 0:                # for the start of each time interval
                        self.axes.text(time+lbl_x_adj, v_max, lbls[int(i/2)],{
                            'backgroundcolor':'#ffffffaa',
                            'rotation':'vertical',
                            'verticalalignment':'top',
                            'horizontalalignment':'left'
                            })
            

            if len(t)>0:
                self.axes.set_xlim(left=0, right=t[-1])
            self.axes.set_xticks(t_ticks)
            self.axes.set_yticks(v_ticks, v_ticks_lbl)
            self.axes.grid(True, linestyle='--', linewidth=0.2)
            for i,t in enumerate(t_ticks):
                if t%1==0:
                    t_ticks[i] = int(t)
            
            self.axes.set_xticklabels(t_ticks, rotation=300)

            
            self.draw()
            
            
        except Exception as e:
            print(e)'''



        
        
