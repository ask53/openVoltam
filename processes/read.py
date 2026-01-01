#read.py
#
# This is the script that reads a data file asynchronously
#   then strips the raw data (which occupies most of the file
#   to return just the layout structure

import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path for custom ("ov_") imports

import ov_globals as g
from ov_functions import get_data_from_file

def write_data(s):      # Write data to data channel 
    sys.stdout.write(s)
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(s)
    sys.stderr.flush()
    
try:
    path = sys.argv[1]                  #   Get path of file to read from
    data = get_data_from_file(path)     #   Read file from path (returns dict)
    for run in data[g.S_RUNS]:          #   For each run in data dict
        for rep in run[g.R_REPLICATES]: #   And for each rep of the run
            rep.pop(g.R_DATA, None)     #   Remove the raw data
    write_data(str(data))               #   Write the data (with raw data stripped) to data channel
except Exception as e:                  # If process generates an error:
    write_error(str(e))                 #   Write that error to error channel
