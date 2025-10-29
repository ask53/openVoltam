# ov_functions.py
#		

import ov_globals as g
from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel
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
    
    
