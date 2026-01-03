# ov_functions.py
#		

from tabularjson import parse, stringify, StringifyOptions, is_homogeneous
from re import sub
from tkinter.filedialog import askopenfilename, askdirectory

from json import dumps


import ov_globals as g
import ov_lang as l

from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QFrame
)

def encodeCustomName(custom_name):
    return g.CUSTOM_NAME_FLAG+custom_name

def isCustomName(s):
    return s.startswith(g.CUSTOM_NAME_FLAG)

def decodeCustomName(encoded_name):
    return encoded_name.replace(g.CUSTOM_NAME_FLAG, '', 1)

def custText(arr):
    return arr[g.L]

def horizontalize(widgetlist, stretch=False):
    """
    takes in a list of widgets and adds them all sequentially to a horizontal layout. Returns the layout
    """
    layout = QHBoxLayout()
    for widget in widgetlist:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch()
    return layout

def makeLabelsSelectable(w):
    els = w.findChildren(QLabel)
    for el in els:
        el.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
    return w

def setWsEnabled(ws, enabled=True):
    for w in ws:
        w.setEnabled(enabled)

def applyStyles():
    g.APP.setStyleSheet(g.STYLES)

def show_alert(obj, title, msg):
    dlg = QMessageBox(obj)
    dlg.setWindowTitle(title)
    dlg.setText(msg)
    dlg.exec()

def guess_filename(name):
    """Takes in a name and returns a best guess at the filename
    by stripping all characters other than letters, numbers,
    em-dashes, and underscores and by replacing all blankspace
    with dashes"""
    guess = sub('[^A-Za-z0-9 ]', '', name)  # remove all characters other than a-z, numbers, and spaces
    guess = ' '.join(guess.split())         # convert all sequential blankspace to a single space
    guess = guess.replace(' ', '-')         # replace all spaces with em-dashes
    return guess

def get_path_from_user(pathtype):
    try:
        path = ''
        if pathtype=='sample':
            path = askopenfilename(filetypes = [(l.filetype_sample_lbl[g.L], g.SAMPLE_FILE_TYPES)])
        elif pathtype=='method':
            path = askopenfilename(filetypes = [(l.filetype_sp_lbl[g.L], g.METHOD_FILE_TYPES)])
        elif pathtype=='folder':
            path = askdirectory()
            
        return path
    except Exception as e:
        print(e)
        
    

def get_data_from_file(path):
    try:
        with open(path, 'r') as file:
            content = file.read()
            data = parse(content)
        return data
    except Exception as e:
        print(e)
        return False

def write_data_to_file(path, data):
    try:
        with open(path, 'w') as file:                            
            
            options: StringifyOptions = {
                "indentation": 4,
                "trailingCommas": False,
                "output_as_table": is_homogeneous
                }
            tab_json_to_write = stringify(data, options)       #   convert dictionary to json string
            file.write(tab_json_to_write)                                       #   write json string to file
            #json_to_write = dumps(data, indent=4)
            #file.write(json_to_write)
            file.close()                                                    #   close the file (to avoid taking up too much memory)
        return True
    except Exception as e:
        print(e)
        return False

def remove_data_from_layout(d):
    for run in d[g.S_RUNS]:          #   For each run in data dict
        for rep in run[g.R_REPLICATES]: #   And for each rep of the run
            rep.pop(g.R_DATA, None)     #   Remove the raw data
    return d

def get_next_id(ids, prefix):
        """ Takes in a list of ids, loops through them to find the
        most recent one. Returns the id of the next one, which should be
        one greater than the current. Assumes IDs are of the format:
             [PREFIX]-n
        For example, if the [PREFIX] was 'fulano' the first few would be:
        fulano-1, fulano-2, fulano-3, etc.
        """
        max_id = -1
        for ID in ids:
            num = int(ID.replace(prefix,''))
            if num > max_id:
                max_id = num
        return prefix+str(max_id+1)

def get_ids(data, key):
    '''assumes that data is a dictionary with many key value pairs. Assumes
    that key is a key whose value is a list. Returns the unique IDs of
    every object in the list.'''
    ids = []
    for obj in data[key]:
        ids.append(obj[g.R_UID_SELF])
    return ids
    

def methods_match(m1, m2):
    ''' Takes in two method dicts, m1 and m2
    checks whether they match. If so, returns True,
    if not, returns False'''
    
    keys_to_ignore = [g.M_UID_SELF]   # List all keys to ignore
    for key in m1:                      # Loop thru all keys in m1
        if key not in keys_to_ignore:   # If key is not on ignore list
            if key not in m2:           # if the key from m1 is not in m2
                return False            #   We don't have a match...
            elif m1[key] != m2[key]:    # if the key exists but the values don't match
                return False            #   Still no match...
    return True                         # If we get all the way thru, its a match! 

