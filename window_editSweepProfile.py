"""
window_editSweepProfile.py

This file defines a class WindowEditConfig which creates a window object
that can be used to create a new sweep profile (if blank) or to edit
an existing profile. There are two ways to edit an existing profile because
there are two places a profile may be stored:
    1. In a standalone sweep profile file (with .ovp extention for 'Open Voltam Profile')
    2. Embedded in an Open Voltam sample file (.ovs).
In the first case, this window is passed a path to the .ovp file. If so,
it loads the sweep profile info which can be edited and either saved back to the
same file or Save-as'd to a new file name/location.
In the second case, both the path of the .ovs file as well as the unique ID of
the stored sweep profile is passed. As this is not being imported from a standalone
file, when "save" is pressed, it prompts the user to select a location and name
for the new file.

Both .ovs and .ovp files use tabular json format (an extension of json that allows
for tabular, comma-separated-value type data to be embedded within a json.

"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from window_sample import QVLine

from functools import partial

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QGroupBox,
    QScrollArea,
    QComboBox,
    QTabWidget,
    
    )

class WindowEditSweepProfile(QMainWindow):
    def __init__(self, path=False, uid=False):
        super().__init__()
        self.path = False

        if path:
            self.path = path
        if self.path:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_edit[g.L])
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_new[g.L])

        v1 = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()
        self.g1 = QGroupBox("Add step")
        v4 = QVBoxLayout()
        self.s1 = QStackedLayout()

        v_const = QVBoxLayout()
        v_const_measure = QVBoxLayout()
        g_const_measure = QGroupBox('Data collection')
        v_ramp = QVBoxLayout()
        v_ramp_measure = QVBoxLayout()
        g_ramp_measure = QGroupBox('Data collection')
        
        
        

        self.graph = QScrollArea()
        name_lbl = QLabel('Profile name')
        self.name = QLineEdit()

        step_name_lbl = QLabel('Step name')
        self.step_name = QLineEdit()
        self.step_name.setMaxLength(8)

        self.stirrer = QCheckBox('Stirrer on during step?')
        self.vibrator = QCheckBox('Vibrator on during step?')
        
        step_type_lbl = QLabel('Step type')
        self.step_type = QComboBox()
        self.step_type.setPlaceholderText('Select...')
        self.step_type.addItems(['Constant voltage','Voltage ramp'])
        self.step_type.currentIndexChanged.connect(self.step_type_changed)

        w_const_v_lbl = QLabel('Voltage [V]')
        self.w_const_v = QDoubleSpinBox()
        w_const_t_lbl = QLabel('Duration [s]')
        self.w_const_t = QDoubleSpinBox()
        s1v1g = QGroupBox('Data collection')
        self.const_data_collect_start = QCheckBox('Begin collecting data')
        self.const_data_collect_start.setObjectName('const-collect-start')
        self.const_data_collect_start.stateChanged.connect(partial(self.collection_state_changed,self.const_data_collect_start))
        self.const_data_collect_end = QCheckBox('Stop collecting data')
        const_begin_measure_lbl = QLabel('Begin collection at [s]')
        self.const_begin_measure = QDoubleSpinBox()
        const_end_measure_lbl = QLabel('Stop collection at [s]')
        self.const_end_measure = QDoubleSpinBox()

        ###################################### THIS CODE WORKS, PLEASE MAKE IT READABLE! ################
        bar = QWidget()
        bar.setLayout(horizontalize([const_begin_measure_lbl, self.const_begin_measure]))
        bar.setObjectName('const-collect-start-layout')
        #################################################################################################
        
        v_const_measure.addWidget(self.const_data_collect_start)

        #v_const_measure.addLayout(horizontalize([const_begin_measure_lbl, self.const_begin_measure]))
        v_const_measure.addWidget(bar)

        
        v_const_measure.addWidget(self.const_data_collect_end)
        v_const_measure.addLayout(horizontalize([const_end_measure_lbl, self.const_end_measure]))
        g_const_measure.setLayout(v_const_measure)
        
        

        
        v_const.addLayout(horizontalize([w_const_v_lbl, self.w_const_v]))
        v_const.addLayout(horizontalize([w_const_t_lbl, self.w_const_t]))
        v_const.addWidget(g_const_measure)
        w_const = QWidget()
        w_const.setLayout(v_const)
        
        self.s1.addWidget(QWidget())
        self.s1.addWidget(w_const)
        self.s1.addWidget(QLabel('this is for RAMPS! Yum onionssss'))

        but_add_step = QPushButton('Add')
        but_cancel_step = QPushButton('Cancel')

        but_add_step.clicked.connect(self.add_step)
        but_cancel_step.clicked.connect(self.cancel_step)

        

        
        v4.addLayout(horizontalize([step_name_lbl,self.step_name]))
        v4.addWidget(self.stirrer)
        v4.addWidget(self.vibrator)
        v4.addLayout(horizontalize([step_type_lbl,self.step_type]))
        v4.addLayout(self.s1)
        v4.addLayout(horizontalize([but_add_step, but_cancel_step]))

        
                          
                                
                                
        
        self.g1.setLayout(v4)           
        policy = self.g1.sizePolicy()           # get existing size policy of g1
        policy.setRetainSizeWhenHidden(True)    # modify policy so that g1 takes up space regardless of whether shown or hidden
        self.g1.setSizePolicy(policy)           # set g1's size policy to the modified version.

        self.prof_chart = QScrollArea()

        but_up = QPushButton()
        but_down = QPushButton()
        but_add = QPushButton()
        but_edit = QPushButton()
        but_dup = QPushButton()
        but_del = QPushButton()
        but_up.setIcon(QIcon('external/icons/up.png'))
        but_down.setIcon(QIcon('external/icons/down.png'))
        but_add.setIcon(QIcon('external/icons/add.png'))
        but_edit.setIcon(QIcon('external/icons/edit.png'))
        but_dup.setIcon(QIcon('external/icons/duplicate.png'))
        but_del.setIcon(QIcon('external/icons/trash.png'))
        but_up.setToolTip('Raise')
        but_down.setToolTip('Lower')
        but_add.setToolTip('Add new step')
        but_edit.setToolTip('Edit step')
        but_dup.setToolTip('Duplicate step(s)')
        but_del.setToolTip('Delete step(s)')
        

        but_add.clicked.connect(self.edit_new_step)
        v3.addWidget(self.prof_chart)
        v3.addLayout(horizontalize([but_up, but_down]))
        v3.addLayout(horizontalize([but_add, but_edit, but_dup, but_del]))
        
        h2.addWidget(self.g1)
        h2.addLayout(v3)
        
        w_custom = QWidget()
        w_custom.setLayout(h2)    # update this with custom layout! 
        w_standard = QLabel('nothing here yet...')

        self.builder = QTabWidget()
        self.builder.setTabPosition(QTabWidget.TabPosition.North)
        self.builder.addTab(w_custom, 'custom')
        self.builder.addTab(w_standard, 'standard')

        ############################################################
        
        but_save = QPushButton('Save')

        v2.addWidget(name_lbl)
        v2.addWidget(self.name)
        v2.addStretch()
        
        h1.addLayout(v2)
        h1.addWidget(self.graph)
        
        v1.addLayout(h1)
        v1.addWidget(self.builder)
        v1.addWidget(but_save)
        
        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)

    def step_type_changed(self, i):
        self.s1.setCurrentIndex(i+1) # the +1 allows for the 0th screen
        # to be completely empty, so the nth option in the list
        # correponds to the n+1th widget in the stacked layout.

    def collection_state_changed(self, checkbox, state):
        lay = self.findChild(QWidget, checkbox.objectName()+'-layout')
        if state == Qt.CheckState.Checked.value:
            lay.show()
        else:
            lay.hide()
        
        

    def edit_new_step(self):
        self.g1.show()

    def add_step(self):
        print('adding step!')

    def cancel_step(self):
        self.g1.hide()
        #####
        ####    RESET g1 FORM HERE
        #####
        
        
