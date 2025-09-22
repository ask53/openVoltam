#globals.py

# Keys for sample dictionary
S_NAME = "sample_name"
S_DATE_ENTERED = "date_first_saved"
S_DATE_COLLECTED = "date_collected"
S_LOC_COLLECTED = "location_collected"
S_COLLECTED_BY = "collected_by"
S_CONTACT = "contact_info"
S_ENTERED_BY = "entered_by"
S_COMMENTS = "sample_comments"
S_SWEEPS = "sweeps"
S_RAW = "raw_data"
S_PROCESSED = "processed_data"

# Language globals 
ENG = 0
ESP = 1
L = ENG  # default lang, changed by program

HEADER_DIVIDER = ' | '

DATE_FORMAT = 'dd-MMM-yyyy'
SAMPLE_NAME_MIN_LENGTH = 3

CANCEL_BUTTON = 'cancel_button_id'

#File system navigation
DEFAULT_EXT = '.json'
FILE_TYPES = '*'+DEFAULT_EXT

