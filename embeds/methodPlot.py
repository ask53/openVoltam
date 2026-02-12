"""
window_editSweepProfile.py

This file defines a class WindowEditConfig which creates a window object
that can be used to create a new sweep profile (if blank) or to edit
an existing profile. There are two ways to edit an existing profile because
there are two places a profile may be stored:
    1. In a standalone sweep profile file (with .ovp extention for 'Open Voltam Profile')
    2. Embedded in an Open Voltam sample file (.ovs).
In the first case, this window is passed a path to the .ovp file. If so,
it loads the sweep profile info which can be edited and either saved back to the
same file or Save-as'd to a new file name/location.
In the second case, both the path of the .ovs file as well as the unique ID of
the stored sweep profile is passed. As this is not being imported from a standalone
file, when "save" is pressed, it prompts the user to select a location and name
for the new file.

Both .ovs and .ovp files use tabular json format (an extension of json that allows
for tabular, comma-separated-value type data to be embedded within a json.

"""
from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

class MethodPlot(Canvas):
    def __init__(self):

        size_mm = g.APP.primaryScreen().physicalSize()
        width_in = size_mm.width() * g.MM2IN
        height_in = size_mm.height() * g.MM2IN

        self.fig = plt.figure(figsize=(width_in/1.75, height_in))
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        
        #self.steps = []
        #self.update_plot(self.steps, [])
        self.update_plot([], [])

        

    def update_plot(self, steps, relays, show_labels=False, show_xticks=True, reps=1):
        self.axes.cla()
        

        t = []
        v = []
        lbls = []
        t_ticks = [0]
        v_ticks = []


        ###################3 SORT THIS WITH NEW RELAY CONFIG ########
        '''segs = {g.M_STIR:[],
                g.M_VIBRATE:[],
                g.M_DATA_COLLECT:[]
                }'''

        segs_data = []
        segs_background = []
        segs_relays = []
        for i in range(len(relays)):
            segs_relays.append([])
        ###########################################

        
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

                if step[g.M_DATA_COLLECT] == g.M_DATA_SIGNAL:
                    segs_data.append((t0,t1))
                elif step[g.M_DATA_COLLECT] == g.M_DATA_BACKGROUND:
                    segs_background.append((t0,t1))
                for relay_id in step[g.M_RELAYS_ON]:
                    segs_relays[relay_id].append((t0,t1))
                    


                '''seg_data = []
                seg_background = []
                seg_relays = {}
                
                for key in segs:
                    if step[key]:
                        segs[key].append((t0,t1))'''
        
        try:
            self.axes.plot(t, v, 'black')
            self.axes.set_title('Applied voltage [V] vs. time [s]')
            
        
            
            
            adj = self.get_indicator_adjustment()
            [ymin, ymax] = self.axes.get_ylim()
            
            ################## AND HERE ###########################3
            '''seg_props = {g.M_STIR:{'pos':ymin-adj, 'color':'pink', 'lbl':'stir'},
                g.M_VIBRATE:{'pos':ymin-2*adj, 'color':'green', 'lbl':'vibrate'},
                g.M_DATA_COLLECT:{'pos':ymin-4*adj, 'color':'purple', 'lbl':'measure'}}'''
            

            relay_colors = ['magenta','springgreen']
            N_relays = len(relays)
            seg_relay_props = []
            k = 0
            for k in range(N_relays):
                seg_relay_props.append({'pos':ymin-k*adj, 'color':relay_colors[k%2], 'lbl':get_relay_text(relays[k], k)})
            seg_data_props = {'pos':ymin-(k+2)*adj, 'color':'darkviolet', 'lbl':'data'}
            seg_background_props = {'pos':ymin-(k+3)*adj, 'color':'thistle', 'lbl':'background'}

            #############################################################################################
            
            v_ticks.append(seg_data_props['pos'])
            v_ticks_lbl.append(seg_data_props['lbl'])
            v_ticks.append(seg_background_props['pos'])
            v_ticks_lbl.append(seg_background_props['lbl'])
            for prop in seg_relay_props:
                v_ticks.append(prop['pos'])
                v_ticks_lbl.append(prop['lbl'])
           
            for seg in segs_data:
                y = seg_data_props['pos']
                c = seg_data_props['color']
                self.axes.plot(seg, [y, y], color=c, linewidth=4)
           
            for seg in segs_background:
                y = seg_background_props['pos']
                c = seg_background_props['color']
                self.axes.plot(seg, [y, y], color=c, linewidth=4)
            
            for k, segs in enumerate(segs_relays):
                for seg in segs_relays[k]:
                    y = seg_relay_props[k]['pos']
                    c = seg_relay_props[k]['color']
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
            
            self.axes.set_yticks(v_ticks, v_ticks_lbl)
            self.axes.grid(True, linestyle='--', linewidth=0.2)

            if show_xticks:
                self.axes.set_xticks(t_ticks)
                for i,t in enumerate(t_ticks):
                    if t%1==0:
                        t_ticks[i] = int(t)
                    else:
                        t_ticks[i] = round(t, 2)
                self.axes.set_xticklabels(t_ticks, rotation=300)
            else:
                self.axes.set_xticks([])

            
            self.draw()
            
            
        except Exception as e:
            print(e)

    def get_step_name_position(self):
        [ymin, ymax] = self.axes.get_ylim()
        span = ymax-ymin
        pct_below = 0.05
        return ymax - pct_below*span

    def get_indicator_adjustment(self):
        [ymin, ymax] = self.axes.get_ylim()
        span = ymax-ymin
        pct_below = 0.05
        return pct_below*span

    def get_x_adj(self):
        [xmin, xmax] = self.axes.get_xlim()
        span = xmax-xmin
        return 0.015 * span

        
        
