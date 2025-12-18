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

from ast import literal_eval
import threading
from queue import SimpleQueue as Queue
import time

#from devices.supportedDevices import devices
from embeds.runVoltagePlot import RunVoltagePlot
from embeds.runPlots import RunPlots

from PyQt6.QtCore import QProcess
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
        self.stopped = False
        self.process = None
        self.port = ""
        self.reps_total = 0
        self.rep_current = 0
        self.dt = 0
        self.i_max = ""
        self.run_raw_data = []
        self.t_prev = -1
        self.t_to_add = 0
        self.current_step_index = 0
        self.data_saved = False
        [self.t, self.v, self.I] = [[],[],[]]
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
        but_stop_run = QPushButton('\nSTOP\n')
        but_stop_run.clicked.connect(self.stop_run)
        self.graphs = RunPlots()

        v_left = QVBoxLayout()
        h1 = QHBoxLayout()

        v_left.addLayout(self.msg_box)
        v_left.addWidget(self.run_details)
        v_left.addWidget(but_stop_run)

        h1.addLayout(v_left)
        h1.addWidget(self.graphs)
        






        
        w = QWidget()
        w.setLayout(h1)
        self.setCentralWidget(w)
        
    def set_run_uid(self, uid):
        self.uid = uid
        self.msg_box.setCurrentIndex(1)

    def message(self, s):
        self.run_details.appendPlainText(s)

    def unpack_msgs(self, str_bundle):
        try:
            prefixes = []
            messages = []
            str_msgs = str_bundle.split('\n')
            for s in str_msgs:
                prefixes.append(s[0:len(g.R_DATA_PREFIX)])
                messages.append(s[len(g.R_DATA_PREFIX):len(s)])
            return [prefixes, messages]
        except Exception as e:
            print(e)

    def handle_stdout(self):
        print('stdout')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        
        [prefixes, msgs] = self.unpack_msgs(stdout)
        for i, prefix in enumerate(prefixes):
            if prefix == g.R_DATA_PREFIX:
                self.q.put(msgs[i])
            else:
                print(prefix)
                print(msgs[i])

    def handle_stderr(self):
        print('stderr')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_state(self, state):
        return

    def handle_finished_rep(self):
        if self.stopped:
            return
        
           
        try:
            self.message("Finished rep "+str(self.rep_current+1)+" of "+str(self.reps_total))
            self.running = False
            while not self.data_saved:                  # Wait here until data is saved, before removing reference to process
                time.sleep(0.05)
            self.process = None                         # Remove reference to process cause its done! 
            self.rep_current = self.rep_current + 1     # Increment rep

            if self.rep_current < self.reps_total:
                self.init_pstat_process()
            else:
                self.message('RUN IS COMPLETE!')
                self.process = None
                self.running = False
            
        except Exception as e:
            print(e)
        

        

    def init_pstat_process(self):
        if self.process is None:
            # Reset graphs and set pre-run variables
            self.graphs.init_plot(self.method)
            self.init_raw_data()
            
            
            # Setup some flags at beginning of run
            self.running = True
            self.data_saved = False

            # Empty the queue
            self.empty_q()

            # Setup and start interrupt to retreive and plot data (this should end after last data from run is saved)
            thread = threading.Thread(target=self.interrupt_data_getter) 
            thread.daemon = True                            # interrupt ends when the start_run() fn returns
            thread.start()

            # Initiate and begin external process (that I/Os with potentiostat
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.handle_finished_rep)
            self.process.start("python", ['processes/run.py', str(self.dt), self.i_max, str(self.steps), self.port])
            self.message('Process started!')

    def empty_q(self):
        while not self.q.empty():   # As long as there is any data in queue                    
            self.q.get()            # Pop the next item!

    def init_raw_data(self):
        [self.t, self.v, self.I] = [[],[],[]]
        self.current_step_index = 0
        self.t_prev = -1
        self.t_to_add = 0
        self.raw_data = []
        for step in self.method[g.M_STEPS]:
            self.raw_data.append([])
        
     
    def start_run(self):
        try:
            self.read_updated_file()
            self.run = get_run_from_file_data(self.data, self.uid)
            self.reps_total = len(self.run[g.R_REPLICATES])
            self.rep_current = 0
            self.method = get_method_from_file_data(self.data, self.run[g.R_UID_METHOD])
            self.steps = self.get_steps()
            self.dt = self.method[g.M_DT]
            self.i_max = self.method[g.M_CURRENT_RANGE]

            # Start run
            self.init_pstat_process()
              
               
        except Exception as e:
            print(e)

     

            

        
    def stop_run(self): ################### WORK THIS OUT SO THAT IT ACTUALLY WORKS RELIABLY WITHOUT CRASHING THE PROGRAM!!!!
        try:
            if self.process:
                self.stopped = True
                self.running = False
                self.process.kill()
                self.process = None
                self.message("Run STOPPED by user")
                # Display message that allows user to resume from start of active run
                #
                #
        except Exception as e:
            print(e)
            
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
            self.store_and_graph_from_queue()   
            time.sleep(g.R_PLOT_REFRESH_TIME)   # (this controls frequency of interrupt)

        time.sleep(g.R_POST_RUN_WAIT_TIME)      # once run is complete, wait a bit to make sure all remaining data is in queue
        self.store_and_graph_from_queue()       # and store and graph all the data remaining in queue
        self.save_rep_raw_data()

    def store_and_graph_from_queue(self):
        while not self.q.empty():                       # and there is some data in queue
            self.store_queued_data() # store the data
        self.graph_new_data()
        
    def graph_new_data(self):
        self.graphs.update_plots(self.t, self.v, self.I)

    def store_queued_data(self):
        a = self.q.get()                                            # Get oldest item from queue
        data_tup = literal_eval(a)                                  # Convert to tuple
        t_now = data_tup[0]                                         # Grab time from tuple
        if t_now < self.t_prev:                                     # If this is the start of a new step
            step = self.method[g.M_STEPS][self.current_step_index]  #   get the current step
            dur = step[g.M_T]                                       #   get expected duration from method
            if dur - self.t_prev < self.dt:                         #   if the last time value reported is less than dt from the duration
                self.t_to_add = self.t_to_add + dur                 #       yay! the duration was pretty accurate!
            else:                                                   #   otherwise
                self.t_to_add = self.t_prev                         #       assume the previous run ended after last timestamp
            self.current_step_index = self.current_step_index + 1   # increment the current step index
            
        t_new = t_now + self.t_to_add
        v_new = data_tup[1]
        I_new = data_tup[2]
        self.t.append(t_now + self.t_to_add)                        # Append values for plotting 
        self.v.append(v_new)
        self.I.append(I_new)                                        # Append tuple to appropriate method list
        self.raw_data[self.current_step_index].append((t_new, v_new, I_new))
        self.t_prev = t_now                                         # Store this time as the previous time for next

    def update_replicate_msg(self, this_rep, total_reps):
        print("--- Running replicate", this_rep+1, "of", total_reps, "---")

    def save_rep_raw_data(self):
        self.message("Saving data for rep "+str(self.rep_current+1))
        raw_data = []
        for i,step in enumerate(self.method[g.M_STEPS]):
            if step[g.M_DATA_COLLECT]:
                for datum in self.raw_data[i]:
                    raw_data.append({
                        g.R_DATA_TIME: datum[0],
                        g.R_DATA_VOLT: datum[1],
                        g.R_DATA_CURR: datum[2]
                        })
        for run in self.data[g.S_RUNS]:
            if run[g.R_UID_SELF] == self.uid:
                print(run)
                for rep in run[g.R_REPLICATES]:
                    if rep[g.R_UID_SELF] == self.get_uid_of_current_rep():
                        rep[g.R_DATA] = raw_data
        try:
            self.parent.data = self.data
            write_data_to_file(self.parent.path, self.data)
            self.data_saved = True
        except Exception as e:
            print(e)
            self.message('Sorry! We were unable to save the data!')

        
        
        
                
    def get_uid_of_current_rep(self):
        return g.R_REPLICATE_UID_PREFIX + str(self.rep_current)
    
    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.setEnabledChildren(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        try:
            self.parent.setEnabled(True)
            self.parent.setEnabledChildren(True)
            self.__init__(self.parent)
            event.accept()
        except Exception as e:
            print(e)
