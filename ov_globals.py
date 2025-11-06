#ov_globals.py

# PyQt globals
QT_NOTHING_SELECTED_INDEX = -1

# Keys for sample dictionary
S_NAME = "sample_name"
S_DATE_ENTERED = "date_first_saved"
S_DATE_COLLECTED = "date_sample_collected"
S_LOC_COLLECTED = "location_collected"
S_CONTACT = "contact_info"
S_COLLECTED_BY = "collected_by"
S_NOTES = "sample_comments"
S_SWEEP_PROFILES = "sweep_profiles"
S_RUNS = "runs"
S_PROCESSED = "processed_data"

S_BLANK_ARRAYS = [S_SWEEP_PROFILES, S_RUNS, S_PROCESSED]

# Keys for sweep profile dictionary
SP_UID_SELF = 'uid'
SP_NOTES = 'notes'          ##### THIS IS JUST A PLACEHOLDER, WE WONT HAVE A NOTES FEATURE HERE
SP_UID_PREFIX = 'sp-'
SP_NAME = 'name'
SP_STIR = 'stir'
SP_VIBRATE = 'vibrate'
SP_TYPE = 'type'
SP_CONSTANT = 'constant'
SP_RAMP = 'ramp'
SP_TYPES = [SP_CONSTANT, SP_RAMP]   # This dicates the order they appear in the menu          
SP_T = 'duration'
SP_START_COLLECT = 'collection-start'
SP_END_COLLECT = 'collection-stop'
SP_START_COLLECT_T = 'collection-start-time'
SP_END_COLLECT_T = 'collection-stop-time'
SP_CONST_V = 'V'
SP_RAMP_V1 = 'V1'
SP_RAMP_V2 = 'V2'


# Keys for run dictionary
R_UID_SELF = 'uid'
R_UID_SP = 'sweep_profile'
R_TYPE = 'run_type'
R_NOTES = 'notes'
R_REPLICATES = 'replicates'
R_RUN_TYPE_BLANK = "blank"
R_RUN_TYPE_SAMPLE = "sample"
R_RUN_TYPE_STDADD = "standard_addition"
R_SAMPLE_VOL = "sample_vol_mL"
R_TOTAL_VOL = "total_vol_mL"
R_STD_ADDED_VOL = "standard_vol_mL"
R_STD_CONC = "standard_conc_ppb"
R_TIMESTAMP = "created"
R_STATUS = 'status'
R_DATA = 'data'
R_STATUS_PENDING = "pending"
R_STATUS_ERROR = "run_error"
R_STATUS_RAN = "run_success"
R_STATUS_ANALYZED = "analyzed"
R_RUN_UID_PREFIX = "run-"
R_REPLICATE_UID_PREFIX = "rep-"
#
#
#
##### ADD MORE RUN PARAMS HERE

ICON_PLUS = 'external/icons/add.png'
ICON_UP = 'external/icons/up.png'
ICON_DOWN = 'external/icons/down.png'
ICON_EDIT = 'external/icons/edit.png'
ICON_DUP = 'external/icons/duplicate.png'
ICON_TRASH = 'external/icons/trash.png'
ICON_X = 'external/icons/x.png'

RC_REPS_MIN = 1
RC_REPS_MAX = 99
SP_V_MIN = -99.99
SP_T_MAX = 9999

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
STEP_EVEN_ROW_NAME = 'step-cell-even'
STEP_ODD_ROW_NAME = 'step-cell-odd'

# Realtime styling
PADDING = 4

#File system navigation
SAMPLE_EXT = '.ovs'
CONFIG_EXT = '.ovc'
SAMPLE_FILE_TYPES = '*'+SAMPLE_EXT
CONFIG_FILE_TYPES = '*'+SAMPLE_EXT

# Globals changed by program
L = ENG  				# default lang, changed by program
BASEDIR = ''			# stores base directory for application executable file
HOME = False			# will hold the object of the homescreen at any given time
STYLES = False                  # will hold all the QSS for updating
APP = False                     # will hold the app object
