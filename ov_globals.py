#ov_globals.py

# Keys for sample dictionary
S_NAME = "sample_name"
S_DATE_ENTERED = "date_first_saved"
S_DATE_COLLECTED = "date_sample_collected"
S_LOC_COLLECTED = "location_collected"
S_CONTACT = "contact_info"
S_COLLECTED_BY = "collected_by"
S_NOTES = "sample_comments"
S_CONFIGS = "sweep_configs"
S_RUNS = "runs"
S_RAW = "raw_data"
S_PROCESSED = "processed_data"

S_BLANK_ARRAYS = [S_CONFIGS, S_RUNS, S_RAW, S_PROCESSED]

# Keys for run dictionary
R_UID_SELF = 'uid'
R_UID_SP = 'sweep_profile'
R_NAME = 'run_name'
R_TYPE = 'run_type'
R_NOTES = 'notes'
#
#
#
##### ADD MORE RUN PARAMS HERE 

# Language globals 
ENG = 0
ESP = 1

HEADER_DIVIDER = ' | '
CUSTOM_NAME_FLAG = 'ov_'

DATE_DISPLAY_FORMAT = 'dd-MMM-yyyy'
DATE_STORAGE_FORMAT = 'yyyy-MM-dd'
DATETIME_STORAGE_FORMAT = DATE_STORAGE_FORMAT+' hh:mmap'
SAMPLE_NAME_MIN_LENGTH = 3

# Widget name mgmt (for targeting with QSS)
RUNS_EVEN_ROW_NAME = 'run-cell-even'
RUNS_ODD_ROW_NAME = 'run-cell-odd'
RUNS_ROW_SELECTED_SUFFIX = '-selected'
RUNS_BUT_ONE_NAME = 'run-but-single'
RUNS_BUT_ANY_NAME = 'run-but-any'

#File system navigation
DEFAULT_EXT = '.json'
FILE_TYPES = '*'+DEFAULT_EXT

# Globals changed by program
L = ENG  				# default lang, changed by program
BASEDIR = ''			# stores base directory for application executable file
HOME = False			# will hold the object of the homescreen at any given time
STYLES = False                  # will hold all the QSS for updating
APP = False                     # will hold the app object
