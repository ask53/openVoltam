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

from external.globals import ov_globals as g
from external.globals.ov_functions import (get_data_from_file,
                          write_data_to_file,
                          remove_data_from_layout,
                          get_method_from_file_data,
                          get_run_from_file_data,
                          get_rep)

from ast import literal_eval

def write_data(s):      # Write data to data channel 
    sys.stdout.write(s)
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(s)
    sys.stderr.flush()

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

def modify_rep(data, params):
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

def modify_run(data, params):
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

def method_to_sample(data, params):     # append method to sample file
    newMethod = params[0]               
    data[g.S_METHODS].append(newMethod)
    return data

def modify_method(data, params):        # modify the method in a sample file
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
    elif saveType == g.SAVE_TYPE_RUN_MOD:
        data=modify_run(data, params)
    elif saveType == g.SAVE_TYPE_METHOD_TO_SAMPLE:
        data=method_to_sample(data, params)
    elif saveType == g.SAVE_TYPE_METHOD_MOD:
        data=modify_method(data, params)

    write_data_to_file(path, data)
    data = remove_data_from_layout(data) 
    write_data(str(data))               #   Write the data (with raw data stripped) to data channel



    
except Exception as e:                  # If process generates an error:
    write_error(str(e))                 #   Write that error to error channel
