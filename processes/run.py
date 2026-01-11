#run.py
#
# This is the script that runs the method directly on the potentiostat
#
# Args:
#   - sys.argv[1] - dt             int or float    the pstat will report a datapoint every dt miliseconds
#   - sys.argv[2] - i_max          string          this string is specific to the device and sets the current range
#   - sys.argv[3] - steps          list of steps   a list of steps to send to the device (may include runs and relay setting)
#   - sys.argv[4] - port           string          name of port to try first to find device
#   - sys.argv[5] - relays_enabled boolean         T/f whether relays are enabled. If False, all relay toggle steps are ignored
#
# Communication:
#   As a script that is designed to be called asynchrounously, it is designed to communicate
#       back with the program that called it. It does so through by using the sys.stdout()
#       and sys.stderr() streams.
#
#   Regular communication is passed through sys.stdout() and
#       messages are given a prefix to indicate which type of communication is being shared
#       The types of messages shared on sys.stdout() are:
#           - Status messages: These are primarily used for debugging
#           - Port: indicates which port holds the pstat
#           - Relay stat: indicates the state of a specific relay which has just been set
#           - Data: this is the data from the pstat!
#
#   Error messages (that shut down run.py) are passed through the sys.stderr() channel. This
#       is accomplished by raising a ValueError() with a custom error message that the
#       calling program can receive, interpret, and act on.
#
# How the run works:
#   This script is designed to be run by another script as an asynchronous process.
#   It takes in system command line arguments through sys.argv.
#   It first tries to find a potentiostat at port.
#   If it cannot, it looks thru all other available ports and uses the first potentiostat
#       that it encounters.
#   Once a pstat has been connected with, various parameters are set (eg. dt, i_max, v_max
#       [v_max is calculated from steps], etc.) on the device.
#   Then the script loops thru steps. For each step, the step is run on the potentiostat.
#       the pstat returns data every dt miliseconds. This data is immediately returned
#       to the calling program through sys.stdout(). This script just passes the data
#       along and assumes that the calling program will handle it.
#   When the steps have all been run, this program finishes.
#
# Limitations:
#   1. At this time, this script can only run the following types of steps:
#       - Set relay on/off
#       - Hold a constant voltage for a time
#       - Run a ramp from v1 to v2 over a time
#      Other types of steps are supported by the potentiostat but would need to be added here
#
#   2. Relay activation does not yet work.
#       Need to implement the script for actually changing the relay state!
#       (see placeholder in the code below.) Right now, relays aren't actually set.
#       this also requires a firmware update of the Rodeostat...


import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path

from ast import literal_eval
import time
import serial.tools.list_ports

from potentiostat import Potentiostat

from external.globals import ov_globals as g
from external.globals.ov_functions import *

# Grab arguments and convert them from strings to intended types, store in script global scope  
DT = literal_eval(sys.argv[1])              # int or float
I_MAX = sys.argv[2]                         # string
STEPS = literal_eval(sys.argv[3])           # list
PORT = sys.argv[4]                          # string
RELAYS_ENABLED = literal_eval(sys.argv[5])  # bool
PSTAT = None                                # Potentiostat object 


def write(s):
    sys.stdout.write(s+'\n')
    sys.stdout.flush()

def write_status(s):
    s = g.R_STATUS_PREFIX + str(s)
    write(s)

def write_data(s):
    s = g.R_DATA_PREFIX + str(s)
    write(s)

def write_port(s):
    s = g.R_PORT_PREFIX + str(s)
    write(s)

def write_relay_state(relay, state):
    s = g.R_RELAY_PREFIX+str(relay)+'-'+str(state)
    write(s)

def calc_v_max():
        v_max_method = 0                                        # Get the maximum abs() voltage of the entire method
        for step in STEPS:
            if step[g.M_TYPE] != g.M_RELAY:
                v_max_step = get_v_max_abs(step)
                if v_max_step > v_max_method:
                    v_max_method = v_max_step

        v_ranges = PSTAT.get_all_volt_range()                   # Grab the v_max options from the device
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
            raise ValueError(g.R_ERROR_VMAX_TOO_HIGH)

def connect_to_device(port):
    
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
    raise ValueError(g.R_ERROR_NO_CONNECT)               # If we don't connect at all, write the error message

def on_data(chan, t, volt, curr):
    write_data((t,volt,curr))

def set_relay(step):
    if RELAYS_ENABLED:
        try:
            relay = step[g.M_RELAY]
            state = step[g.M_RELAY_STATE]
            ####################################################################################################
            #
            #
            #
            set_relay_state(relay, state)       # THIS DOESN'T DO ANYTING YET (other than generate an error lol).....
            #
            #
            #
            #######################################
            write_relay_state(relay, state)
        except:
            raise ValueError(g.R_ERROR_SET_RELAY)

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
