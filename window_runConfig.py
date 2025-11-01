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

from json import dumps, loads

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
    def __init__(self, parent, uid=False):
        super().__init__()
        
        print(parent.path)
        self.parent = parent
        self.setWindowTitle(l.rc_window_title[g.L])
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.run_to_run = False
        self.reps_to_run = []
            
        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
            
        run_type_lbl = QLabel("Run type")
            

        #####################
        # editable!
        self.types = [l.rc_type_blank[g.L], l.rc_type_sample[g.L], l.rc_type_stdadd[g.L]]
        self.run_type = QComboBox()
        self.run_type.addItems(self.types)
        self.run_type.setItemData(0, g.R_RUN_TYPE_BLANK)
        self.run_type.setItemData(1, g.R_RUN_TYPE_SAMPLE)
        self.run_type.setItemData(2, g.R_RUN_TYPE_STDADD)
        #
        #####################
        self.run_type.setPlaceholderText(l.rc_select[g.L])
        self.run_type.currentIndexChanged.connect(self.run_type_changed)

        sweep_prof_lbl = QLabel("Sweep profile")
            
        ###############3 THIS IS A PLACEHOLDER, READ THESE IN AT INIT
        ############### AND UPDATE THIS LIST IF A NEW ONE IS ADDED
        self.sps = ['sp0', 'my favorite sp1', 'ooops sp2']
        #
        #   These Sweep profiles are two types:
        #       - Those loaded in from .ovc (OV config) files   (data is path)
        #       - Those loaded from already in this sample      (data is uid of sweep in this file)
        ##########################################################
        
        self.sweep_profile = QComboBox()
        self.sweep_profile.setPlaceholderText(l.rc_select[g.L])
        self.sweep_profile.addItems(self.sps)
        self.sweep_profile.currentIndexChanged.connect(self.sweep_profile_changed)

        but_sp_load = QPushButton('load from file')
        but_sp_load.clicked.connect(self.open_sp_from_file)

        replicates_lbl = QLabel("Repeats")
        self.replicates = QSpinBox()
        self.replicates.setValue(g.RC_REPS_MIN)
        self.replicates.setMinimum(g.RC_REPS_MIN)
        self.replicates.setMaximum(g.RC_REPS_MAX)
            

        self.graph_area = QScrollArea()

        notes_lbl = QLabel("Notes")
        self.notes = QLineEdit()
        

        # setup stacked layout for options specific to each run type
        self.type_stack = QStackedLayout(self)
        w_blank = QWidget()

        f_sample = QFormLayout()
        self.w_sample_sample_vol = QDoubleSpinBox()
        self.w_sample_total_vol = QDoubleSpinBox()
        f_sample.addRow('Sample volume [mL]', self.w_sample_sample_vol)
        f_sample.addRow('Total volume [mL]', self.w_sample_total_vol)
        g_sample = QGroupBox("Sample parameters")
        g_sample.setLayout(f_sample)

        f_stdadd = QFormLayout()
        self.w_stdadd_vol_std = QDoubleSpinBox()
        self.w_stdadd_conc_std = QDoubleSpinBox()
        f_stdadd.addRow('Volume standard added [mL]', self.w_stdadd_vol_std)
        f_stdadd.addRow('Standard concentration [mg/L]', self.w_stdadd_conc_std)
        g_stdadd = QGroupBox("Standard addition parameters")
        g_stdadd.setLayout(f_stdadd)
               
        self.type_stack.addWidget(w_blank)
        self.type_stack.addWidget(g_sample)
        self.type_stack.addWidget(g_stdadd)

        but_run = QPushButton('Begin run!')
        but_run.clicked.connect(self.run_button_clicked)

        # add widgets to layouts 
        v1.addWidget(run_type_lbl)
        v1.addWidget(self.run_type)
        v1.addWidget(sweep_prof_lbl)
        v1.addLayout(horizontalize([self.sweep_profile, but_sp_load]))
        v1.addStretch()
        v1.addLayout(horizontalize([replicates_lbl, self.replicates]))

        h1.addLayout(v1)
        h1.addWidget(self.graph_area)
    
        v2.addLayout(h1)
        v2.addLayout(self.type_stack)
        v2.addLayout(horizontalize([notes_lbl, self.notes]))
        v2.addStretch()
        v2.addWidget(but_run)

        if uid:
            i = -1
            data = get_data_from_file(self.parent.path)
            for j, run in enumerate(data[g.S_RUNS]):
                if run[g.R_UID_SELF] == uid:
                    i = j

            if i == -1:
                show_alert(self, "eeeeek", "there is no run that matches!")
            else:
                show_alert(self, 'success!', 'legooooo')
                    
               
                #####################################
                #
                #   FILL THIS OUT!!!
                #
                #   This is where we load the form with
                #   the config values from the run with
                #   the passed uid. 

            pass
            

        
        w = QWidget()
        w.setLayout(v2)
        self.setCentralWidget(w)

    def run_type_changed(self, i):
        self.type_stack.setCurrentIndex(i)

    def sweep_profile_changed(self, i):
        return
        #
        # THIS IS WHERE WE GRAPH THINGSSS

    def open_sp_from_file(self):
        print('we are now allowing a user to select an sp from the file!')
        
    def run_button_clicked(self):
        try:
            form_is_valid = self.validate_form()    # Validate form
            if form_is_valid:   
                self.save_sweep_profile()   # Save the sweep profile
                self.save_run_configs()    # Save the configs for the run

                print(self.run_to_run)
                print(self.reps_to_run)
                self.run_runs()
                                                    # start running the runs!
        except Exception as e:
            print(e)


    def validate_form(self):
    
        if self.run_type.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
            show_alert(self, l.alert_header[g.L], 'please select a run type to proceed.')
            return False

        elif self.sweep_profile.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
            show_alert(self, l.alert_header[g.L], 'please select a sweep profile to proceed.')
            return False
            
        if self.run_type.currentText() == l.rc_type_sample[g.L]:
            vol_sample = self.w_sample_sample_vol.value()
            vol_total = self.w_sample_total_vol.value()
            if (vol_sample == float(0) or vol_total == float(0)):
                show_alert(self, l.alert_header[g.L], 'Neither the sample nor total volume can be 0. Please check the sample parameters.')
                return False
            elif (vol_sample > vol_total):
                show_alert(self, l.alert_header[g.L], 'The sample volume cannot be larger than the total volume. Please check the sample parameters.')
                return False

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

    def save_sweep_profile(self):
        # Get the selected sweep profile
        #######################
        #
        # THIS IS A PLACEHOLDER TILL WE GET THE SWEEP PROFILE GENERATOR WORKING
        sp_new = {g.SP_NOTES: self.sweep_profile.currentText()}
        #
        #######################
        # grab the most up to date version of the sample data from file
        data = get_data_from_file(self.parent.path)

        sp_id = False
        for sp in data[g.S_SWEEP_PROFILES]:
            if sweep_profiles_match(sp, sp_new):
                sp_id = sp[g.R_UID_SELF]

        if not sp_id:                                       # if this is a brand new sweep profie for this sample
                                                            # Generate a new sweep id + add it to the data
            ids = get_ids(data, g.S_SWEEP_PROFILES)             # get existing sp uids      
            sp_id = get_next_id(ids, g.SP_UID_PREFIX)           # generate the next sp uid
            sp_new[g.SP_UID_SELF] = sp_id                       # add that new sp uid to this current sweep proile
            data[g.S_SWEEP_PROFILES].append(sp_new)             # append the new sweep profile to the old data
            write_data_to_file(self.parent.path, data)          # write the data back to the file! 
            
        self.sp_id = sp_id   

        
                
        
        

    def save_run_configs(self):
        try:
            # grab the most up to date version of the sample data from file
            data = get_data_from_file(self.parent.path)

            # Create dictionary from new run configs entered by user
            new_data = {}
            #######################
            #
            # THIS IS A PLACEHOLDER TILL WE GET THE SWEEP PROFILE GENERATOR WORKING
            new_data[g.R_UID_SP] = self.sp_id
            #
            #######################

            run_type = self.run_type.currentData()
            new_data[g.R_TYPE] = run_type
            new_data[g.R_NOTES] = self.notes.text()
            if run_type == g.R_RUN_TYPE_SAMPLE:
                new_data[g.R_SAMPLE_VOL] = self.w_sample_sample_vol.value()
                new_data[g.R_TOTAL_VOL] = self.w_sample_total_vol.value()
            elif run_type == g.R_RUN_TYPE_STDADD:
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
        return

    
            
            

    

    ############################################################################
        
