# ov_functions.py
#		

import ov_globals as g

def encodeCustomName(custom_name):
    return g.CUSTOM_NAME_FLAG+custom_name

def isCustomName(s):
    return s.startswith(g.CUSTOM_NAME_FLAG)

def decodeCustomName(encoded_name):
    return encoded_name.replace(g.CUSTOM_NAME_FLAG, '', 1)
