"""
window_runConfig.py

This file defines a class WindowRunConfig which creates a window
object that can be used to set the configuration parameters for a
run. This is broader than sweep_config which just sets the sweep
profile. This window allows the user the select the sweep profile and
set a bunch of other parameters as well.
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from json import dumps, loads

from PyQt6.QtCore import Qt
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
        try:
            print(parent.path)
            self.parent = parent
            self.setWindowTitle(l.rc_window_title[g.L])
            self.setWindowModality(Qt.WindowModality.ApplicationModal)

            
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
            ##########################################################
            
            self.sweep_profile = QComboBox()
            self.sweep_profile.setPlaceholderText(l.rc_select[g.L])
            self.sweep_profile.addItems(self.sps)
            self.sweep_profile.currentIndexChanged.connect(self.sweep_profile_changed)

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
            
                               
            
            #w_stdadd = QLabel('you selected standard addition!')
            
            self.type_stack.addWidget(w_blank)
            self.type_stack.addWidget(g_sample)
            self.type_stack.addWidget(g_stdadd)
            


            but_run = QPushButton('Begin run!')
            but_run.clicked.connect(self.run_button_clicked)

            # add widgets to layouts 
            v1.addWidget(run_type_lbl)
            v1.addWidget(self.run_type)
            v1.addWidget(sweep_prof_lbl)
            v1.addWidget(self.sweep_profile)
            v1.addStretch()
            v1.addLayout(horizontalize([replicates_lbl, self.replicates]))

            h1.addLayout(v1)
            h1.addWidget(self.graph_area)
            
            v2.addLayout(h1)
            v2.addLayout(horizontalize([notes_lbl, self.notes]))
            v2.addStretch()
            v2.addLayout(self.type_stack)
            v2.addStretch()
            v2.addWidget(but_run)

            if uid:
               
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
        except Exception as e:
            print(e)

    def run_type_changed(self, i):
        self.type_stack.setCurrentIndex(i)

    def sweep_profile_changed(self, i):
        print(self.sps[i])

    #####################################################################
    #
    #
    #   HERE
    #
    #       2. Save run configs to file (***Next step*** save run placeholder, see below)
    #       3. Save info in memory to run runs
    #       4. Run the run(s)!
    #       5. (Make sure the QDoubleSpinBoxes handle decimals well)
        
    def run_button_clicked(self):
        try:
            form_is_valid = self.validate_form()    # Validate form
            if form_is_valid:   
                saved = self.save_run_configs()     # Save the configs for all runs
                if saved:
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

    def save_run_configs(self):
        try:
            # grab the most up to date version of the sample data from file
            data = False
            with open(self.parent.path, 'r') as file:
                content = file.read()
                data = loads(content)

            # Create dictionary from new run configs entered by user
            new_data = {}
            #######################
            #
            # THIS IS A PLACEHOLDER TILL WE GET THE SWEEP PROFILE GENERATOR WORKING
            new_data[g.R_UID_SP] = self.sweep_profile.currentText()
            #
            #######################

            run_type = self.run_type.currentData()
            new_data[g.R_TYPE] = run_type
            new_data[g.R_NOTES] = self.notes.text()
            if run_type == g.R_RUN_TYPE_SAMPLE:
                print('here!')
                new_data[g.R_SAMPLE_VOL] = self.w_sample_sample_vol.value()
                new_data[g.R_TOTAL_VOL] = self.w_sample_total_vol.value()
            elif run_type == g.R_RUN_TYPE_STDADD:
                new_data[g.R_STD_ADDED_VOL] = self.w_stdadd_vol_std.value()
                new_data[g.R_STD_CONC] = self.w_stdadd_conc_std.value()
        
            # Check whether this new run configuration already exists
            match = False
            run_ids = []
            for i, run in enumerate(data[g.S_RUN_CONFIGS]):
                run_ids.append(run[g.R_UID_SELF])
                if (run[g.R_UID_SP]==new_data[g.R_UID_SP] and run[g.R_TYPE] == new_data[g.R_TYPE] and run[g.R_NOTES] == new_data[g.R_NOTES]):
                    print('here!')
                    if run[g.R_TYPE] == g.R_RUN_TYPE_SAMPLE:
                        if (run[g.R_SAMPLE_VOL] == new_data[g.R_SAMPLE_VOL] and run[g.R_TOTAL_VOL] == new_data[g.R_TOTAL_VOL]):
                            match = True
                            break
                    elif run[g.R_TYPE] == g.R_RUN_TYPE_STDADD:
                        if (run[g.R_STD_ADDED_VOL] == new_data[g.R_STD_ADDED_VOL] and run[g.R_STD_CONC] == new_data[g.R_STD_CONC]):
                            match = True
                            break
                    else:
                        match = True
                        break
            
            
            if match:
                run_id = data[g.S_RUN_CONFIGS][i][g.R_UID_SELF]   
            else:
                run_id = self.get_next_run_id(run_ids)
                new_data[g.R_UID_SELF] = run_id
                data[g.S_RUN_CONFIGS].append(new_data)

            #########
            #
            #   HERE
            #
            #   Add new dicts to "runs" list that point back to the appropriate
            #   run config using the run_id
            #
            ####################################################
           
            with open(self.parent.path, 'w') as file:
                j = dumps(data, indent=4, ensure_ascii=False)   #convert dictionary to json string
                file.write(j)                                   # write json string to file
                file.close()                                    # close the file (to avoid taking up too much memory)
            
            return True
        except Exception as e:
            show_alert(self, l.alert_header[g.L], 'Saving the run config produced the following error:\n'+e)
            return False
            
        
        

    def run_runs(self):
        print('running!')

    def get_next_run_id(self, run_ids):
        """ Takes in a list of run ids, loops through them to find the
        most recent one. Returns the id of the next one, which should be
        one greater than the current. Assumes IDs are of the format:
             [PREFIX]-n
        For example, if the [PREFIX] was 'runz' the first few would be:
        runz-1, runz-2, runz-3, etc.
        """
        max_id = 0
        for ID in run_ids:
            num = int(ID.replace(g.R_RUN_UID_PREFIX,''))
            if num > max_id:
                max_id = num
        return g.R_RUN_UID_PREFIX+str(max_id+1)
            
            

    

    ############################################################################
        
