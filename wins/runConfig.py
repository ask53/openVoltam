"""
window_runConfig.py

This file defines a class WindowRunConfig which creates a window
object that can be used to set the configuration parameters for a
run. This is broader than sweep_config which just sets the sweep
profile. This window allows the user the select the sweep profile and
set a bunch of other parameters as well.
"""

    #####################################################################
    #
    #
    #   TODO
    #       
    #       4. Run the run(s)!
    #       5. (Make sure the QDoubleSpinBoxes handle decimals well)

import ov_globals as g
import ov_lang as l
from ov_functions import *

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

import time # FOR TESTING ONLY
import sys, os

class WindowRunConfig(QMainWindow):
    def __init__(self, parent, mode, run_id=False):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.run_id = run_id
     
        self.setWindowTitle(l.rc_window_title[g.L])
        self.run_to_run = False
        self.reps_to_run = []
        self.status = self.statusBar()
        self.saved = False
            
        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        v3 = QVBoxLayout()

        method_lbl = QLabel("Method")
        self.method = QComboBox()
        self.method.setPlaceholderText(l.rc_select[g.L])

        for method in self.parent.data[g.S_METHODS]:
            self.method.addItem(method[g.M_NAME], method)
        self.method.currentIndexChanged.connect(self.method_changed)

        but_m_load = QPushButton('load from file')
        but_m_load.clicked.connect(self.open_method_from_file)

        device_lbl = QLabel("Device")
        self.device = QComboBox()
        self.device.setPlaceholderText(l.rc_select[g.L])
        for dev in devices:
            self.device.addItem(dev['name'], dev)
            
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
        self.replicates.valueChanged.connect(self.refresh_graph)
            
        self.graph = MethodPlot()
        graph_area = QScrollArea()
        graph_area.setObjectName('ov-graph-area')
        graph_area.setWidget(self.graph)

        but_view_method = QPushButton('View method details')
        but_view_method.clicked.connect(self.view_method)

        notes_lbl = QLabel("Notes")
        self.notes = QLineEdit()
        
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
               
        self.type_stack.addWidget(w_blank)
        self.type_stack.addWidget(g_sample)
        self.type_stack.addWidget(g_stdadd)

        self.but_new = QPushButton('Ready to run!')
        self.but_edit = QPushButton('Save changes')
        self.but_view = QPushButton('Edit configs')

        self.but_new.clicked.connect(self.run_button_clicked)
        self.but_edit.clicked.connect(self.save_changes)
        self.but_view.clicked.connect(self.edit_button_clicked)
        
        self.buts = [self.but_new, self.but_edit, self.but_view]


        ############### SORT THIS OUT FOR TOGGLING BUTTONS AND FIELDS!
        #
        #
        #
        self.ws_to_toggle = {self.run_type, self.w_sample_sample_vol, self.w_sample_total_vol,
                             self.w_stdadd_vol_std, self.w_stdadd_conc_std, self.notes}
        #
        #
        #           AND UPDATE toggle_widget_editability() function as well

        

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

        if run_id:
            self.set_form(run_id)
        

        if self.mode == g.WIN_MODE_NEW:
            self.set_mode_new()
        elif self.mode == g.WIN_MODE_EDIT:
            self.set_mode_edit()
        else:
            self.set_mode_view()
            

        

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

    def set_form(self, uid=False):                                  # Sets Run Config window to match values from run with uid
        self.reset_form()
        if uid:
            self.run_to_run = uid
            data = get_data_from_file(self.parent.path)
            run = get_run_from_file_data(data, uid)                 # Look for the relevant run, store it if found, else run=False
            if run:                                           
                method = get_method_from_file_data(data, run[g.R_UID_METHOD]) # Look for relevant method, store if found, else method=False
                if method:                                          # If the method is found in the file
                    self.method.setCurrentText(method[g.M_NAME])    # Select that method in the method dropdown

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
            if self.mode == g.WIN_MODE_VIEW_ONLY:
                self.setViewOnly()

    def run_type_changed(self, i):
        self.type_stack.setCurrentIndex(i)

    def method_changed(self, i):
        self.refresh_graph()

    def open_method_from_file(self):
        path = get_path_from_user('method')
        data = get_data_from_file(path)
        try:
            if len(self.parent.data[g.S_METHODS]) > 0 and len(self.parent.data[g.S_METHODS]) == self.method.count():
                self.method.insertSeparator(self.method.count())
            self.method.addItem(data[g.M_NAME], data)
            self.method.setCurrentIndex(self.method.count()-1)
        except Exception as e:
            print(e)
        
    def run_button_clicked(self):
        try:
            form_is_valid = self.validate_form()    # Validate form
            if form_is_valid:   
                self.save_method()          # Save the sweep profile
                                                    # start running the runs!
        except Exception as e:
            print(e)


    def validate_form(self):
        ########## FOR TESTING, COMMENT TO RUN ####################################
        #self.valid = True
        #return True
        ###############################################################

        

    
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
        ###############################################
        #
        # THIS IS WHERE WE VALIDATE WHETHER THE DEVICE IS COMPATIBLE WITH THE METHOD
        #
        #       BUILD THIS!!
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
        #####################################################
        return True
        

    def save_method(self):

        # grab the most up to date version of the sample data 
        data = self.parent.data
        method_new = self.method.currentData()

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
        self.status.showMessage('Method saved.', g.SB_DURATION)
        self.save_config()
        
    def after_save_method_error(self):
        self.status.showMessage('ERROR on method save.', g.SB_DURATION_ERROR)       

    def save_config(self):
        try:
            data = self.parent.data

            # Create dictionary from new run configs entered by user
            new_data = {}

            new_data[g.R_UID_METHOD] = self.method_id
            new_data[g.R_DEVICE] = self.device.currentText()
            new_data = self.append_editable_run_info(new_data)
        
            # Get the unique run id for this run
            run_ids = get_ids(data, g.S_RUNS)
            run_id = get_next_id(run_ids, g.R_RUN_UID_PREFIX)
            new_data[g.R_UID_SELF] = run_id
            self.run_to_run = run_id

            # Get the datetime of creation of run
            new_data[g.R_TIMESTAMP] = QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)

            # Create spaces for replicate info and raw data for each replicate
            new_data[g.R_REPLICATES] = []
            for i in range(0, self.replicates.value()):
                uid_rep = g.R_REPLICATE_UID_PREFIX+str(i)
                rep = {g.R_UID_SELF: uid_rep,
                       g.R_STATUS: g.R_STATUS_PENDING,
                       g.R_NOTES: '',
                       g.R_DATA: False
                       }
                new_data[g.R_REPLICATES].append(rep)
                self.reps_to_run.append(uid_rep)

            # Append the new data onto the old dataset
            #data[g.S_RUNS].append(new_data)

            # Then write the data back to file
            #write_data_to_file(self.parent.path, data)
            self.status.showMessage('Saving run configuration...')
            self.parent.start_async_save(g.SAVE_TYPE_RUN_NEW, [new_data], onSuccess=self.after_save_config_success, onError=self.after_save_config_error)
   
        except Exception as e:
            #show_alert(self, l.alert_header[g.L], 'Saving the run config produced the following error:\n'+e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def after_save_config_success(self):
        self.status.showMessage('Run configuration saved.')
        self.run_runs()
        
        
    def after_save_config_error(self):
        self.status.showMessage('ERROR on method save.')       
         
    def run_runs(self):
        self.close()
        self.parent.new_win_view_run(self.run_to_run)

    def set_mode_new(self):
        print('GOTOMODE:new')
        self.mode = g.WIN_MODE_NEW
        self.toggle_widget_editability()
        self.set_button_bar(self.but_new)
        self.setWindowTitle("Run configuration | New")

    def set_mode_edit(self):
        print('GOTOMODE:edit')
        self.mode = g.WIN_MODE_EDIT
        self.toggle_widget_editability()
        self.set_button_bar(self.but_edit)
        self.setWindowTitle("Run configuration | Edit")  

    def set_mode_view(self):
        print('GOTOMODE:view')
        self.mode = g.WIN_MODE_VIEW_ONLY
        self.toggle_widget_editability()
        self.set_button_bar(self.but_view)
        self.setWindowTitle("Run configuration | View")

    def toggle_widget_editability(self):
        return
    
    def set_button_bar(self, button):        
        for but in self.buts:
            but.setParent(None)
        self.centralWidget().layout().children()[-1].addWidget(button)



    
        

    def setViewOnly(self, modifiable=False):
        if self.run_to_run:
            self.view_only_modifiable = modifiable          # set/reset flag
            for w in self.ws_to_toggle:                     # toggle enabled status of buttoms/inputs
                w.setEnabled(modifiable)
            if not modifiable:
                self.but_edit.setText('Edit run info')          # set button text 
                self.setWindowTitle('View | '+self.run_to_run)  # and window title
            else:
                self.but_edit.setText('Save changes')           # set button text
                self.setWindowTitle('Edit | '+self.run_to_run)  # and window title    

    def edit_button_clicked(self):
        if self.view_only_modifiable:
            try:
                form_is_valid = self.validate_form()    # Validate form
                if form_is_valid:
                    self.status.showMessage('saving...')
                    self.save_modified_run_configs()     # Save the configs for the run
                    self.setViewOnly()
                    self.status.showMessage('Saved!', g.SB_DURATION)
            except Exception as e:
                show_alert(self, "Error", "Eek! There was an issue saving the data, please try again.")
                print(e)
        else:
            self.setViewOnly(modifiable=True)


    def save_changes(self):
        data = get_data_from_file(self.parent.path)
        runDict = False
        for run in data[g.S_RUNS]:
            if run[g.R_UID_SELF] == self.run_to_run:
                runDict = run
                break
        if runDict:
            runDict = self.append_editable_run_info(runDict)
            write_data_to_file(self.parent.path, data)

    def append_editable_run_info(self, rDict):
        
        ### IF THERE IS DATA SPECIFIC TO THE RUN TYPE, INDICATE IT HERE: #####
        #
        #
        sample_info = {g.R_SAMPLE_VOL: self.w_sample_sample_vol,
                       g.R_TOTAL_VOL:self.w_sample_total_vol}

        stdadd_info = {g.R_STD_ADDED_VOL: self.w_stdadd_vol_std,
                        g.R_STD_CONC: self.w_stdadd_conc_std}
        #
        #
        ######################################################################

        keys = list(sample_info.keys()) + list(stdadd_info.keys())
        run_type = self.run_type.currentData()          # Get the current run type
        rDict[g.R_TYPE] = run_type                      # Add current run type to dict
        rDict[g.R_NOTES] = self.notes.text()            # Add current note to dict
        
        dict_to_save = None                             # If there are type-specific values to save
        if run_type == g.R_TYPE_SAMPLE:                 # Indicate which ones
            dict_to_save = sample_info
        elif run_type == g.R_TYPE_STDADD:
            dict_to_save = stdadd_info
            
        for key in keys:                                # just in case, remove all                        
            rDict.pop(key, None)                        # key/value pairs for sample and stdadd
        if dict_to_save:                                # if type-specific daa
            for key in dict_to_save:                    # Add the data from the given type
                rDict[key] = dict_to_save[key].value()
        return rDict

   
        

    def refresh_graph(self):
        reps = int(self.replicates.value())
        steps = []
        if self.method.currentIndex() != g.QT_NOTHING_SELECTED_INDEX:
            steps = self.method.currentData()[g.M_STEPS]    
        self.graph.update_plot(steps, show_labels=False, reps=reps)

    def view_method(self):
        if self.method.currentIndex() != g.QT_NOTHING_SELECTED_INDEX:
            self.parent.parent.open_config(data=self.method.currentData(), editable=False)


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
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.accept_close(event)

    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()

    
