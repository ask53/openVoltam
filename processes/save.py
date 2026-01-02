#save.py
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

import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path for custom ("ov_") imports

import ov_globals as g
from ov_functions import get_data_from_file, write_data_to_file, remove_data_from_layout

from ast import literal_eval

def write_data(s):      # Write data to data channel 
    sys.stdout.write(s)
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(s)
    sys.stderr.flush()


def write_progress(pct):
    write_data(str(pct)+'\n')


def update_sample(data, params):    # Takes the sample parameters
    newData = params[0]             # passed in params[0]
    for key in g.S_EDITABLES:       # and overwrites the existing values
        data[key] = newData[key]    # with the passed values
    return data

def add_new_run(data, params):
    newRun = params[0]               
    data[g.S_RUNS].append(newRun)
    return data

def delete_rep(data, params):
    return

def modify_rep(data, params):
    run_id = params[0][0]
    rep_id = params[0][1]
    newRep = params[1]
    found = False
    for run in data[g.S_RUNS]:
        if run[g.R_UID_SELF] == run_id:
            for rep in run[g.R_REPLICATES]:
                if rep[g.R_UID_SELF] == rep_id:
                    found = True
                    break
            if found:
                break
    prevData = rep[g.R_DATA]    # store the previous raw data
    keys = list(rep.keys())     # get a list of all keys in saved rep
    for key in keys:            # removal all keys and values from rep
        rep.pop(key, None)      
    for key in newRep:          # add new keys and values to rep (does not include raw data)
        rep[key] = newRep[key]
    rep[g.R_DATA] = prevData    # add previous raw data back in
    return data

def replace_rep(data, params):
    return

def modify_run(data, params):
    return

def method_to_sample(data, params):     # append method to sample file
    newMethod = params[0]               
    data[g.S_METHODS].append(newMethod)
    return data
    
try:
    path = sys.argv[1]                  # get path of file to read from
    saveType = sys.argv[2]              # get save type
    params = literal_eval(sys.argv[3])  # cast sys.argv[3] from string to list
    data = get_data_from_file(path)     # read file from path (returns dict)
    if saveType == g.SAVE_TYPE_SAMPLE:
        data=update_sample(data, params)
    elif saveType == g.SAVE_TYPE_RUN_NEW:
        data=add_new_run(data, params)
    elif saveType == g.SAVE_TYPE_REP_DELETE:
        data=delete_rep(data, params)
    elif saveType == g.SAVE_TYPE_REP_MOD:
        data=modify_rep(data, params)
    elif saveType == g.SAVE_TYPE_REP_MOD_WITH_DATA:
        data=replace_rep(data, params)
    elif saveType == g.SAVE_TYPE_RUN_MOD:
        data=modify_run(data, params)
    elif saveType == g.SAVE_TYPE_METHOD_TO_SAMPLE:
        data=method_to_sample(data, params)

    write_data_to_file(path, data)
    data = remove_data_from_layout(data) 
    write_data(str(data))               #   Write the data (with raw data stripped) to data channel



    
except Exception as e:                  # If process generates an error:
    write_error(str(e))                 #   Write that error to error channel
