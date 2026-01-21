#process.py
#


import sys
from os import getcwd
from os.path import exists

sys.path.append(getcwd()) # current working directory must be appended to path for custom ("ov_") imports

from external.globals import ov_globals as g
from external.globals.ov_functions import (get_data_from_file,
                                           write_data_to_file,
                                           remove_data_from_layout,
                                           get_method_from_file_data,
                                           get_run_from_file_data,
                                           get_rep,
                                           get_v_max_abs)

from ast import literal_eval
from csv import DictWriter
from re import sub
import serial.tools.list_ports
from potentiostat import Potentiostat


#################################
#                               #
#   GENERAL WRITING FUNCTIONS   #
#                               #
#################################

def write_data(s):      # Write data to data channel 
    sys.stdout.write(str(s)+'\n')
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(str(s)+'\n')
    sys.stderr.flush()
    

#################################
#                               #
#       OVERWRITE               #
#                               #
#################################
#
def overwrite():
    path = sys.argv[2]                  # get path of file to write from
    data = literal_eval(sys.argv[3])    # get data dict
    write_data(str(path))
    write_data_to_file(path, data)


#################################
#                               #
#       EXPORT                  #
#                               #
#################################
#
def export():
    readpath = sys.argv[2]              # get path of file to read from
    writepath = sys.argv[3]             # get path of folder to write to
    tasks = literal_eval(sys.argv[4])   # cast sys.argv[4] from string to list of tuples
    data = get_data_from_file(readpath) # read file (returns dict)
    for task in tasks:
        try:
            run_id = task[0]
            rep_id = task[1]
            run = next(filter(lambda x: x[g.R_UID_SELF] == run_id, data[g.S_RUNS]), None)
            rep = next(filter(lambda x: x[g.R_UID_SELF] == rep_id, run[g.R_REPLICATES]), None)
            repData = rep[g.R_DATA]
            if repData:
                keys = list(repData[0].keys())
                
                samplename=readpath.split('/')[-1]              # get filename from path 
                groups = samplename.split('.')                  # begin removing the extension (split at all periods)
                samplename = '.'.join(groups[:len(groups)-1])   #   finish removing the extension (rejoin all with periods except for last)
                
                filename = samplename+'_'+run_id+'_'+rep_id     # add on the run and rep IDs
                path = writepath+'/'+filename                   # append filename to path
                suffix = ''
                i = 1
                
                while exists(path+suffix+'.csv'):               # while the file already exists
                    suffix = '_COPY'+str(i)                     # tack on a suffix
                    i = i+1                                     # and increment the counter until we find a filename that is not taken!
                path = path+suffix+'.csv'                       # generate that novel filename
                
                with open(path, 'w', encoding='UTF8', newline='') as f:
                    writer = DictWriter(f, fieldnames=keys) # Tell the writer we are writing from a dictionary with 'keys' as headers
                    writer.writeheader()                        # Write the header row
                    writer.writerows(repData)                   # Write  the data'''

                write_data(str(task))
            else:
                write_error(str(task))
        except Exception as e:          # If a specific export task generates an error
            write_error(str(e))
            write_error(str(task))


    
    




#################################
#                               #
#       SAVE                    #
#                               #
#################################
#
# This is the script that can be called to write asynchronously to the data file.
#   There are several types of saves supported. Arguments are passed through commande line sys.argv:
#
#       1. path     str.                path to find file for reading/writing
#       2. saveType str.                defines which type of save is requested 
#       3. params   list cast as str.    a string-cast list with parameters that depend on saveType
#
#   The different types of save are as follows:
#
#       - sample        params = [dict of sample params]                    Saves new sample parameters
#       - new run       params = [dict of run params]                       Saves a new run 
#       - delete rep    params = [(runID, repID),(runID,repID),...]         Deletes all listed reps. Also deletes runs and methods as needed
#       - rep no data   params = [(runID,repID), dict of rep params]        Modifies existing rep parameters but maintains raw data
#       - rep w data    params = [(runID,repID), dict of rep params]        Replaces existing rep parameters (including raw data)
#       - run modified  params = [runID, dict of run params]                Modifies existing run parameters but maintains replicates
#   
#   For each type of save, when the save completes, it sends a writes the data dictionary (not including raw data)
#   back as data. 

