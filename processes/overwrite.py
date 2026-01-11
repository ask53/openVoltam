#overwrite.py
#
#Is designed to be called as an asynchronous process
#Is passed two cmd line parameters:
#   -sys.argv[1] String.                path to where data should be saved
#   -sys.argv[2] Dict cast as String.   Stringified dictionary of data to write
#This script converts the arg[2] back into a dictionary, then writes
#it to the path.

import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path for custom ("ov_") imports

from external.globals.ov_functions import write_data_to_file
from ast import literal_eval

def write_data(s):      # Write data to data channel 
    sys.stdout.write(s)
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(s)
    sys.stderr.flush()

 
try:
    path = sys.argv[1]                  # get path of file to write  from
    data = literal_eval(sys.argv[2])    # get data dict
    write_data_to_file(path, data)
    
except Exception as e:                  # If process generates an error:
    write_error(str(e))                 #   Write that error to error channel
