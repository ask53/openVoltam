#export.py
#
#

import sys
import os
sys.path.append(os.getcwd()) # current working directory must be appended to path for custom ("ov_") imports

from external.globals import ov_globals as g
from external.globals.ov_functions import get_data_from_file

from ast import literal_eval
import csv

def write_data(s):      # Write data to data channel 
    sys.stdout.write(s+'\n')
    sys.stdout.flush()

def write_error(s):     # Write error to error channel
    sys.stderr.write(s+'\n')
    sys.stderr.flush()
    
try:
    readpath = sys.argv[1]              # get path of file to read from
    writepath = sys.argv[2]             # get path of folder to write to
    tasks = literal_eval(sys.argv[3])   # cast sys.argv[3] from string to list of tuples
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
                
                while os.path.exists(path+suffix+'.csv'):       # while the file already exists
                    suffix = '_COPY'+str(i)                     # tack on a suffix
                    i = i+1                                     # and increment the counter until we find a filename that is not taken!
                path = path+suffix+'.csv'                       # generate that novel filename
                
                with open(path, 'w', encoding='UTF8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=keys) # Tell the writer we are writing from a dictionary with 'keys' as headers
                    writer.writeheader()                        # Write the header row
                    writer.writerows(repData)                   # Write  the data'''

                write_data(str(task))
            else:
                write_error(str(task))
        except Exception as e:          # If a specific export task generates an error
            write_error(str(e))
            write_error(str(task))
except Exception as e:                  # If process in general generates an error (eg. with args or file read):
    write_error(str(e))                 #   Write that error to error channel