def save_update_sample(data, params):   # Takes the sample parameters
    newData = params[0]                 # passed in params[0]
    for key in g.S_EDITABLES:           # and overwrites the existing values
        data[key] = newData[key]        # with the passed values
    return data

def save_add_new_run(data, params):
    newRun = params[0]               
    data[g.S_RUNS].append(newRun)
    return data

def save_delete_rep(data, params):
    """ Args:
        params[0] -- list of tuples w format (runID, repID)

        Function:
        Deletes all of the replicates indicated in the argument list.
        Then checks whether there are any runs whose reps have all been deleted.
            if so, deletes them too.
        Then checks whether there are any methods which are no longer referenced
            by any runs in the sample file. If so, deletes these methods too.

        Returns: data"""
    tasks = params[0]

    #Delete the requested replicates
    while tasks:                                            
        task = tasks[0]
        run_id = task[0]
        rep_id = task[1]

        found = False
        index = False
        for run in data[g.S_RUNS]:                  # First, find the replicate 
            if run[g.R_UID_SELF] == run_id:
                for i, rep in enumerate(run[g.R_REPLICATES]):
                    if rep[g.R_UID_SELF] == rep_id:
                        found = True
                        index = i
                        break
                if found:
                    break

        if found:                                   # If it was found, remove it!
            run[g.R_REPLICATES].pop(index)
        tasks.pop(0)

    # Delete empty runs
    some_runs_empty = True
    while some_runs_empty:                          # Now that we've deleted all reps
        found = False                               # Check whether there are any runs where al;
        for i,run in enumerate(data[g.S_RUNS]):     #   reps have been deleted
            if not run[g.R_REPLICATES]:
                found = True
                break

        if found:                                   # Delete these empty runs as well!
            data[g.S_RUNS].pop(i)                           
        else:
            some_runs_empty = False

    # Delete unreferenced methods
    methods_to_keep = []                            # Get list of uids of methods to keep
    for run in data[g.S_RUNS]:
        if not run[g.R_UID_METHOD] in methods_to_keep:
            methods_to_keep.append(run[g.R_UID_METHOD])
            
    methods_floating = True                         
    while methods_floating:
        found = False                               # If there is a floating method
        for i,method in enumerate(data[g.S_METHODS]):
            if not method[g.M_UID_SELF] in methods_to_keep:
                found = True
                break
        if found:
            data[g.S_METHODS].pop(i)                # delete it!
        else:
            methods_floating = False
          
    return data

def save_modify_rep(data, params):
    run_id = params[0][0]
    rep_id = params[0][1]
    newRep = params[1]

    rep = get_rep(data, (run_id, rep_id))

    if rep:
        #prevData = rep[g.R_DATA]    # store the previous raw data
        keys = list(rep.keys())     # get a list of all keys in saved rep
        keys.remove(g.R_DATA)       #   except for the data key
        for key in keys:            # remove all keys and values from rep except data
            rep.pop(key, None)      
        for key in newRep:          # add new keys and values to rep (does not include raw data)
            rep[key] = newRep[key]
        #rep[g.R_DATA] = prevData    # add previous raw data back in
    return data

def save_modify_run(data, params):
    run_id = params[0]
    newRun = params[1]

    run = get_run_from_file_data(data, run_id)
    
    if run:
        prevReps = run[g.R_REPLICATES]  # store previous replicates (includes raw data)
        keys = list(run.keys())         # get a list of all keys in saved run
        for key in keys:                # remove all keys and values from run
            run.pop(key, None)      
        for key in newRun:              # add new keys and values to run (does not include replicates)
            run[key] = newRun[key]
        run[g.R_REPLICATES] = prevReps  # add the old replicates (with raw data) back in   
    
    return data

def save_method_to_sample(data, params):     # append method to sample file
    newMethod = params[0]               
    data[g.S_METHODS].append(newMethod)
    return data

def save_modify_method(data, params):        # modify the method in a sample file
    method_id = params[0]
    newMethod = params[1]
    
    method = get_method_from_file_data(data, method_id)

    if method:
        keys = list(method.keys())
        for key in keys:
            method.pop(key, None)
        for key in newMethod:
            method[key] = newMethod[key]
    return data

