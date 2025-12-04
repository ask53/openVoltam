"""
run.py

This file defines a class WindowRun which creates a window
object that does the run. It follows the following algorithm:

1. Connect to device
2. Run the run in the file (accessed at self.parent.path) and
    determined by the argument run_uid
3. For each replicate:
    a. Shows the number of the current replicate and total # of reps
    b. Shows realtime graphs of the voltage being applied and the
    current being measured
4. At end of complete run (all replicates complete), saves
    all data to file. 
    
"""


import ov_globals as g
import ov_lang as l
from ov_functions import *

from potentiostat import Potentiostat

import serial.tools.list_ports
from re import sub

#from devices.supportedDevices import devices

#from functools import partial

#from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)

class WindowRun(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.data = False
        self.uid = False
        self.run = False
        self.method = False
        self.pstat = False
        self.setWindowTitle(l.r_window_title[g.L]+' | '+self.parent.data[g.S_NAME])
        
        w = QWidget()
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)
        

    def start_run(self, uid):
        self.uid = uid
        self.read_updated_file()
        self.run = get_run_from_file_data(self.data, self.uid)
        self.method = get_method_from_file_data(self.data, self.run[g.R_UID_METHOD])
        self.connect_to_device()
        if self.pstat:
            print('connected!')
            print('--REPS--')
            #################################################
            #
            # Turn off relays here!
            #
            #################################################
            self.set_dt()                               ###### SORT THIS OUTTTTT
            self.set_i_max()
            self.set_v_max()
            self.pstat.set_auto_connect(True)
            self.modify_method_for_run()
            for i,rep in enumerate(self.run[g.R_REPLICATES]):
                
                print(i)
                print(rep)
            print('-------')



            
            print('sample period')
            print(self.pstat.get_sample_period())
            print('sample rate')
            print(self.pstat.get_sample_rate())
            print('current range')
            print(self.pstat.get_curr_range())
            print('volt range (maxV)')
            print(self.pstat.get_volt_range())
            

        else:
            print('uh oh, we had trouble finding the',self.run[g.R_DEVICE],'please check the connections and try again')

        

    def connect_to_device(self):
        
        ###############################3
        #
        #   TODO
        #
        # 1. Rework this so we can confirm connection to the correct type of device.
        #       Currently, this fn just connects to the first device found whose
        #       name contains the string "USB Serial Device" which could be any
        #       number of devices =0
        
        if self.pstat:                              # if the potentiostat is already connected
            try:
                self.pstat.get_hardware_variant()        # run a command that would produce an error with another nonpotentiostat device
                return                              # if it doesn't throw and error, we're good to go with the current pstat!
            except:
                self.pstat = False                  # if it does throw an error, read on! 

        for port in serial.tools.list_ports.comports(): # loop thru all serial ports with connections
            if 'USB Serial Device' in port.description: # if the device name contains "USB Serial Device"
                try:
                    pstat = Potentiostat(port.device)   # try to connect as potentiostat
                    pstat.get_hardware_variant()        # run a command that would produce an error with another nonpotentiostat device
                    self.pstat = pstat                  # if no error, store that pstat object!
                    return
                except Exception as e:
                    print(e)
                    pass        # if we get an error in connecting on tihs port, keep trying the rest of the connected ports!

        

        
    def set_dt(self):
        ####################3
        #
        ### FIX THIS ONCE I HEAR BACK FROM WILL ABOUT THE UNITS OF SET_SAMPLE_PERIOD
        #
        ##################################################################
        
        #print(self.method[g.M_DT])
        #self.pstat.set_sample_period(self.method[g.M_DT])
        self.pstat.set_sample_rate(50)
        
    def set_i_max(self):
        self.pstat.set_curr_range(self.method[g.M_CURRENT_RANGE])
        
    def set_v_max(self):
        v_max_method = 0                                        # Get the maximum abs() voltage of the entire method
        for step in self.method[g.M_STEPS]:
            v_max_step = get_v_max_abs(step)
            if v_max_step > v_max_method:
                v_max_method = v_max_step

        v_ranges = self.pstat.get_all_volt_range()              # Grab the v_max options from the device
        v_ranges_int = []
        for v_range in v_ranges:
            v_ranges_int.append(int(sub("[^0-9]", "",v_range))) # And convert them from strings to integers

        v_max_i = g.QT_NOTHING_SELECTED_INDEX
        for i,v in enumerate(v_ranges_int):                     # Taking advantage of fact that they are sorted low->high
            print(v)
            print(v_max_method)
            if v_max_method <= v:                               # Loop thru all of them. As soon as a v_max setting exceeds
                print('breaking!')
                v_max_i = i                                     # the method's v_max, use that setting!
                break

        if v_max_i != g.QT_NOTHING_SELECTED_INDEX:              # if we have found a vmax, then set it
            v_max = v_ranges[v_max_i]
            self.pstat.set_volt_range(v_max)
        else:                                                   # otherwise, the V is too high, DONT RUN!!!
            print("the max voltage of this method exceeds the device's capability...")
            
    def modify_method_for_run(self):
        new_method = []
        relay_on = []
        for i in enumerate(g.M_RELAYS):
            relay_on.append(False)
        
        
        for step in self.method[g.M_STEPS]:
            #new_steps = []
            for i, relay in enumerate(g.M_RELAYS):
                if not relay_on[i] and step[relay]:     # if the relay is OFF and needs to be ON for this step
                    new_method.append({                 # append a step to the method turning this relay ON
                        g.M_TYPE: g.M_RELAY,
                        g.M_RELAY: relay,
                        g.M_RELAY_STATE: True})
                    relay_on[i] = True
                elif relay_on[i] and not step[relay]:   # if the relay is ON and needs to be OFF for this step
                    new_method.append({                 # append a step to the method turning this relay OFF
                        g.M_TYPE: g.M_RELAY,
                        g.M_RELAY: relay,
                        g.M_RELAY_STATE: False})
                    relay_on[i] = False
            new_method.append(step)                     # then append the step itself

        for i, relay in enumerate(g.M_RELAYS):          # at end, add steps for turning off all relays as needed
            if relay_on[i]:
                new_method.append({
                    g.M_TYPE: g.M_RELAY,
                    g.M_RELAY: relay,
                    g.M_RELAY_STATE: False})

        self.method = new_method
        
    def read_updated_file(self):
        self.parent.load_sample_info()
        self.data = self.parent.data
    
    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.setEnabledChildren(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        self.parent.setEnabled(True)
        self.parent.setEnabledChildren(True)
        event.accept()
