#run.py
#
# This is the script that runs the method directly on the potentiostat

import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path

from ast import literal_eval
import time
import serial.tools.list_ports

from potentiostat import Potentiostat

import ov_globals as g
from ov_functions import *

# Grab arguments and convert them from strings to intended types, store in script global scope  
DT = literal_eval(sys.argv[1])          # int or float
I_MAX = sys.argv[2]                     # string
STEPS = literal_eval(sys.argv[3])       # list
PORT = sys.argv[4]                      # string
PSTAT = None                            # Potentiostat object 


def write(s):
    sys.stdout.write(s+'\n')
    sys.stdout.flush()

def write_error(s):
    s = g.R_ERROR_PREFIX + str(s)
    write(s)

def write_status(s):
    s = g.R_STATUS_PREFIX + str(s)
    write(s)

def write_data(s):
    s = g.R_DATA_PREFIX + str(s)
    write(s)

def write_port(s):
    s = g.R_PORT_PREFIX + str(s)
    write(s)

def calc_v_max():
        v_max_method = 0                                        # Get the maximum abs() voltage of the entire method
        for step in STEPS:
            if step[g.M_TYPE] != g.M_RELAY:
                v_max_step = get_v_max_abs(step)
                if v_max_step > v_max_method:
                    v_max_method = v_max_step

        v_ranges = PSTAT.get_all_volt_range()              # Grab the v_max options from the device
        v_ranges_int = []
        for v_range in v_ranges:
            v_ranges_int.append(int(sub("[^0-9]", "",v_range))) # And convert them from strings to integers

        v_max_i = g.QT_NOTHING_SELECTED_INDEX
        for i,v in enumerate(v_ranges_int):                     # Taking advantage of fact that they are sorted low->high
            if v_max_method <= v:                               # Loop thru all of them. As soon as a v_max setting exceeds
                v_max_i = i                                     # the method's v_max, use that setting!
                break

        if v_max_i != g.QT_NOTHING_SELECTED_INDEX:              # if we have found a vmax, return it
            return v_ranges[v_max_i]
        else:                                                   # otherwise, the V is too high, return error!!!
            write_error(g.R_ERROR_VMAX_TOO_HIGH)
            return False

def connect_to_device(port):
    ###############################3
    #
    #   TODO
    #
    # 1. Rework this so we can confirm connection to the correct type of device.
    #       Currently, this fn just connects to the first device found whose
    #       name contains the string "USB Serial Device" which could be any
    #       number of devices =0
    
    global PSTAT
    global PORT
    
    try:
        PSTAT = Potentiostat(port)      # Check the connection by creating a new PSTAT object and 
        PSTAT.get_hardware_variant()    # running a command that would produce an error with a nonpotentiostat device
        PORT = port
        write_port(PORT)
        return True                     # if it doesn't throw and error, we're good to go with the current pstat!
    except:
        PSTAT = None                    # if it does throw an error, read on!
        return False

def device_is_connected():
    if PORT:                                # If we're supposed to be connected already
        if connect_to_device(PORT):         # If we're still connected, great! 
            return True
    for port in serial.tools.list_ports.comports(): # If not: try to connect: loop thru all serial ports with connections
        if 'USB Serial Device' in port.description: # if the device name contains "USB Serial Device"
            if connect_to_device(port.device):      # Try to connect to it, if so, great! 
                return True 
    write_error(g.R_ERROR_NO_CONNECT)               # If we don't connect at all, write the error message
    return False

def on_data(chan, t, volt, curr):
    write_data((t,volt,curr))

def set_relay(step):
    write_status('relay step here')

def run_const(step):
    v = step[g.M_CONST_V]
    t = int(step[g.M_T] * g.S2MS)
    params = {
        'quietValue' : v,
        'quietTime'  : 0,
        'value'      : v,
        'duration'   : t,
        }
    write_status('STARTING a constant voltage')
    PSTAT.run_test('constant', param=params, on_data=on_data, display=None)
    write_status('FINISHED a constant voltage')

def run_ramp(step):
    v0 = step[g.M_RAMP_V1]          # get starting voltage
    v1 = step[g.M_RAMP_V2]          # get ending voltage
    t = int(step[g.M_T] * g.S2MS)   # get duration as float in [s], convert to int in [ms]
    params = {
        'quietTime'  : 0,   # quiet period duration (ms)
        'quietValue' : v0,  # quiet period voltage (V)
        'startValue' : v0,  # linear sweep starting voltage (V)
        'finalValue' : v1,  # linear sweep final voltage (V)
        'duration'   : t,   # linear sweep duration (ms)
        }
    write_status('STARTING a ramp')
    PSTAT.run_test('linearSweep', param=params, on_data=on_data, display=None)
    write_status('FINISHED a ramp')
    
    
    

def init_run():
    dev = device_is_connected()
    if not dev:
        return
    write_status('device is connected!')
    PSTAT.set_sample_period(DT)
    PSTAT.set_curr_range(I_MAX)
    v_max = calc_v_max()
    if not v_max:
        return
    PSTAT.set_volt_range(v_max)
    PSTAT.set_auto_connect(True)
    
    write_status('sample period is: '+str(PSTAT.get_sample_period()))
    write_status('current range is: '+str(PSTAT.get_curr_range()))
    write_status('voltage range is: '+str(PSTAT.get_volt_range()))     
    write_status("now we're doing stuff!")

    for step in STEPS:
        step_type = step[g.M_TYPE]
        if step_type == g.M_RELAY:
            set_relay(step)
        elif step_type == g.M_CONSTANT:
            run_const(step)
        elif step_type == g.M_RAMP:
            run_ramp(step)
    
init_run()
