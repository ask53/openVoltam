# ov_functions.py
#		

from tabularjson import parse, stringify, StringifyOptions

import ov_globals as g
from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea
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

def applyStyles():
    g.APP.setStyleSheet(g.STYLES)

def show_alert(obj, title, msg):
    dlg = QMessageBox(obj)
    dlg.setWindowTitle(title)
    dlg.setText(msg)
    dlg.exec()

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
            
            options: StringifyOptions = {"indentation": 4, "trailingCommas": False}
            tab_json_to_write = stringify(data, options)       #   convert dictionary to json string
            file.write(tab_json_to_write)                                       #   write json string to file
            file.close()                                                    #   close the file (to avoid taking up too much memory)
        return True
    except Exception as e:
        print(e)
        return False

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
    

def sweep_profiles_match(sp1, sp2):
    ''' Takes in two sweep profile dicts, sp1 and sp2
    checks whether they match. If so, returns True,
    if not, returns False'''

    #####   THIS IS A PLACE HOLDER, WRITE ACTUAL FUNCTION ONCE WE KNOW STRUCTURE OF SWEEP PROFILES!
    #
    if sp1[g.SP_NOTES] == sp2[g.SP_NOTES]:
        return True
    return False
    #
    #
    ################################################################################################

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

    
        
    
    
