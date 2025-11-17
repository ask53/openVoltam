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
    def __init__(self, parent, uid=False):
        super().__init__()
        
        self.parent = parent
        self.parent.load_sample_info()                              # make sure data in parent is up-to-date
        self.setWindowTitle(l.rc_window_title[g.L])
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.run_to_run = False
        self.reps_to_run = []
            
        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        v3 = QVBoxLayout()
            
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

        method_lbl = QLabel("Method")
        self.method = QComboBox()
        self.method.setPlaceholderText(l.rc_select[g.L])
        for method in parent.data[g.S_METHODS]:
            self.method.addItem(method[g.SP_NOTES], method)
        self.method.currentIndexChanged.connect(self.method_changed)

        but_m_load = QPushButton('load from file')
        but_m_load.clicked.connect(self.open_method_from_file)

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

        but_view_method = QPushButton('Method details')

        ######################### HERE ######################
        #
        #
        #   Figure out how to view method details if method:
        #       a. comes from a file (this is easy, just load from path)
        #       b. comes from the .osv file (this is harder, have to pass data array.)

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

        but_run = QPushButton('Begin run!')
        but_run.clicked.connect(self.run_button_clicked)

        # add widgets to layouts 
        v1.addWidget(run_type_lbl)
        v1.addWidget(self.run_type)
        v1.addWidget(method_lbl)
        v1.addLayout(horizontalize([self.method, but_m_load]))
        v1.addLayout(self.type_stack)
        v1.addLayout(horizontalize([replicates_lbl, self.replicates], True))
        v1.addLayout(horizontalize([notes_lbl, self.notes]))
        v1.addStretch()
        

        v2.addWidget(graph_area)
        v2.addWidget(but_view_method)
        v2.addStretch()

        h1.addLayout(v2)
        h1.addLayout(v1)
    
        v3.addLayout(h1)
        v3.addWidget(but_run)

        if uid:
            i = -1
            data = self.parent.data
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
        w.setLayout(v3)
        self.setCentralWidget(w)

    def run_type_changed(self, i):
        self.type_stack.setCurrentIndex(i)

    def method_changed(self, i):
        print(self.method.currentData())
        self.refresh_graph()
        

    def open_method_from_file(self):
        path = get_path_from_user('method')
        data = get_data_from_file(path)
        try:
            if len(self.parent.data[g.S_METHODS]) > 0 and len(self.parent.data[g.S_METHODS]) == self.method.count():
                self.method.insertSeparator(self.method.count())
            self.method.addItem(data[g.SP_SP_NAME], data)
            self.method.setCurrentIndex(self.method.count()-1)
        except Exception as e:
            print(e)
        
        print('---')
        print(data)
        print('---')
        
    def run_button_clicked(self):
        try:
            form_is_valid = self.validate_form()    # Validate form
            if form_is_valid:   
                self.save_method()   # Save the sweep profile
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

        elif self.method.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:
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

    def save_method(self):
        # Get the selected sweep profile
        #######################
        #
        # THIS IS A PLACEHOLDER TILL WE GET THE SWEEP PROFILE GENERATOR WORKING
        sp_new = {g.SP_NOTES: self.method.currentText()}
        #
        #######################
        # grab the most up to date version of the sample data from file
        data = get_data_from_file(self.parent.path)

        sp_id = False
        for sp in data[g.S_METHODS]:
            if methods_match(sp, sp_new):
                sp_id = sp[g.R_UID_SELF]

        if not sp_id:                                       # if this is a brand new sweep profie for this sample
                                                            # Generate a new sweep id + add it to the data
            ids = get_ids(data, g.S_METHODS)                # get existing sp uids      
            sp_id = get_next_id(ids, g.SP_UID_PREFIX)           # generate the next sp uid
            sp_new[g.SP_UID_SELF] = sp_id                       # add that new sp uid to this current sweep proile
            data[g.S_METHODS].append(sp_new)                    # append the new sweep profile to the old data
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

    def refresh_graph(self):
        if self.method.currentIndex() != g.QT_NOTHING_SELECTED_INDEX:
            reps = int(self.replicates.value())
            self.graph.update_plot(self.method.currentData()[g.SP_STEPS], show_labels=False, reps=reps)

    
            
            

    

    ############################################################################
        