def get_row_ws(w_parent, i):
    """Accepts:
    - w_parent: a widget that contains a grid layout
    - i: the row, indexed from 0, of interest
    Loops through the w_parent and returns a list of all
    child widgets in row i.
    """
    try:
        row_ws = []
        ws = w_parent.findChildren(QLabel)
        for w in ws:
            if w.property('row') == i:
                row_ws.append(w)
        return row_ws
    except Exception as e:
        print(e)

#### IS THIS NECESSARY??? #####################################################
#
#
#
def scroll_area_resized(outer, inner, event):
    print('---')
    print('HERE!')
    QScrollArea.resizeEvent(outer, event)   # Because this fn intercepts the resizeEvent, call the actual resizeEvent
                                            # (this checks whether to add/remove scroll bars, etc.
                                            # Then adjust the inner widget to fit well within the scroll area:
    outer_width = outer.width()             #   get width of the scroll area
    v_bar_width = 0 
    v_bar = outer.verticalScrollBar()       #   get the vertical scrollbar widget
    if v_bar.isVisible():                   #   if its visible
        v_bar_width = v_bar.width()         #   account for its width
    inner.setFixedWidth(outer_width-g.PADDING-v_bar_width)
    print(outer_width)
    print(inner.width())
#
#
###########################################################3

def get_run_from_file_data(data, run_id):
    
    """ takes in a full dataset dictionary, data, and the uid of the run
    we are seeking, run_id. Loops through all run elements in the data
    looking for one with a matching uid. If found, returns the dictionary
    of that run. Otherwise, returns False."""
    
    for run in data[g.S_RUNS]:          
        if run[g.R_UID_SELF] == run_id: 
            return run
    return False
    

def get_method_from_file_data(data, method_id):

    """ takes in a full dataset dictionary, data, and the uid of the method
    we are seeking, method_id. Loops through all method elements in the data
    looking for one with a matching uid. If found, returns the dictionary
    of that method. Otherwise, returns False."""
    
    for method in data[g.S_METHODS]:
        if method[g.M_UID_SELF] == method_id:
            return method
    return False

def get_v_max_abs(step):

    """ takes in a step of the method, and returns the maximum amplitude
    of volutage (always positive) during that step. """

    if step[g.M_TYPE] == g.M_CONSTANT:
        return abs(step[g.M_CONST_V])

    elif step[g.M_TYPE] == g.M_RAMP:
        v0 = abs(step[g.M_RAMP_V1])
        v1 = abs(step[g.M_RAMP_V2])
        return max(v0, v1)

def get_method_duration(steps):
    t = 0
    for step in steps:
        t = t + step[g.M_T]
    return t
        
def get_method_v_extremes(steps):
    v_min = 0
    v_max = 0
    for step in steps:
        if step[g.M_TYPE] == g.M_CONSTANT:
            if step[g.M_CONST_V] < v_min:
                v_min = step[g.M_CONST_V]
            elif step[g.M_CONST_V] > v_max:
                v_max = step[g.M_CONST_V]
        elif step[g.M_TYPE] == g.M_RAMP:
            if step[g.M_RAMP_V1] > step[g.M_RAMP_V2]:
                hi = step[g.M_RAMP_V1]
                lo = step[g.M_RAMP_V2]
            else:
                hi = step[g.M_RAMP_V2]
                lo = step[g.M_RAMP_V1]
            if lo < v_min:
                v_min = lo
            if hi > v_max:
                v_max = hi
    return [v_min, v_max]

def html_escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&#39;")
    return s









# Classes!

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)

class saveMessageBox(QMessageBox):
    def __init__(self, parent):                       
        super().__init__()
        # set text for save message
        self.setWindowTitle(l.s_edit_discard[g.L]) 
        self.setText(l.e_edit_save_dialog[g.L])
        self.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

        # customize button language text for multi-language support
        but_save = self.button(QMessageBox.StandardButton.Save)
        but_save.setText(l.s_edit_save[g.L])
        but_disc = self.button(QMessageBox.StandardButton.Discard)
        but_disc.setText(l.s_edit_close_wo_save[g.L])
        but_canc = self.button(QMessageBox.StandardButton.Cancel)
        but_canc.setText(l.s_edit_cancel[g.L])

    
        
    
    
