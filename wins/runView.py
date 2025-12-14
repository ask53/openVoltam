"""
runView.py

This file defines a class WindowRunView which creates a window
object that lets the user view and control the run. It follows
the following algorithm:

1. Connect to device
2. Run the run in the file (accessed at self.parent.path) and
    determined by the argument run_uid
3. For each replicate:
    a. Shows the number of the current replicate and total # of reps
    b. Shows realtime graphs of the voltage being applied and the
    current being measured
    c. Shows status of step/run and prompts user for any needed
    input (save/delete, stop run, restart run, etc.)
4. At end of complete run (all replicates complete), saves
    all data to file. 
    
"""
import sys

import ov_globals as g
import ov_lang as l
from ov_functions import *

from potentiostat import Potentiostat

import serial.tools.list_ports
from re import sub
import threading
from queue import SimpleQueue as Queue
import time

#from devices.supportedDevices import devices

#from functools import partial

from PyQt6.QtCore import QProcess#Qt, QDateTime
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QPlainTextEdit
)

class WindowRunView(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.data = False
        self.uid = False
        self.run = False
        self.method = False
        self.steps = False
        self.running = False
        self.process = None
        self.port = ""
        self.run_raw_data = []
        self.q = Queue()
        self.setWindowTitle(l.r_window_title[g.L]+' | '+self.parent.data[g.S_NAME])

        # Stacked layout in upper left
        self.msg_box = QStackedLayout()
        self.msg_box.addWidget(QWidget())

        # Stacked item 0: Pre-run
        but_start_run = QPushButton('begin run')
        but_start_run.clicked.connect(self.start_run)
        self.msg_box.addWidget(but_start_run)

        self.run_details = QPlainTextEdit()
        but_close = QPushButton()
        graph_area_voltage = QScrollArea()
        graph_area_current = QScrollArea()

        v_left = QVBoxLayout()
        v_right = QVBoxLayout()
        h1 = QHBoxLayout()

        v_left.addLayout(self.msg_box)
        v_left.addWidget(self.run_details)
        v_left.addWidget(but_close)

        v_right.addWidget(graph_area_voltage)
        v_right.addWidget(graph_area_current)

        h1.addLayout(v_left)
        h1.addLayout(v_right)
        






        
        w = QWidget()
        w.setLayout(h1)
        self.setCentralWidget(w)
        
    def set_run_uid(self, uid):
        self.uid = uid
        self.msg_box.setCurrentIndex(1)

    def message(self, s):
        self.run_details.appendPlainText(s)

    def handle_stdout(self):
        print('stdout')
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_stderr(self):
        print('stderr')
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_state(self, state):
        return

    def handle_finished(self):
        self.message("Process finished.")
        self.p = None
        

    def start_run(self):
        try:
            self.msg_box.setCurrentIndex(0)
            self.read_updated_file()
            self.run = get_run_from_file_data(self.data, self.uid)
            self.method = get_method_from_file_data(self.data, self.run[g.R_UID_METHOD])
            self.steps = self.get_steps()
            dt = self.method[g.M_DT]
            i_max = self.method[g.M_CURRENT_RANGE]
            if self.process is None:
               self.message('Beginning process!')
               self.p = QProcess()
               self.p.readyReadStandardOutput.connect(self.handle_stdout)
               self.p.readyReadStandardError.connect(self.handle_stderr)
               self.p.stateChanged.connect(self.handle_state)
               self.p.finished.connect(self.handle_finished)
               self.p.start("python", ['processes/run.py', str(dt), i_max, str(self.steps), self.port])
        except Exception as e:
            print(e)

        ''' self.running = True

            # setup interrupt
            thread = threading.Thread(target=self.interrupt_data_getter) 
            thread.daemon = True                            # interrupt ends when the start_run() fn returns
            thread.start()

            
            try:
                for i,rep in enumerate(self.run[g.R_REPLICATES]): 
                    self.update_replicate_msg(i, len(self.run[g.R_REPLICATES]))
                    self.do_run()
            except Exception as e:
                print(e)
                self.running = False
                #   and figure out what to do here (offer user to save ###################################
                #   data as incomplete or restart or whatever). ##############################################################

            self.running = False
            time.sleep(1)
            print(self.run_raw_data)
            
            print('-------')'''

        

            
    def get_steps(self):
        """
        Assumes that there is a method loaded into self.method. Takes this method and
        figures out when each relay should be turned on/off, creating a new array entry
        (separate step) for modifying the state of each relay. Makes sure all relays are
        off at the end of the run. Returns a list of steps where each step either changes
        the state of a relay or does a run on the potentiostat.
        """
        new_method = []
        relay_on = []
        for i in enumerate(g.M_RELAYS):
            relay_on.append(False)
        
        
        for step in self.method[g.M_STEPS]:
            #new_steps = []
            for i, relay in enumerate(g.M_RELAYS):
                if not relay_on[i] and step[relay]:     # if the relay is OFF and needs to be ON for this step
                    new_method.append({                 # append a step to the method turning this relay ON
                        g.M_TYPE: g.M_RELAY,
                        g.M_RELAY: relay,
                        g.M_RELAY_STATE: True})
                    relay_on[i] = True
                elif relay_on[i] and not step[relay]:   # if the relay is ON and needs to be OFF for this step
                    new_method.append({                 # append a step to the method turning this relay OFF
                        g.M_TYPE: g.M_RELAY,
                        g.M_RELAY: relay,
                        g.M_RELAY_STATE: False})
                    relay_on[i] = False
            new_method.append(step)                     # then append the step itself

        for i, relay in enumerate(g.M_RELAYS):          # at end, add steps for turning off all relays as needed
            if relay_on[i]:
                new_method.append({
                    g.M_TYPE: g.M_RELAY,
                    g.M_RELAY: relay,
                    g.M_RELAY_STATE: False})

        return new_method
        
    def read_updated_file(self):
        self.parent.load_sample_info()
        self.data = self.parent.data

    def interrupt_data_getter(self):
        """
        This function is designed to be run as an interrupt and should only be started
        once the run has been initiated and self.running==True.

        As long as the running flag is set, this fn loops every g.R_PLOT_REFRESH_TIME seconds.
        On each loop, if there is data waiting on the queue, calls a function to handle
        that data.

        Once the run is complete, it waits for g.R_POST_RUN_WAIT_TIME to ensure that all
        straggler datapoints are in the queue, then handles the queued  data one last time.

        """
        
        while self.running:          # while run is ongoing
            print('checking')
            while not self.q.empty():    # and there is some data in queue
                self.store_and_graph_queued_data()           # do stuff with all that data! Organize! Graph!
            time.sleep(g.R_PLOT_REFRESH_TIME)         # (this controls frequency of interrupt)

        time.sleep(g.R_POST_RUN_WAIT_TIME)      # once run is complete, wait a bit to make sure all remaining data is in queue
        while not self.q.empty():               #   then loop thru the queue
            self.store_and_graph_queued_data()  #   and handle the last data to arrive


    def store_and_graph_queued_data(self):
        a = self.q.get()
        print("GOT <",a,"> FROM THE QUEUE")
        self.run_raw_data.append(a)

    def update_replicate_msg(self, this_rep, total_reps):
        print("--- Running replicate", this_rep+1, "of", total_reps, "---")

    def do_run(self):
        ###########################################333
        # PLACEHOLDER CODE...
        #
        #
        self.q.put('-- new run beginning now! --')
        for step in self.method:
            self.q.put(step[g.M_TYPE])
            if step[g.M_TYPE] == 'ramp':
                raise ValueError("i'm an error message!")
            time.sleep(0.25)
        #
        #
        ################################################
    
    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.setEnabledChildren(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        self.parent.setEnabled(True)
        self.parent.setEnabledChildren(True)
        event.accept()