def save():    
    try:
        path = sys.argv[2]                  # get path of file to read from
        saveType = sys.argv[3]              # get save type
        params = literal_eval(sys.argv[4])  # cast sys.argv[4] from string to list
        data = get_data_from_file(path)     # read file from path (returns dict)

        if saveType == g.SAVE_TYPE_SAMPLE:
            data=save_update_sample(data, params)
        elif saveType == g.SAVE_TYPE_RUN_NEW:
            data=save_add_new_run(data, params)
        elif saveType == g.SAVE_TYPE_REP_DELETE:
            data=save_delete_rep(data, params)
        elif saveType == g.SAVE_TYPE_REP_MOD:
            data=save_modify_rep(data, params)
        elif saveType == g.SAVE_TYPE_RUN_MOD:
            data=save_modify_run(data, params)
        elif saveType == g.SAVE_TYPE_METHOD_TO_SAMPLE:
            data=save_method_to_sample(data, params)
        elif saveType == g.SAVE_TYPE_METHOD_MOD:
            data=save_modify_method(data, params)

        write_data_to_file(path, data)
        data = remove_data_from_layout(data) 
        write_data(str(data))               #   Write the data (with raw data stripped) to data channel



        
    except Exception as e:                  # If process generates an error:
        write_error(str(e))                 #   Write that error to error channel


#################################
#                               #
#       READ/DATA LOAD          #
#                               #
#################################
#
def read():
    path = sys.argv[2]                  #   Get path of file to read from
    data = get_data_from_file(path)     #   Read file from path (returns dict)
    for run in data[g.S_RUNS]:          #   For each run in data dict
        for rep in run[g.R_REPLICATES]: #   And for each rep of the run
            rep.pop(g.R_DATA, None)     #   Remove the raw data
    write_data(str(data))               #   Write the data (with raw data stripped) to data channel


#################################
#                               #
#       RUN                     #
#                               #
#################################
#
# This is the script that runs the method directly on the potentiostat
#
# Args:
#   - sys.argv[2] - dt             int or float    the pstat will report a datapoint every dt miliseconds
#   - sys.argv[3] - i_max          string          this string is specific to the device and sets the current range
#   - sys.argv[4] - steps          list of steps   a list of steps to send to the device (may include runs and relay setting)
#   - sys.argv[5] - port           string          name of port to try first to find device
#   - sys.argv[6] - relays_enabled boolean         T/f whether relays are enabled. If False, all relay toggle steps are ignored
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

def write_run_status(s):
    s = g.R_STATUS_PREFIX + str(s)
    write_data(s)

def write_run_data(s):
    s = g.R_DATA_PREFIX + str(s)
    write_data(s)

def write_run_port(s):
    s = g.R_PORT_PREFIX + str(s)
    write_data(s)

def write_run_relay_state(relay, state):
    s = g.R_RELAY_PREFIX+str(relay)+'-'+str(state)
    write_data(s)

def calc_v_max(pstat, steps):
        v_max_method = 0                                        # Get the maximum abs() voltage of the entire method
        for step in steps:
            if step[g.M_TYPE] != g.M_RELAY:
                v_max_step = get_v_max_abs(step)
                if v_max_step > v_max_method:
                    v_max_method = v_max_step

        v_ranges = pstat.get_all_volt_range()                   # Grab the v_max options from the device
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
    
    try:
        pstat = Potentiostat(port)      # Check the connection by creating a new PSTAT object and 
        pstat.get_hardware_variant()    # running a command that would produce an error with a nonpotentiostat device
        write_run_port(port)
        return (pstat, port)            # if it doesn't throw and error, we're good to go with the current pstat!
    except:
        PSTAT = None                    # if it does throw an error, read on!
        return None

def device_is_connected(port):
    if port:                                # If we're supposed to be connected already
        resp = connect_to_device(port)
        if resp:                            # If we're still connected, great! 
            return resp
    for port in serial.tools.list_ports.comports(): # If not: try to connect: loop thru all serial ports with connections
        if 'USB Serial Device' in port.description: # if the device name contains "USB Serial Device"
            resp = connect_to_device(port.device)
            if resp:                                # Try to connect to it, if so, great!
                return resp 
    raise ValueError(g.R_ERROR_NO_CONNECT)               # If we don't connect at all, write the error message

def on_data(chan, t, volt, curr):
    write_run_data((t,volt,curr))

