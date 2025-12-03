"""
run.py

This file defines a class WindowRun which creates a window
object that does the run. It follows the following algorithm:

1. Connect to device
2. Run the run in the file (accessed at self.parent.path) and
    determined by the argument run_uid
3. For each replicate:
    a. Shows the number of the current replicate and total # of reps
    b. Shows realtime graphs of the voltage being applied and the
    current being measured
4. At end of complete run (all replicates complete), saves
    all data to file. 
    
"""


import ov_globals as g
import ov_lang as l
from ov_functions import *

#from devices.supportedDevices import devices

#from functools import partial

#from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)

class WindowRun(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.setWindowTitle(l.r_window_title[g.L])
        
        w = QWidget()
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)

    def start_run(self, uid):
        self.uid = uid
        print("now we're starting the run from within the new object yayyyy")

    

    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.setEnabledChildren(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        self.parent.setEnabled(True)
        self.parent.setEnabledChildren(True)
        event.accept()

    
            
            

    

    ############################################################################
        
