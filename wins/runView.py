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
    def __init__(self, parent, tasks):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.parent = parent
        self.tasks = tasks

        self.current_task = 0

        self.port = ""
        self.process = None
        self.steps = False
        self.dt = 0
        self.method = False



        self.stopped = False
        
        
        self.reps_total = 0
        self.rep_current = 0
        
        self.i_max = ""


        self.q = Queue()

        self.status = self.statusBar()
        ##### FOR TESTING ####
        #
        #self.setWindowTitle(l.r_window_title[g.L]+' | '+self.parent.data[g.S_NAME])
        #
        ######################
        
        # Stacked layout in upper left
        self.msg_box = QStackedLayout()

        # Stacked item 0: blank
        self.msg_box.addWidget(QWidget())

        # Stacked item 1: Pre-run (**DEFAULT**)
        but_start_run = QPushButton('begin run')
        but_start_run.clicked.connect(self.start_run)
        self.msg_box.addWidget(but_start_run)
        self.msg_box.setCurrentIndex(1)

        # Stacked item 2: Device not connected
        lbl_disconnected = QLabel("Sorry, i'm having trouble finding a compatible potentiostat. Please ensure that one is connected and try again.")
        lbl_disconnected.setWordWrap(True)
        but_disconnected = QPushButton('try again')
        but_disconnected.clicked.connect(self.disconnected_try_again)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_disconnected)
        v1.addWidget(but_disconnected)
        w = QWidget()
        w.setLayout(v1)
        self.msg_box.addWidget(w)

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

    #########################################
    #                                       #
    #   Start run function                  #
    #                                       #
    #########################################

    def start_run(self):
        try:
            #self.read_updated_file()
            if self.current_task < len(self.tasks):
                if not self.process:
                    (self.run_id, self.rep_id) = self.tasks[self.current_task]
                    run = get_run_from_file_data(self.parent.data, self.run_id)
                    self.method = get_method_from_file_data(self.parent.data, run[g.R_UID_METHOD])      ####### CAN WE MAKE method a local variable? Not self? Check in after modifying data save routine
                    self.steps = self.get_steps(self.method)
                    self.dt = self.method[g.M_DT]
                    self.i_max = self.method[g.M_CURRENT_RANGE]

                    # Reset graphs
                    self.graphs.init_plot(self.method)

                    # set pre-run variables
                    [self.t, self.v, self.I] = [[],[],[]]
                    self.current_step_index = 0
                    self.t_prev = -1
                    self.t_to_add = 0
                    self.error_run_msg = ''
                    self.error_run_flag = False
                    self.save_complete_flag = False
                    #self.raw_data = []
                    #for step in self.method[g.M_STEPS]:
                    #    self.raw_data.append([])

                    # Setup some flags at beginning of run
                    self.running_flag = True
                    self.data_saved_flag = False

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
                    self.process.finished.connect(self.handle_finished)
                    self.status.showMessage('Running...')
                    self.process.start("python", ['processes/run.py', str(self.dt), self.i_max, str(self.steps), self.port])      
                   
        except Exception as e:
            print(e)

    #########################################
    #                                       #
    #   Run process handlers                #
    #                                       #
    #########################################

    def handle_stdout(self):
        print('stdout')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        
        [prefixes, msgs] = self.unpack_msgs(stdout)
        for i, prefix in enumerate(prefixes):
            if prefix == g.R_DATA_PREFIX:
                self.q.put(msgs[i])
            elif prefix == g.R_ERROR_PREFIX:
                self.error_run_flag = True
                self.error_run_msg = msgs[i]
                print(prefix)
                print(msgs[i])
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

    def handle_finished(self):
        if self.stopped:
            return
            ##########################
            #
            # Do stopped stuff here!
            #
            #
            #
            ##########################
        try:    
            self.process = None                     # these two lines must be in this order, because running_flag==False
            self.running_flag = False               #   is a precondition for the interrupt to begin the save process
            while not self.save_complete_flag:      # Wait here until data is saved, before removing reference to process
                time.sleep(0.05)

            self.message("Finished rep "+str(self.current_task+1)+" of "+str(len(self.tasks)))
            
            if self.error_run_flag:     # If there was an error during this run
                if self.error_run_msg == g.R_ERROR_NO_CONNECT:
                    self.message('error, no device detected')
                    self.msg_box.setCurrentIndex(2)
                if self.error_run_msg == g.R_ERROR_VMAX_TOO_HIGH:
                    self.message("error, this device doesn't support a maximum voltage this high.")
                
                ######################
                #
                #   HANDLE ERROR ON RUN HERE (Depends on error code...)
                #
                ######################
            
            
            else:
                self.current_task = self.current_task + 1   # Increment task

                if self.current_task < len(self.tasks):
                    self.start_run()
                else:
                    self.message('RUN IS COMPLETE!')
                    print('run complete!')
                    #self.process = None
                    #self.running = False
            
        except Exception as e:
            print(e)

        '''def init_pstat_process(self):
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
            self.message('Process started!')'''

    def message(self, s):
        self.run_details.appendPlainText(s)

    def unpack_msgs(self, str_bundle):
        try:
            prefixes = []
            messages = []
            str_msgs = str_bundle.split('\r\n')
            for s in str_msgs:
                prefixes.append(s[0:len(g.R_DATA_PREFIX)])
                messages.append(s[len(g.R_DATA_PREFIX):len(s)])
            return [prefixes, messages]
        except Exception as e:
            print(e)

    
        

        



    def empty_q(self):
        while not self.q.empty():   # As long as there is any data in queue                    
            self.q.get()            # Pop the next item!



    #########################################
    #                                       #
    #   Functions for msg_box buttons       #
    #                                       #
    #########################################
     
    def disconnected_try_again(self):
        self.msg_box.setCurrentIndex(0)
        self.start_run()

     

            

        
    def stop_run(self): ################### WORK THIS OUT SO THAT IT ACTUALLY WORKS RELIABLY WITHOUT CRASHING THE PROGRAM!!!!
        try:
            if self.process:
                self.stopped = True
                self.running_flag = False
                self.process.kill()
                self.process = None
                self.message("Run STOPPED by user")
                # Display message that allows user to resume from start of active run
                #
                #
        except Exception as e:
            print(e)
            
    def get_steps(self, method):
        """
        Takes this method and
        figures out when each relay should be turned on/off, creating a new array entry
        (separate step) for modifying the state of each relay. Makes sure all relays are
        off at the end of the run. Returns a list of steps where each step either changes
        the state of a relay or does a run on the potentiostat.
        """
        new_method = []
        relay_on = []
        for i in enumerate(g.M_RELAYS):
            relay_on.append(False)
        
        
        for step in method[g.M_STEPS]:
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
        try:
            #self.parent.load_sample_info()
            self.data = self.parent.data
        except Exception as e:
            print(e)

    #########################################
    #                                       #
    #   Interrupt data getter               #
    #    (and associated functions)         #
    #                                       #
    #   1. interrupt_data_getter            #
    #   2. store_and_graph_from_queue       #
    #   3. graph_new_data                   #
    #   4. store_queued_data                #
    #   5. save_rep_raw_data                #
    #                                       #
    #########################################

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
        
        while self.running_flag:          # while run is ongoing
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
        #self.raw_data[self.current_step_index].append((t_new, v_new, I_new))
        self.t_prev = t_now                                         # Store this time as the previous time for next

    def save_rep_raw_data(self):
        print('this is where we would start an async save of the raw data...')
        self.save_complete_flag = True      # For debugging, pretending like we did a successful save here...









        
        return
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
            self.data_saved_flag = True
        except Exception as e:
            print(e)
            self.message('Sorry! We were unable to save the data!')

















    '''def update_replicate_msg(self, this_rep, total_reps):
        print("--- Running replicate", this_rep+1, "of", total_reps, "---")'''



        
        
        
                
    def get_uid_of_current_rep(self):
        return g.R_REPLICATE_UID_PREFIX + str(self.rep_current)

    def update_win(self):
        """This is necessary for parent window to call this one to update.
        Please do not delete!"""
        return
    
    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.set_enabled_children(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.accept_close(event)

    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()

