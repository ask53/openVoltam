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

class WindowRunConfig(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        
        self.parent = parent
        self.parent.load_sample_info()                              # make sure data in parent is up-to-date
        self.setWindowTitle(l.rc_window_title[g.L])
        self.run_to_run = False
        self.reps_to_run = []
        self.valid = False
            
        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        v3 = QVBoxLayout()

        method_lbl = QLabel("Method")
        self.method = QComboBox()
        self.method.setPlaceholderText(l.rc_select[g.L])
        for method in parent.data[g.S_METHODS]:
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

        but_run = QPushButton('Ready to run!')
        but_run.clicked.connect(self.run_button_clicked)

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
    
        v3.addLayout(h1)
        v3.addWidget(but_run)
        
        w = QWidget()
        w.setLayout(v3)
        self.setCentralWidget(w)

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

    def set_form(self, uid):                                        # Sets Run Config window to match values from run with uid
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

            self.refresh_graph()                                # refresh the graph pane

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
                self.save_run_configs()     # Save the configs for the run
                self.run_runs()
                                                    # start running the runs!
        except Exception as e:
            print(e)


    def validate_form(self):
        ########## FOR TESTING, DELETE TO RUN ####################################
        self.valid = True
        return True
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

        self.valid = True    
        return True

    def method_and_device_compatible(self):
        ###############################################
        #
        # THIS IS WHERE WE VALIDATE WHETHER THE DEVICE IS COMPATIBLE WITH THE METHOD
        #
        #####################################################
        return True
        

    def save_method(self):

        # grab the most up to date version of the sample data from file
        data = get_data_from_file(self.parent.path)
        method_id = False

        if self.valid:
            method_new = self.method.currentData()
            
            for method in data[g.S_METHODS]:
                if methods_match(method, method_new):
                    method_id = method[g.R_UID_SELF]
                    break
            
            if not method_id:                                   # if this is a brand new method for this sample
                                                                        # Generate a new method id + add it to the data
                    ids = get_ids(data, g.S_METHODS)                # get existing method uids      
                    method_id = get_next_id(ids, g.M_UID_PREFIX)   # generate the next method uid
                    try:
                        method_new[g.M_UID_SELF] = method_id           # add that new method uid to this current sweep proile
                    except Exception as e:
                        print(e)

                    data[g.S_METHODS].append(method_new)            # append the new sweep profile to the old data
                    write_data_to_file(self.parent.path, data)      # write the data back to the file!
            
                
            self.method_id = method_id   

        
                
        
        

    def save_run_configs(self):
        try:
            # grab the most up to date version of the sample data from file
            data = get_data_from_file(self.parent.path)

            # Create dictionary from new run configs entered by user
            new_data = {}

            new_data[g.R_UID_METHOD] = self.method_id
            new_data[g.R_DEVICE] = self.device.currentText()
            run_type = self.run_type.currentData()
            new_data[g.R_TYPE] = run_type
            new_data[g.R_NOTES] = self.notes.text()
            if run_type == g.R_TYPE_SAMPLE:
                new_data[g.R_SAMPLE_VOL] = self.w_sample_sample_vol.value()
                new_data[g.R_TOTAL_VOL] = self.w_sample_total_vol.value()
            elif run_type == g.R_TYPE_STDADD:
                new_data[g.R_STD_ADDED_VOL] = self.w_stdadd_vol_std.value()
                new_data[g.R_STD_CONC] = self.w_stdadd_conc_std.value()
        
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
            data[g.S_RUNS].append(new_data)

            # Then write the data back to file
            write_data_to_file(self.parent.path, data)
            
  
        except Exception as e:
            #show_alert(self, l.alert_header[g.L], 'Saving the run config produced the following error:\n'+e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
            
        


    def run_runs(self):
        self.close()
        self.parent.start_run(self.run_to_run)

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
        self.parent.setEnabled(False)
        self.parent.setEnabledChildren(False)
        self.setEnabled(True)
        event.accept()
        
    def closeEvent(self, event):
        self.parent.setEnabled(True)
        self.parent.setEnabledChildren(True)
        self.parent.load_sample_info()
        event.accept()

    
            
            

    

    ############################################################################
        
