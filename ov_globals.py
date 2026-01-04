#ov_globals.py

CURRENT_RANGES = ['1uA', '10uA', '100uA', '1000uA', '10000uA']

# PyQt globals
QT_NOTHING_SELECTED_INDEX = -1

# Status bar
SB_DURATION = 6000  # duration of status bar messages in [ms]
SB_DURATION_ERROR = 10000  # duration of status bar messages in [ms]
SB_PROGRESS_BAR_WIDTH = 200

# Window modes
WIN_MODE_NEW = 'new'
WIN_MODE_VIEW_ONLY = 'view'
WIN_MODE_EDIT = 'edit'
WIN_MODE_VIEW_WITH_MINOR_EDITS = 'view-with-edits'

# Keys for sample (S) dictionary
S_NAME = "sample_name"
S_DATE_ENTERED = "date_first_saved"
S_DATE_COLLECTED = "date_sample_collected"
S_LOC_COLLECTED = "location_collected"
S_CONTACT = "contact_info"
S_COLLECTED_BY = "collected_by"
S_NOTES = "sample_comments"
S_METHODS = "methods"
S_RUNS = "runs"
S_PROCESSED = "processed_data"

S_EDITABLES = [S_NAME, S_DATE_COLLECTED, S_LOC_COLLECTED, S_CONTACT, S_COLLECTED_BY, S_NOTES]
S_BLANK_ARRAYS = [S_METHODS, S_RUNS, S_PROCESSED]

# Keys for method (M) dictionary
M_UID_SELF = 'uid'
M_UID_PREFIX = 'method-'
M_NAME = 'name'
M_DT = 'dt'
M_CURRENT_RANGE = 'current-range'
M_STEPS = 'steps'
M_STEP_NAME = 'name'
M_DATA_COLLECT = 'data-collect'
M_STIR = 'stir'
M_VIBRATE = 'vibrate'
M_TYPE = 'type'
M_CONSTANT = 'constant'
M_RAMP = 'ramp'
M_TYPES = [M_CONSTANT, M_RAMP]   # This dicates the order they appear in the menu          
M_T = 'duration'
M_CONST_V = 'V'
M_RAMP_V1 = 'V1'
M_RAMP_V2 = 'V2'
M_SCAN_RATE = 'scan-rate'
M_RELAY = 'relay'
M_RELAY_STATE = 'relay-state'
M_RELAYS = [M_STIR, M_VIBRATE]


# Keys for run (R) dictionary
R_UID_SELF = 'uid'
R_UID_METHOD = 'method'
R_DEVICE = 'device'
R_TYPE = 'run_type'
R_NOTES = 'notes'
R_REPLICATES = 'replicates'
R_TYPE_BLANK = "blank"
R_TYPE_SAMPLE = "sample"
R_TYPE_STDADD = "standard_addition"
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
R_TYPES = [R_TYPE_BLANK, R_TYPE_SAMPLE, R_TYPE_STDADD]

# Run window
R_PLOT_REFRESH_TIME = 0.1   # refreshes graph every x seconds
R_POST_RUN_WAIT_TIME = 0.5  # time after run to wait for last data [s]
R_ERROR_PREFIX = 'ERR'
R_STATUS_PREFIX = 'STA'
R_DATA_PREFIX = 'DAT'
R_PORT_PREFIX = 'POR'
R_ERROR_NO_CONNECT = '0'
R_ERROR_VMAX_TOO_HIGH = '1'
R_FINISHED_MSG = 'FIN'
R_DATA_TIME = 'time_s'
R_DATA_VOLT = 'voltage_V'
R_DATA_CURR = 'current_mA'

# Icon URLs 
ICON_PLUS = 'external/icons/add.png'
ICON_UP = 'external/icons/up.png'
ICON_DOWN = 'external/icons/down.png'
ICON_EDIT = 'external/icons/edit.png'
ICON_DUP = 'external/icons/duplicate.png'
ICON_TRASH = 'external/icons/trash.png'
ICON_X = 'external/icons/x.png'
ICON_STIR = 'external/icons/stirer.png'
ICON_VIB = 'external/icons/vibrator.png'
ICON_MEASURE = 'external/icons/measure.png'
ICON_REFRESH = 'external/icons/refresh.png'

# Asynchronous save
SAVE_TYPE_SAMPLE = 'sample'
SAVE_TYPE_RUN_NEW = 'new-run'
SAVE_TYPE_REP_DELETE = 'rep-del'
SAVE_TYPE_REP_MOD = 'rep-no-data'
SAVE_TYPE_REP_MOD_WITH_DATA = 'rep-w-data'
SAVE_TYPE_RUN_MOD = 'run-mod'
SAVE_TYPE_METHOD_TO_SAMPLE = 'method-to-sample'
SAVE_TYPE_METHOD_MOD = 'method-mod'

# Input 
RC_REPS_MIN = 1
RC_REPS_MAX = 99
M_V_MIN = -99.99
M_T_MAX = 9999
M_SCAN_RATE_MAX = 99.99
M_DT_MIN = 1
M_DT_MAX = 86399999         # 86,400,000 miliseconds in a day

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
METHOD_EXT = '.ovm'
SAMPLE_FILE_TYPES = '*'+SAMPLE_EXT
METHOD_FILE_TYPES = '*'+METHOD_EXT

# Unit conversions
MM2IN = 1. / 25.4   # milimeters to inches
S2MS = 1000         # seconds to miliseconds

# Globals changed by program
L = ENG  				# default lang, changed by program
BASEDIR = ''			# stores base directory for application executable file
HOME = False			# will hold the object of the homescreen at any given time
STYLES = False                  # will hold all the QSS for updating
APP = False                     # will hold the app object