def set_relay(pstat, step, relays_enabled):
    if relays_enabled:
        try:
            relay = step[g.M_RELAY]
            state = step[g.M_RELAY_STATE]
            ################################ MODIFY THIS FOR DEVICE SPECIFIC LOGIC
            #
            #
            if state:
                resp = pstat.set_dio_value('ExpDioPin3', 'High')
            else:
                resp = pstat.set_dio_value('ExpDioPin3', 'Low')
            #
            #
            #############################################################
            write_run_relay_state(relay, state)
        except:
            raise ValueError(g.R_ERROR_SET_RELAY)

def run_const(pstat, step):
    v = step[g.M_CONST_V]
    t = int(step[g.M_T] * g.S2MS)
    params = {
        'quietValue' : v,
        'quietTime'  : 0,
        'value'      : v,
        'duration'   : t,
        }
    write_run_status('STARTING a constant voltage')
    pstat.run_test('constant', param=params, on_data=on_data, display=None)
    write_run_status('FINISHED a constant voltage')

def run_ramp(pstat, step):
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
    write_run_status('STARTING a ramp')
    pstat.run_test('linearSweep', param=params, on_data=on_data, display=None)
    write_run_status('FINISHED a ramp')
    
    
    

def run():
    # Grab arguments and convert them from strings to intended types, store in script global scope  
    DT = literal_eval(sys.argv[2])              # int or float
    I_MAX = sys.argv[3]                         # string
    STEPS = literal_eval(sys.argv[4])           # list
    PORT = sys.argv[5]                          # string
    RELAYS_ENABLED = literal_eval(sys.argv[6])  # bool
    PSTAT = None                                # Potentiostat object 

    resp = device_is_connected(PORT)            # try to connect to device
    if not resp:
        return
    
    write_run_status('device is connected!')
    (PSTAT, PORT) = resp
    PSTAT.set_sample_period(DT)                 # set sample parameters to device
    PSTAT.set_curr_range(I_MAX)
    v_max = calc_v_max(PSTAT, STEPS)
    if not v_max:
        return
    PSTAT.set_volt_range(v_max)
    PSTAT.set_auto_connect(True)

    ############## MODIFY THIS TO ACCOUNT FOR DIFFERENCES IN RELAY PINS FOR DIFFERNT DEVICES #######3
    #
    #
    relays= ['ExpDioPin3', 'ExpDioPin4', 'ExpDioPin5', 'ExpDioPin6', 'ExpDioPin7', 'ExpDioPin8', 'ExpDioPin9', 'ExpDioPin10']
    for relay in relays:
        PSTAT.set_dio_pin_mode(relay, 'Output')
        PSTAT.set_dio_value(relay, 'Low')
    #
    #
    ######################################
        
    write_run_status('sample period is: '+str(PSTAT.get_sample_period()))
    write_run_status('current range is: '+str(PSTAT.get_curr_range()))
    write_run_status('voltage range is: '+str(PSTAT.get_volt_range()))     
    write_run_status("now we're doing stuff!")

    for step in STEPS:
        step_type = step[g.M_TYPE]
        if step_type == g.M_RELAY:
            set_relay(PSTAT, step, RELAYS_ENABLED)
        elif step_type == g.M_CONSTANT:
            run_const(PSTAT, step)
        elif step_type == g.M_RAMP:
            run_ramp(PSTAT, step)

    #### MODIFY THIS TO ACCOUNT FOR DIFFERENT DEVICES WITH DIFFERENT IO PINS
    #
    #
    # Turn off all relays at end of run
    for relay in relays:
        PSTAT.set_dio_value(relay, 'Low')
    #
    #
    #####################################################


    

#################################
#                               #
#       MAIN LOOP               #
#                               #
#################################

try:
    processType = sys.argv[1]
    if processType == g.PROC_TYPE_SAVE:
        save()
    elif processType == g.PROC_TYPE_OVERWRITE:
        overwrite()
    elif processType == g.PROC_TYPE_EXPORT:
        export()
    elif processType == g.PROC_TYPE_READ:
        read()
    elif processType == g.PROC_TYPE_RUN:
        run()
        

except Exception as e:                  # If process in general generates an error (eg. with args or file read):
    write_error(str(e))                 #   Write that error to error channel

        
