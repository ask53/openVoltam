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

from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from ast import literal_eval
import threading
from queue import SimpleQueue as Queue
import time

#from devices.supportedDevices import devices
from embeds.runPlots import RunPlots

from PyQt6.QtCore import QProcess, QDateTime
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QTextEdit
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
        self.time_completed = None
        self.running_flag = False
        self.relays_enabled = True



        self.stopped = False
        
        #### DELETE THIS WHEN POSSIBLE
        #
        self.rep_current = 0
        #
        ############


        self.q = Queue()

        self.status = self.statusBar()
        
        ##### FOR TESTING ####
        #
        #self.setWindowTitle(l.r_window_title[g.L]+' | '+self.parent.data[g.S_NAME])
        #
        ######################
        
        # Stacked layout in upper left
        self.msg_box = QStackedLayout()
        self.msg_box_container = QWidget()
        self.msg_box_container.setLayout(self.msg_box)
        self.msg_box_container.setObjectName('msg_container')

        # Stacked item 0: blank
        self.msg_box.addWidget(QWidget())

        # Stacked item 1: Pre-run (**DEFAULT**)
        but_start_run = QPushButton('begin run')
        but_start_run.clicked.connect(self.start_run)
        self.msg_box.addWidget(but_start_run)
        self.msg_box.setCurrentIndex(1)

        # Stacked item 2: Device not connected
        lbl_disconnected = QLabel("No potentiostat detected. Please ensure that one is connected and try again.")
        lbl_disconnected.setWordWrap(True)
        but_disconnected = QPushButton('try again')
        but_disconnected.clicked.connect(self.try_again)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_disconnected)
        v1.addWidget(but_disconnected)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('error')
        self.msg_box.addWidget(w)

        # Stacked item 3: Error during run
        lbl_error_in_run = QLabel("Error during run! Please check potentiostat connection and select an option:")
        lbl_error_in_run.setWordWrap(True)
        but_er_save = QPushButton('save data and go to next')
        but_er_next = QPushButton('go to next rep WITHOUT saving')
        but_er_try_agian = QPushButton('erase data and try again')
        but_er_save.clicked.connect(self.next_run_with_save)
        but_er_next.clicked.connect(self.next_run_save_nothing)
        but_er_try_agian.clicked.connect(self.try_again)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_error_in_run)
        v1.addWidget(but_er_save)
        v1.addWidget(but_er_next)
        v1.addWidget(but_er_try_agian)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('error')
        self.msg_box.addWidget(w)

        # Stacked item 4: Error during save
        lbl_error_in_save = QLabel("Yikes, we ran into an error saving the run!")
        lbl_error_in_save.setWordWrap(True)
        but_save_er_save = QPushButton('Try save again')
        but_save_er_skip = QPushButton('go to next rep WITHOUT saving')
        but_save_er_save.clicked.connect(self.next_run_with_save)
        but_save_er_skip.clicked.connect(self.skip_save)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_error_in_save)
        v1.addWidget(but_save_er_save)
        v1.addWidget(but_save_er_skip)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('error')
        self.msg_box.addWidget(w)

        # Stacked item 5: All done.
        lbl_done = QLabel("Run complete!")
        lbl_done.setWordWrap(True)
        but_done = QPushButton("Close")
        but_done.clicked.connect(self.close)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_done)
        v1.addWidget(but_done)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('success')
        self.msg_box.addWidget(w)

        # Stacked item 6: Error with potentiostat configuration.
        lbl_error = QLabel("Error with potentiostat configuration:")
        lbl_error.setWordWrap(True)
        self.lbl_error_msg = QLabel()
        but_next = QPushButton("Continue")
        but_done = QPushButton("Exit without saving")
        but_next.clicked.connect(self.next_run_with_save)
        but_done.clicked.connect(self.close)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_error)
        v1.addWidget(self.lbl_error_msg)
        v1.addWidget(but_next)
        v1.addWidget(but_done)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('error')
        self.msg_box.addWidget(w)

        # Stacked item 7: Error with re/setting a relay.
        lbl_error = QLabel("There was an error while setting the relay state.")
        lbl_error.setWordWrap(True)
        but_repeat = QPushButton("Try again")
        but_no_relays = QPushButton("Disable relays and try again")
        but_continue = QPushButton("Save and go to next task")
        but_repeat.clicked.connect(self.try_again)
        but_no_relays.clicked.connect(self.toggle_relays_and_repeat)
        but_continue.clicked.connect(self.next_run_with_save)
        v1 = QVBoxLayout()
        v1.addWidget(lbl_error)
        v1.addWidget(but_repeat)
        v1.addWidget(but_no_relays)
        v1.addWidget(but_continue)
        w = QWidget()
        w.setLayout(v1)
        w.setObjectName('error')
        self.msg_box.addWidget(w)



        # Run details scrolling text (in html or markdown format)
        self.run_details = QTextEdit()
        self.run_details.setReadOnly(True)
        s = '<b>Tasks to run:</b><br>'
        for task in self.tasks:
            s = s + str(task[0])+', '+str(task[1])+'<br>'
        self.run_details.setHtml(s)


     
        but_stop_run = QPushButton('\nSTOP\n')
        but_stop_run.clicked.connect(self.stop_run)
        but_stop_run.setToolTip('To stop run, just unplug device from computer!')
        ######### KEEPING THIS BUTTON GREYED OUT UNTIL IT WORKS!
        #
        but_stop_run.setEnabled(False)
        #
        ##############################
        self.graphs = RunPlots()

        v_left = QVBoxLayout()
        h1 = QHBoxLayout()

        v_left.addWidget(self.msg_box_container)
        v_left.addWidget(self.run_details)
        v_left.addWidget(but_stop_run)

        h1.addLayout(v_left)
        h1.addWidget(self.graphs)

        #Status bar messaging

        # Count
        count_status_lbl1 = QLabel('Task ')
        self.count_status = QLabel('...')               # stored to self for access later
        count_status_lbl2 = QLabel(' of ')
        count_status_lbl3 = QLabel(str(len(self.tasks)))

        # Relays        #####################################################################
        #
        #
        #       CONVERT THIS WHOLE THING TO A FOR-LOOP THAT CREATES THESE BASED ON THE PASSED METHOD
        #       ONCE WE'VE MOVED ALL RELAYS TO A LOOPING AND NUMBERED FORMAT
        #       THEN GET RELAY NAMES FROM THE METHOD.
        #
        
        r0_lbl = QLabel('STIR: ')
        r0_status = QLabel('OFF')
        r1_lbl = QLabel('VIBRATE: ')
        r1_status = QLabel('OFF')
        

        self.relay_statuses = {'stir': r0_status,       # stored to self for access later
                               'vibrate': r1_status}

        ########################################################################################

        # Lay out status bar "permanent" widgets
        h2 = QHBoxLayout()
        h2.addWidget(r0_lbl)
        h2.addWidget(r0_status)
        h2.addWidget(QVLine())
        h2.addWidget(r1_lbl)
        h2.addWidget(r1_status)
        h2.addWidget(QVLine())
        h2.addWidget(count_status_lbl1)
        h2.addWidget(self.count_status)
        h2.addWidget(count_status_lbl2)
        h2.addWidget(count_status_lbl3)
        
        w_perm_status = QWidget()
        w_perm_status.setLayout(h2)
        self.status.addPermanentWidget(w_perm_status)
        
        
    

        
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
            if self.current_task < len(self.tasks):
                if not self.process:
                    self.msg_box.setCurrentIndex(0)
                    (self.run_id, self.rep_id) = self.tasks[self.current_task]
                    self.run = get_run_from_file_data(self.parent.data, self.run_id)
                    self.method = get_method_from_file_data(self.parent.data, self.run[g.R_UID_METHOD])      ####### CAN WE MAKE method a local variable? Not self? Check in after modifying data save routine
                    self.steps = self.get_steps(self.method)
                    if not self.relays_in_steps(self.steps):
                        self.relays_enabled = False
                    self.dt = self.method[g.M_DT]
                    i_max = self.method[g.M_CURRENT_RANGE]

                    # Reset graphs
                    self.graphs.init_plot(self.method)

                    # set pre-run variables
                    [self.t, self.v, self.I] = [[],[],[]]
                    self.current_step_index = 0
                    self.t_prev = -1
                    self.t_to_add = 0
                    self.error_run_msg = ''
                    self.error_run_flag = False
                    self.data_storage_complete_flag = False
                    
                    # Setup some flags at beginning of run
                    self.running_flag = True
                    self.data_saved_flag = False

                    # Empty the queue
                    self.empty_q()

                    self.set_run_details()
                    

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
                    self.count_status.setText(str(self.current_task+1))

                    
                    self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_RUN, str(self.dt), i_max, str(self.steps), self.port, str(self.relays_enabled)])
                   
        except Exception as e:
            print(e)

    def set_run_details(self):

        rep = get_rep(self.parent.data, self.tasks[self.current_task])
        
        s = '<u>'+self.tasks[self.current_task][0]+', '+self.tasks[self.current_task][1]+'</u><br>'
        s = s + '<b>Run type: </b>'+l.rc_types[self.run[g.R_TYPE]][g.L] +'<br>'
        s = s + '<b>Method: </b>'+self.method[g.M_NAME] +'<br><br>'
        
        s = s + '<b>Device: </b>'+self.run[g.R_DEVICE]+'<br>'
        s = s + '<b>Current range: </b>'+self.method[g.M_CURRENT_RANGE]+'<br>'
        s = s + '<b>Sample frequency:</b> Every '+str(self.dt)+' miliseconds<br><br>'

        s = s + '<b>Run note: </b>'+self.run[g.R_NOTES]+'<br>'
        s = s + '<b>Replicate note: </b>'+rep[g.R_NOTES]+'<br>'
        
        self.run_details.setHtml(s)
            
            

    #########################################
    #                                       #
    #   Run process handlers                #
    #                                       #
    #########################################

    def handle_stdout(self):
        #print('stdout')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        
        [prefixes, msgs] = self.unpack_msgs(stdout)
        for i, prefix in enumerate(prefixes):
            if prefix == g.R_DATA_PREFIX:
                self.q.put(msgs[i])
            elif prefix == g.R_PORT_PREFIX:
                #print('port is:',msgs[i])
                self.port = msgs[i]
            elif prefix == g.R_RELAY_PREFIX:
                try:
                    #rels = literal_eval(msgs[i])
                    [relay, state] = msgs[i].split('-')
                    #relay = int(relay)                 # <<<--- enable this line when we setup integer numbering of relays!
                    state = literal_eval(state)
                
                    if state:
                        self.relay_statuses[relay].setText('ON')
                    else:
                        self.relay_statuses[relay].setText('OFF')
                except Exception as e:
                    print(e)
            elif prefix == g.R_STATUS_PREFIX:
                pass
                #print(prefix)
                #print(msgs[i])
                # do something with statuses here if you want! 
            else:
                pass
                #print(prefix)
                #print(msgs[i])

    def handle_stderr(self):
        #print('stderr')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print('ERROR PASSED THRU STDERR STREAM')
        print(stderr)
        err = ''
        try:
            err = stderr.split('\r\n')[-2].replace('ValueError: ','')   # Grab error message 
            print(err)
        except:                                                         # if grabbing msg errors, no worries, report error w no message
            pass
        self.error_run_flag = True
        self.error_run_msg = err
        
                                                    #   typically by a return/newline (\r\n)
    def handle_state(self, state):
        return

    def handle_finished(self):
        self.time_completed = QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)
        self.status.showMessage('')
        
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
            self.process = None                         # these two lines must be in this order, because running_flag==False
            self.running_flag = False                   #   is a precondition for the interrupt to begin the save process
            while not self.data_storage_complete_flag:  # Wait here until data is saved, before removing reference to process
                time.sleep(0.25)

            if self.error_run_flag:     # If there was an error during this run
                self.status.showMessage('Error!')
                if self.error_run_msg == g.R_ERROR_NO_CONNECT:      # if the error was a failure to connect
                    self.msg_box.setCurrentIndex(2)
                elif self.error_run_msg == g.R_ERROR_VMAX_TOO_HIGH: # if the error is that method is incompatible with device
                    self.lbl_error_msg.setText("The method's voltage is too extreme for this device!")
                    self.msg_box.setCurrentIndex(6)
                    #########################################
                    #
                    #   SHOULD THIS ACTUALLY BE HERE? WE SHOULD BE DOING COMPATIBILITY CHECKING IN PREVIOUS WINDOW =0
                    #
                    ####################################
                elif self.error_run_msg == g.R_ERROR_SET_RELAY:    # there was an error setting a relay
                    self.msg_box.setCurrentIndex(7)
                else:                                               # assume error during the run, likely cable issue
                    self.msg_box.setCurrentIndex(3)
                
            else:                                       # If run completed withou an error
                self.status.showMessage('Saving...')    # ...This will only appear if we sort out async saves here....oh well. ####
                self.synchronous_data_save()
                
            
        except Exception as e:
            print(e)


    def message(self, s):
        self.run_details.append(s)

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
    
    def try_again(self):
        self.msg_box.setCurrentIndex(0)
        self.start_run()
        
    def next_run_with_save(self):
        print('here! yay!')
        self.msg_box.setCurrentIndex(0)
        self.synchronous_data_save()

    def next_run_save_nothing(self):
        self.msg_box.setCurrentIndex(0)
        [self.t, self.v, self.I] = [[],[],[]]
        self.synchronous_data_save()

    def skip_save(self):
        self.msg_box.setCurrentIndex(0)
        self.go_to_next_step()

    def toggle_relays_and_repeat(self):
        self.relays_enabled = False
        self.try_again()
        

    #########################################
    #                                       #
    #   Functions for async save            #
    #                                       #
    #########################################

    def synchronous_data_save(self):
        try:
            data = get_data_from_file(self.parent.path)
            rep = get_rep(data, self.tasks[self.current_task])
            if self.error_run_flag:
                rep[g.R_STATUS] = g.R_STATUS_ERROR
            else:
                rep[g.R_STATUS] = g.R_STATUS_COMPLETE
            rep[g.R_TIMESTAMP_REP] = self.time_completed
            rep[g.R_DATA] = self.raw_data_to_dict()

            write_data_to_file(self.parent.path, data)
            data = remove_data_from_layout(data)
            self.parent.data = data
            self.parent.update_win()
            self.status.showMessage('Complete.')
            self.go_to_next_step()
            

        except Exception as e:
            self.msg_box.setCurrentIndex(4) # if save error, alert the user!
            print(e)

    def go_to_next_step(self):
        self.current_task = self.current_task + 1
        if self.current_task < len(self.tasks):
            self.start_run()
        else:
            self.all_done()
            
    def all_done(self):
        s = '<u>Run summary</u><br><br>'
        ers = False
        for task in self.tasks:
            rep = get_rep(self.parent.data, task)
            if rep[g.R_STATUS] == g.R_STATUS_COMPLETE:
                s = s +'<b>'+ task[0] + ', ' + task[1] +'</b>:   <u>Complete</u><br>'
            elif rep[g.R_STATUS] == g.R_STATUS_ERROR:
                ers = True
                s = s +'<b>'+ task[0] + ', ' + task[1] +'</b>:   <u>Error</u> during the run (caution: some data may have been saved)<br>'
        if not ers:
            s = s + '<br>:)'

        self.run_details.setHtml(s)
        self.msg_box.setCurrentIndex(5)
        

        
        

        
        
    # STUFF FOR ASYNC SAVE...REHAB THIS SOMEDAY?
    '''self.status.showMessage('Saving run...')
        self.parent.start_async_save(g.SAVE_TYPE_REP_WITH_DATA,
                                     [self.tasks[self.current_task], newRep],
                                     onSuccess=self.after_save_success,
                                     onError=self.after_save_error)'''

    '''def after_save_success(self):
        print('saved successfully!')

    def after_save_error(self):
        print('save ErR0r!')'''
    ##########################

                         
    



     

            

        
    def stop_run(self): ################### WORK THIS OUT SO THAT IT ACTUALLY WORKS RELIABLY WITHOUT CRASHING THE PROGRAM!!!!
        try:
            if self.process:
                self.stopped = True
                self.running_flag = False
                self.process.kill()
                self.process = None
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

    def relays_in_steps(self, steps):
        relays = False
        for step in steps:
            print(step)
            if step[g.M_TYPE] == g.M_RELAY:
                relays = True
                break
        return relays
        
    def raw_data_to_dict(self):
        data = []
        for i, t in enumerate(self.t):
            data.append({g.R_DATA_TIME: self.t[i],
                         g.R_DATA_VOLT: self.v[i],
                         g.R_DATA_CURR: self.I[i]})
        return data

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
            #print('checking')
            self.store_and_graph_from_queue()   
            time.sleep(g.R_PLOT_REFRESH_TIME)   # (this controls frequency of interrupt)

        time.sleep(g.R_POST_RUN_WAIT_TIME)      # once run is complete, wait a bit to make sure all remaining data is in queue
        self.store_and_graph_from_queue()       # and store and graph all the data remaining in queue
        self.data_storage_complete_flag = True  # Indicate that all data has been stored in RAM and return, ending interrupt thread

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
        self.t_prev = t_now                                         # Store this time as the previous time for next

    














        
        
                
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
        if self.running_flag:
            event.ignore()
            show_alert(self, "Alert!", "Sorry, cannot close this window while the run is ongoing. If you need to stop an ongoing run, just unplug the potentiostat!")
        else:
            self.parent.setEnabled(True)
            self.parent.set_enabled_children(True)
            self.accept_close(event)

    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()

