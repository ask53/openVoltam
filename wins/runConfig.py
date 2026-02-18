"""
window_runConfig.py

This file defines a class WindowRunConfig which creates a window
object that can be used to set the configuration parameters for a
run. This is broader than sweep_config which just sets the sweep
profile. This window allows the user the select the sweep profile and
set a bunch of other parameters as well.
"""

from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from embeds.methodPlot import MethodPlot
from devices.supportedDevices import devices

from functools import partial

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import (
    QMainWindow,
    QComboBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QSpinBox,
    QScrollArea,
    QDoubleSpinBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QLineEdit
)

# FOR TESTING ONLY ############
import time 
import sys, os
#####################################

class WindowRunConfig(QMainWindow):
    def __init__(self, parent, mode, run_id=False):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.run_id = run_id
     
        self.saved = True
        self.close_on_save = False
        
        self.status = self.statusBar()
        
        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        v3 = QVBoxLayout()

        method_lbl = QLabel("Method")
        self.method = QComboBox()
        self.method.setPlaceholderText(l.rc_select[g.L])

        for method in self.parent.data[g.S_METHODS]:
            self.method.addItem(method[g.M_NAME], {'type':g.M_FROM_SAMPLE,
                                                   'method': method})
        self.method.currentIndexChanged.connect(self.method_changed)

        but_m_load = QPushButton('load from file')
        but_m_load.clicked.connect(self.open_method_from_file)

        device_lbl = QLabel("Device")
        self.device = QComboBox()
        self.device.setPlaceholderText(l.rc_select[g.L])
        for dev in devices:
            self.device.addItem(dev['name'], dev)
        self.device.currentIndexChanged.connect(self.device_changed)
            
        run_type_lbl = QLabel("Run type")
        #####################
        # editable!
        self.types = [l.rc_type_blank[g.L], l.rc_type_sample[g.L], l.rc_type_stdadd[g.L]]
        #
        #####################
        self.run_type = QComboBox()
        self.run_type.setPlaceholderText(l.rc_select[g.L])  # set placeholder text
        self.run_type.addItems(self.types)                  # add all text in correct language
        for i in range(0, len(self.types)):                 # for each text item:
            self.run_type.setItemData(i, g.R_TYPES[i])      #   link the corresponding label in English for cross-language data storage
        
        self.run_type.currentIndexChanged.connect(self.run_type_changed)

        replicates_lbl = QLabel("Repeats")
        self.replicates = QSpinBox()
        self.replicates.setValue(g.RC_REPS_MIN)
        self.replicates.setMinimum(g.RC_REPS_MIN)
        self.replicates.setMaximum(g.RC_REPS_MAX)
        self.replicates.valueChanged.connect(self.reps_changed)
            
        self.graph = MethodPlot()
        graph_area = QScrollArea()
        graph_area.setObjectName('ov-graph-area')
        graph_area.setWidget(self.graph)

        but_view_method = QPushButton('View method details')
        but_view_method.clicked.connect(self.view_method)

        notes_lbl = QLabel("Notes")
        self.notes = QLineEdit()
        self.notes.textEdited.connect(self.value_changed)
        
        # setup stacked layout for options specific to each run type
        self.type_stack = QStackedLayout(self)
        w_blank = QWidget()

        v_sample = QVBoxLayout()
        self.w_sample_sample_vol = QDoubleSpinBox()
        self.w_sample_total_vol = QDoubleSpinBox()
        w_sample_sample_vol_lbl = QLabel('Sample volume [mL]')
        w_sample_total_vol_lbl = QLabel('Total volume [mL]')
        v_sample.addLayout(horizontalize([w_sample_sample_vol_lbl, self.w_sample_sample_vol],True))
        v_sample.addLayout(horizontalize([w_sample_total_vol_lbl, self.w_sample_total_vol], True))
        g_sample = QGroupBox("Sample parameters")
        g_sample.setLayout(v_sample)

        v_stdadd = QVBoxLayout()
        self.w_stdadd_vol_std = QDoubleSpinBox()
        self.w_stdadd_conc_std = QDoubleSpinBox()
        w_stdadd_vol_std_lbl = QLabel('Volume standard added [mL]')
        w_stdadd_conc_std_lbl = QLabel('Standard concentration [mg/L]')
        v_stdadd.addLayout(horizontalize([w_stdadd_vol_std_lbl, self.w_stdadd_vol_std], True))
        v_stdadd.addLayout(horizontalize([w_stdadd_conc_std_lbl, self.w_stdadd_conc_std], True))
        g_stdadd = QGroupBox("Standard addition parameters")
        g_stdadd.setLayout(v_stdadd)

        ws_in_stack = [self.w_sample_sample_vol,
                       self.w_sample_total_vol,
                       self.w_stdadd_vol_std,
                       self.w_stdadd_conc_std]
        for w in ws_in_stack:
            w.valueChanged.connect(self.value_changed)
               
        self.type_stack.addWidget(w_blank)
        self.type_stack.addWidget(g_sample)
        self.type_stack.addWidget(g_stdadd)

        self.but_new = QPushButton('Ready to run!')
        self.but_edit = QPushButton('Save changes')
        self.but_view = QPushButton('Edit configs')

        self.but_new.clicked.connect(self.run_button_clicked)
        self.but_edit.clicked.connect(self.save_changes)
        self.but_view.clicked.connect(self.set_mode_edit)
        
        self.buts = [self.but_new, self.but_edit, self.but_view]

        # Define which buttons are enabled on which modes
        self.ws_for_new = [self.method, but_m_load, self.device, self.replicates]
        self.ws_for_edit = [self.run_type, self.w_sample_sample_vol, self.w_sample_total_vol,
                             self.w_stdadd_vol_std, self.w_stdadd_conc_std, self.notes]
        self.ws_for_view = [but_view_method]
      
        # add widgets to layouts 
        v1.addWidget(method_lbl)
        v1.addLayout(horizontalize([self.method, but_m_load]))
        v1.addWidget(device_lbl)
        v1.addWidget(self.device)
        v1.addWidget(run_type_lbl)
        v1.addWidget(self.run_type)
        v1.addLayout(self.type_stack)
        v1.addLayout(horizontalize([replicates_lbl, self.replicates], True))
        v1.addLayout(horizontalize([notes_lbl, self.notes]))
        v1.addStretch()

        v2.addWidget(graph_area)
        v2.addWidget(but_view_method)

        h1.addLayout(v2)
        h1.addLayout(v1)
        
        w = QWidget()
        w.setLayout(h1)
        self.setCentralWidget(w)

        # If there is a specific run selected, fill out the form with that run's details
        if run_id:                  
            self.set_form()

        if self.mode == g.WIN_MODE_NEW:
            self.set_mode_new()
            #self.run_id = False             # if there was a run_id entered to preload values for a new run, forget about it now.
        elif self.mode == g.WIN_MODE_EDIT:
            self.set_mode_edit()
        else:
            self.set_mode_view()

        self.saved = True

        
    #########################################
    #                                       #
    #   Window visualization/layout fns     #
    #                                       #
    #   1. reset_form                       #
    #   2. set_form                         #
    #   3. refresh_graph                    #
    #   4. update_win                       #
    #                                       #
    ######################################### 

    def reset_form(self):                                           # resets Run Config window to all blank values
        self.method.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)    # set dropdowns to 'nothing selected'
        self.device.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)
        self.run_type.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)
        self.w_sample_sample_vol.setValue(0)                        # Set all type-dependent values to 0
        self.w_sample_total_vol.setValue(0)
        self.w_stdadd_vol_std.setValue(0)
        self.w_stdadd_conc_std.setValue(0)
        self.replicates.setValue(g.RC_REPS_MIN)                     # set reps to minimum value (1)
        self.notes.setText('')                                      # set notes to an empty string
        self.type_stack.setCurrentIndex(0)                          # set stacked view to the 0th view (blank)
        self.refresh_graph()                                        # refresh the graph pane
        
    def set_form(self):                                             # Sets Run Config window to match values from run with uid
        self.reset_form()
        if self.run_id:
            data = self.parent.data
            run = get_run_from_file_data(data, self.run_id)         # Look for the relevant run, store it if found, else run=False
            if run:                                           
                method = get_method_from_file_data(data, run[g.R_UID_METHOD]) # Look for relevant method, store if found, else method=False
                if method:                                          # If the method is found in the file
                    self.method.setCurrentText(method[g.M_NAME])    # Select that method in the method dropdown
                    self.method_id = method[g.M_UID_SELF]

                self.device.setCurrentText(run[g.R_DEVICE])         # set device menu to value from file
                self.replicates.setValue(len(run[g.R_REPLICATES]))  # set replicates to length of replicate list of run from file
                self.notes.setText(run[g.R_NOTES])                  # set notes to value from file
                

                for i in range(0, self.run_type.count()):           # loop through all the items in the type list            
                    if self.run_type.itemData(i) == run[g.R_TYPE]:  # (list text is in user language) but if list item *data*
                        self.run_type.setCurrentIndex(i)            #   matches the type of run stored in the file, select that
                        self.type_stack.setCurrentIndex(i)          #   entry in both the dropdown list and the following stacked layout
                        break
                                                                    # Then load the data for the relevant section of the stacked layout
                if run[g.R_TYPE] == g.R_TYPE_SAMPLE:                # if this run was the sample
                    self.w_sample_sample_vol.setValue(run[g.R_SAMPLE_VOL])
                    self.w_sample_total_vol.setValue(run[g.R_TOTAL_VOL])
                    
                elif run[g.R_TYPE] == g.R_TYPE_STDADD:              # if this run was the standard addition
                    self.w_stdadd_vol_std.setValue(run[g.R_STD_ADDED_VOL])
                    self.w_stdadd_conc_std.setValue(run[g.R_STD_CONC])
            self.refresh_graph()                                    # refresh the graph pane

    def refresh_graph(self):
        reps = int(self.replicates.value())
        steps = []
        relays = []
        if self.method.currentIndex() != g.QT_NOTHING_SELECTED_INDEX:
            steps = self.method.currentData()['method'][g.M_STEPS]
            relays = self.method.currentData()['method'][g.M_EXT_DEVICES]
        self.graph.update_plot(steps, relays, show_labels=False, reps=reps)

    def update_win(self):
        if self.mode != g.WIN_MODE_NEW:
            self.set_form()

    #########################################
    #                                       #
    #   Handlers for changed widgets        #
    #                                       #
    #   1. method_changed                   #
    #   2. device_changed                   #
    #   3. run_type_changed                 #
    #   4. reps_changed                     #
    #   5. value_changed                    #
    #                                       #
    #########################################

    def method_changed(self, i):
        """Resets flag to indicate that the run config has been modified from
        saved version and refreshes graph."""
        self.saved = False
        self.refresh_graph()

    def device_changed(self):
        """Resets flag to indicate that the run config has been modified from
        saved version."""
        self.saved = False

    def run_type_changed(self, i):
        """Resets flag to indicate that the run config has been modified from
        saved version and toggles stacked layout to appropriate stack."""
        self.saved = False
        self.type_stack.setCurrentIndex(i)

    def reps_changed(self):
        """Resets flag to indicate that the run config has been modified from
        saved version and refreshes graph."""
        self.saved = False
        self.refresh_graph()

    def value_changed(self):
        """Generic hanlder: Resets flag to indicate that the run config has
        been modified from saved version."""
        self.saved = False


    #########################################
    #                                       #
    #   Method-related functions            #
    #                                       #
    #   1. open_method_from_file            #
    #   2. view_method                      #
    #                                       #
    #########################################      

    def open_method_from_file(self):
        path = get_path_from_user(self, 'method')
        if not path:
            return
        data = get_data_from_file(path)
        if len(self.parent.data[g.S_METHODS]) > 0 and len(self.parent.data[g.S_METHODS]) == self.method.count():
            self.method.insertSeparator(self.method.count())
        self.method.addItem(data[g.M_NAME], {'type':g.M_FROM_FILE,
                                            'path': path,
                                            'method': data})
        self.method.setCurrentIndex(self.method.count()-1)
        

    def view_method(self):
        if self.method.currentIndex() != g.QT_NOTHING_SELECTED_INDEX:
            try:
                if self.method.currentData()['type'] == g.M_FROM_SAMPLE:    # if method is from an existing run in sample file
                    method_id = self.method.currentData()['method'][g.M_UID_SELF]
                    self.parent.new_win_method_by_id(g.WIN_MODE_VIEW_ONLY, method_id, False)
                else:                                                       # if method is from a separatemethod file
                    path = self.method.currentData()['path']
                    self.parent.new_win_method_by_path(g.WIN_MODE_VIEW_ONLY, path, False)
            except Exception as e:
                print(e)
                
            #self.parent.parent.open_config(data=self.method.currentData(), editable=False)

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    ######################3 HERE ######################################################


    #########################################
    #                                       #
    #   Saving and validation               #
    #                                       #
    #   1. run_button_clicked               #
    #   2. validate_form                    #
    #   3. method_and_device_compatible     #
    #   4. save_method                      #
    #       5. after_save_method_success    #
    #       6. after_save_method_error      #
    #   7. save_config                      #
    #       8. after_save_config_success    #
    #       9. after_save_config_error      #
    #   10. save_changes                    #
    #       11. after_save_changes_success  #
    #       12. after_save_changes_error    #
    #   13. run_runs                        #
    #                                       #
    #########################################
        
    def run_button_clicked(self):
        if self.parent.process:                 # If parent is running a process (save or load or whatever)
            return                              #   ignore this button click
        form_is_valid = self.validate_form()    # Validate form
        if form_is_valid:   
            self.save_method()                  # Start the save process
                            
    def validate_form(self):
        """ Checks a series of validation criteria on self. If any single criteria is
        not met, an alert is shown to the user and returns False. Thus it only alerts
        user to first criterion that is not met. 
        If all criteria are met, returns True."""
        
        # Make sure all drop down menus have something selected
        if self.method.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
            show_alert(self, l.alert_header[g.L], 'please select a sweep profile to proceed.')
            return False

        elif self.device.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
            show_alert(self, l.alert_header[g.L], 'please select a device to proceed.')
            return False

        if not self.method_and_device_compatible():
            return False

        elif self.run_type.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
            show_alert(self, l.alert_header[g.L], 'please select a run type to proceed.')
            return False

        # If relevant, validate the parameters specific to the "sample" type run
        if self.run_type.currentText() == l.rc_type_sample[g.L]:
            vol_sample = self.w_sample_sample_vol.value()
            vol_total = self.w_sample_total_vol.value()
            if (vol_sample == float(0) or vol_total == float(0)):
                show_alert(self, l.alert_header[g.L], 'Neither the sample nor total volume can be 0. Please check the sample parameters.')
                return False
            elif (vol_sample > vol_total):
                show_alert(self, l.alert_header[g.L], 'The sample volume cannot be larger than the total volume. Please check the sample parameters.')
                return False
            
        # If relevant, validate the parameters specific to the "standard-addition" type run
        if self.run_type.currentText() == l.rc_type_stdadd[g.L]:
            vol_add = self.w_stdadd_vol_std.value()
            conc = self.w_stdadd_conc_std.value()
            if vol_add == float(0):
                show_alert(self, l.alert_header[g.L], 'You probably added some standard. Please check the standard addition parameters.')
                return False
            elif conc == float(0):
                show_alert(self, l.alert_header[g.L], 'The concentration of the standard is probably not 0. Please check the standard addition parameters.')
                return False

        return True

    def method_and_device_compatible(self):

        # Check whether selected device has enough general purpose input output pins for this method
        if len(self.device.currentData()['gpio']) < len(self.method.currentData()['method'][g.M_EXT_DEVICES]):
            show_alert(self, l.alert_header[g.L], 'This device does not have enough input/output pins to control all the external devices in that method.\nPlease try either another device or another method.')
            return False
        
        ###############################################
        #
        # THIS IS WHERE WE VALIDATE WHETHER THE DEVICE IS COMPATIBLE WITH THE METHOD
        #
        #       BUILD THIS!!
        #       Check:
        #           - Max V
        #           - Current range?
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #####################################################
        return True
        

    def save_method(self):

        # grab the most up to date version of the sample data 
        data = self.parent.data
        method_new = self.method.currentData()['method']

        # if this method is already in the file
        for method in data[g.S_METHODS]:                
            if methods_match(method, method_new):       
                self.method_id = method[g.R_UID_SELF]   # grab the id of the stored version and return
                self.status.showMessage('Method saved.', g.SB_DURATION)
                self.save_config()
                return

        # if this is a brand new method for this sample                                                              
        ids = get_ids(data, g.S_METHODS)                    # get existing method uids      
        self.method_id = get_next_id(ids, g.M_UID_PREFIX)   # generate the next method uid
        method_new[g.M_UID_SELF] = self.method_id           # add that new method uid to this current sweep proile        
        data[g.S_METHODS].append(method_new)                # append the new sweep profile to the old data
        #write_data_to_file(self.parent.path, data)          # write the data back to the file!

        self.status.showMessage('Saving method...')
        self.parent.start_async_save(g.SAVE_TYPE_METHOD_TO_SAMPLE, [method_new], onSuccess=self.after_save_method_success, onError=self.after_save_method_error)
   
    def after_save_method_success(self):
        print('method save SUCCESS')
        self.status.showMessage('Method saved.', g.SB_DURATION)
        self.save_config()
        
    def after_save_method_error(self):
        print('method save ERROR')
        self.status.showMessage('ERROR on method save.', g.SB_DURATION_ERROR)       

    def save_config(self):
        self.set_run_id()                       # make sure the correct run id is set 
        new_data = self.get_config_data_dict()  # get data dict without reps
        reps = self.get_replicate_list()        # get reps as a list
        new_data[g.R_REPLICATES] = reps         # add reps list as value to data dict

        print(new_data)
        # Then start the save!   
        self.status.showMessage('Saving run configuration...')
        self.parent.start_async_save(g.SAVE_TYPE_RUN_NEW, [new_data], onSuccess=self.after_save_config_success, onError=self.after_save_config_error)
        print('ASYNC SAVER LAUNCHED!')
        
    def after_save_config_success(self):
        print('AFTERSHAVE SUCCESS!')
        self.status.showMessage('Run configuration saved.', g.SB_DURATION)
        self.saved = True
        self.run_runs()
           
    def after_save_config_error(self):
        print('AFTERSHAVE eRr0rrr!')
        self.status.showMessage('ERROR: Changes were not saved.', g.SB_DURATION_ERROR)

    def save_changes(self):
        if self.parent.process:                     # If there is an ongoing parent process (save, load, run, etc.)
            return                                  #   do nothing (ignore button press)
        elif self.saved:                            # If there are no changes to save
            self.after_save_changes_success()       #   run all-changes-saved routine
            return                                  #   and otherwise do nothing
        form_is_valid = self.validate_form()        # If there are changes to save, validate form
        if form_is_valid:                           # If form is valid:
            new_data = self.get_config_data_dict()  #   get data dict without reps and save
            self.status.showMessage('Saving run configuration...')
            self.parent.start_async_save(g.SAVE_TYPE_RUN_MOD, [self.run_id, new_data], onSuccess=self.after_save_changes_success, onError=self.after_save_changes_error)

    def after_save_changes_success(self):
        self.status.showMessage('All changes saved.', g.SB_DURATION)
        self.saved = True
        if self.close_on_save:
            self.close()
        else:
            self.set_mode_view()
           
    def after_save_changes_error(self):
        self.status.showMessage('ERROR: Changes were not saved.', g.SB_DURATION_ERROR)
        self.close_on_save = False

    def run_runs(self):
        tasks = []
        for run in self.parent.data[g.S_RUNS]:
            if run[g.R_UID_SELF] == self.run_id:
                for rep in run[g.R_REPLICATES]:
                    tasks.append((self.run_id, rep[g.R_UID_SELF]))
                break
        self.close()
        self.parent.new_win_view_run(tasks)


    #########################################
    #                                       #
    #   Data preparation functions          #
    #                                       #
    #   1. set_run_id                       #
    #   2. get_config_data_dict             #
    #   3. get_replicate_list               # 
    #                                       #
    #########################################

    def set_run_id(self):
        if self.mode == g.WIN_MODE_NEW:                              # If this is a new run:
            data = self.parent.data                                 #   from up to date data:
            run_ids = get_ids(data, g.S_RUNS)                       #   grab all previous IDs
            self.run_id = get_next_id(run_ids, g.R_RUN_UID_PREFIX)  #   and find the next ID
            
    def get_config_data_dict(self):
        try:
            run = {}    
                
            run[g.R_UID_SELF] = self.run_id
            if self.mode == g.WIN_MODE_NEW:                 # only store time created if this is a new config
                run[g.R_TIMESTAMP] = QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)
            run[g.R_UID_METHOD] = self.method_id
            run[g.R_DEVICE] = self.device.currentText()
            run[g.R_NOTES] = self.notes.text()              

            run_type = self.run_type.currentData()          # Get the current run type
            run[g.R_TYPE] = run_type                        # Add current run type to dict
            
            if run_type == g.R_TYPE_SAMPLE:                 # If its a sample run, add the relevant parameters   
                run[g.R_SAMPLE_VOL] = self.w_sample_sample_vol.value()
                run[g.R_TOTAL_VOL] = self.w_sample_total_vol.value()
            elif run_type == g.R_TYPE_STDADD:               # If its a standard addition run, add the relevant parameters 
                run[g.R_STD_ADDED_VOL] = self.w_stdadd_vol_std.value()
                run[g.R_STD_CONC] = self.w_stdadd_conc_std.value()
                
            return run
        except Exception as e:
            print(e)

    def get_replicate_list(self):
        reps = []
        for i in range(0, self.replicates.value()):
            uid_rep = g.R_REPLICATE_UID_PREFIX+str(i)
            rep = {g.R_UID_SELF: uid_rep,
                   g.R_STATUS: g.R_STATUS_PENDING,
                   g.R_TIMESTAMP_REP: '',
                   g.R_NOTES: '',
                   g.R_DATA: [],
                   g.R_BACKGROUND: []
                   }
            reps.append(rep)
        return reps


    #########################################
    #                                       #
    #   Mode change functions               #
    #                                       #
    #   1. set_mode_new                     #
    #   2. set_mode_edit                    # 
    #   3. set_mode_view                    #
    #   4. toggle_widget_editability        #
    #   5. set_button_bar                   #
    #                                       #
    #########################################
    
    def set_mode_new(self):
        """Sets window mode to that of a new run configuration"""
        self.mode = g.WIN_MODE_NEW                      # Set the mode flag
        self.toggle_widget_editability()                # enable the appropriate widgets for this mode
        self.set_button_bar(self.but_new)               # Make sure the button specific to this mode is visible
        self.setWindowTitle("Run configuration | New")  # Set the window title to indicate current mode

    def set_mode_edit(self):
        """Sets window mode to editing the configuration of an already-completed run"""
        self.mode = g.WIN_MODE_EDIT                     
        self.toggle_widget_editability()
        self.set_button_bar(self.but_edit)
        self.setWindowTitle("Run configuration | Edit")  

    def set_mode_view(self):
        """Sets window mode to viewing the configuration of an already-completed run"""
        self.mode = g.WIN_MODE_VIEW_ONLY
        self.toggle_widget_editability()
        self.set_button_bar(self.but_view)
        self.setWindowTitle("Run configuration | View")

    def toggle_widget_editability(self):
        """Depending on the current mode, enables/greys-out certain widgets"""
        if self.mode == g.WIN_MODE_NEW:
            to_enable = self.ws_for_new + self.ws_for_edit + self.ws_for_view
            to_not = []
        elif self.mode == g.WIN_MODE_EDIT:
            to_enable = self.ws_for_edit + self.ws_for_view
            to_not = self.ws_for_new
        else:
            to_enable = self.ws_for_view
            to_not = self.ws_for_edit + self.ws_for_new
        for w in to_enable:
            w.setEnabled(True)
        for w in to_not:
            w.setEnabled(False)
    
    def set_button_bar(self, button):
        """Takes in a button widget. Removes all removable buttons from layout, then adds
        button back in at the appropriate spot"""
        for but in self.buts:
            but.setParent(None)
        self.centralWidget().layout().children()[-1].addWidget(button) # Add button to end of right-column layout
   
        
    #########################################
    #                                       #
    #   Window show/hide event handlers     #
    #                                       #
    #   1. showEvent                        #
    #   2. closeEvent                       # 
    #   3. accept_close                     #
    #                                       #
    #########################################

    def showEvent(self, event):
        try:
            if not self.mode == g.WIN_MODE_VIEW_ONLY:
                self.parent.setEnabled(False)
                self.parent.set_enabled_children(False)
                self.setEnabled(True)
            event.accept()
        except Exception as e:
            print(e)
        
    def closeEvent(self, event):
        if not self.saved and self.mode == g.WIN_MODE_EDIT:
            confirm = saveMessageBox(self)
            resp = confirm.exec()
            if resp == QMessageBox.StandardButton.Save:
                event.ignore()
                self.close_on_save = True
                self.save_changes()
            elif resp == QMessageBox.StandardButton.Discard:
                self.accept_close(event)
            else:
                event.ignore()  
        else:
            self.accept_close(event)                     

    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.parent.children.remove(self)
        closeEvent.accept()
