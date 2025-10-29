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
    QFormLayout
)

class WindowRunConfig(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        try:
            print(parent.path)

            self.setWindowTitle(l.rc_window_title[g.L])
            self.setWindowModality(Qt.WindowModality.ApplicationModal)

            self.types = [l.rc_type_blank[g.L], l.rc_type_sample[g.L], l.rc_type_stdadd[g.L]]
            
            v1 = QVBoxLayout()
            h1 = QHBoxLayout()
            v2 = QVBoxLayout()
            
            run_type_lbl = QLabel("Run type")
            self.run_type = QComboBox()
            self.run_type.setPlaceholderText(l.rc_select[g.L])
            self.run_type.addItems(self.types)
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


            

            # setup stacked layout for options specific to each run type
            self.type_stack = QStackedLayout()
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
            
                               
            
            w_stdadd = QLabel('you selected standard addition!')

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
            v2.addLayout(self.type_stack)
            v2.addStretch()
            v2.addWidget(but_run)

        
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
    #       1. Validate form
    #       2. Save run configs to file
    #       3. Save info in memory to run runs
    #       4. Run the run(s)!
    #       5. (Make sure the QDoubleSpinBoxes handle decimals well)
        
    def run_button_clicked(self):
        form_is_valid = self.validate_form()    # Validate form
        if form_is_valid:   
            self.save_run_configs()             # Save the configs for all runs 
                                                # start running the runs!
            
        return

    def validate_form(self):
        return False

    def save_run_configs(self):
        return

    def run_runs(self):
        return

    ############################################################################
        
