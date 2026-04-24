"""
method.py

OVERALL FUNCTION

This file defines a class WindowMethod which creates a window object
that can be used to:
    - create a new method
    - view an existing method
    - edit an existing method
Depending on the arguments passed when first creating the WindowMethod() object.

There are two ways to edit an existing method because there are two places in which
a method may be stored:
    1. In a standalone method file (with .ovm extention for 'Open Voltam Method')
    2. Embedded in an Open Voltam sample (.ovs) file.

Thus WindowMethod() accepts either  a path to an .ovm file (as in
case #1) or a dictionary of data (as in case #2). When a path is given, the user
is given options for "save" (save changes to original path) and "save as" (save
changes to a new file, without modifying the original). When data is passed, the
user can only select "save" and the relevant .ovs file will automatically be updated.

ARGUMENTS

The WindowMethod() class accepts the following arguments:
    - path=False           -- a path to a .ovm data file
    - data=False           -- a dictionary the contains the expected keys present in an .ovm file
    - view_only=False      -- if True, the method is NOT editable, only viewable.
    - parent=False         -- the parent object of the WindowMethod (this is necessary only when view_only==True
    - view_only_edit=True  -- a binary that determines whether the "edit" button is enabled when view-only==True


INITIALIZATION

To get the following window configurations, use these arguments:
    - New Method:
        all args = default
        
    - Edit existing method from .osm file:
        path = path to file
        all other args = default

    - Edit existing method that is stored in a sample file:
        path = False
        data = data from sample file as dictionary
        all other args = default

    - View existing method from .osm file:
        path = path to file
        data = False
        view_only = True
        parent = parent object ('self' from calling object, usually)
        view_only_edit = whatever you prefer (True if you want the user to be able to open an editing window from the view window)

    - View existing method that is stored in a sample file:
        path = False
        data = data from sample file as dictionary
        view_only = True
        parent = parent object ('self' from calling object, usually)
        view_only_edit = whatever you prefer (True if you want the user to be able to open an editing window from the view window)

FUNCTIONALITY TO ADD
1. Auto fill ramp v0 parameter when ramp is added after const V. (for quick ease of use)
2. Auto fill const duration to match previous const duration (for quick ease of use)
3. Extend step rows to match width of QScrollArea


"""
#############################
#
#       IMPORTS
#
#############################

from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

from wins.sample import QVLine
from embeds.methodPlot import MethodPlot

from functools import partial
from copy import deepcopy

from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QIcon, QPixmap, QCloseEvent
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
    QGridLayout,
    QGroupBox,
    QSplitter,
    QScrollArea,
    QComboBox,
    QTabWidget,
    QApplication,
    QFileDialog
    )

class WindowMethod(QMainWindow):
    def __init__(self, parent, mode, path=False, method_id=False, mode_changable=True):
        super().__init__()
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.path = path
        self.method_id = method_id
        self.mode_changable = mode_changable

        self.saved = True
        self.analysis_change = False
        self.adding = False     # flag for whether step is being added
        self.editing = False    # flag for whether step is being edited
        self.close_on_save = False
        self.process = False
        self.save_error_flag = False
        self.steps = []
        self.selected = []
        self.relays = []
        self.status = self.statusBar()
        
        self.dl_val = 0
        self.changing_unit = False

        # Method name field
        self.name = QLineEdit()
        self.name.setObjectName('ov-method-name')
        self.name.setPlaceholderText('Profile name')
        self.name.textChanged.connect(self.changed_name)
    
        # Define method-wide parameters
        dt_lbl_0 = QLabel('Sample frequency:')   # sample frequency
        self.dt = QDoubleSpinBox()
        dt_lbl_1 = QLabel('Hz')
        self.dt.setMinimum(g.M_SAMPLE_FREQ_MIN)
        self.dt.setMaximum(g.M_SAMPLE_FREQ_MAX)
        self.dt.setValue(1)
        self.dt.valueChanged.connect(self.changed_value)

        current_range_lbl = QLabel("Device current range")  # Current range
        self.current_range = QComboBox()
        self.current_range.setPlaceholderText('Select...')
        for cr in g.CURRENT_RANGES:    
            self.current_range.addItem(cr)
        self.current_range.currentIndexChanged.connect(self.changed_value)

        gRelay = QGroupBox('External devices')
        self.vRelay = QVBoxLayout()
        self.vRelay.addStretch()
        gRelay.setLayout(self.vRelay)

        # Graph stuff
        self.hide_plot_lbls = QCheckBox('Hide plot labels')
        self.hide_plot_lbls.stateChanged.connect(self.refresh_graph)
        self.graph = MethodPlot()
        graph_area = QScrollArea()
        graph_area.setObjectName('ov-graph-area')
        graph_area.setWidget(self.graph)

        # Initialize scroll area for steps
        self.profile_chart = QScrollArea()          

        # Create buttons for the different window states
        self.but_new_save = QPushButton('Save')
        self.but_edit_save = QPushButton('Save')
        self.but_edit_save_as = QPushButton('Save as')
        self.but_view_only = QPushButton('Edit')
        self.but_edit_name_only = QPushButton('Save')

        self.but_new_save.clicked.connect(self.start_save)
        self.but_edit_save.clicked.connect(self.start_save)
        self.but_edit_save_as.clicked.connect(partial(self.start_save,True))
        self.but_view_only.clicked.connect(self.set_mode_viewish)
        self.but_edit_name_only.clicked.connect(self.start_save)
        
        self.buts = [self.but_new_save,
                     self.but_edit_save,
                     self.but_edit_save_as,
                     self.but_view_only,
                     self.but_edit_name_only]

        v1 = QVBoxLayout()
        v1.addLayout(horizontalize([dt_lbl_0, self.dt, dt_lbl_1], True))
        v1.addLayout(horizontalize([current_range_lbl, self.current_range], True))
        v1.addStretch()
        g1 = QGroupBox('Method parameters')
        g1.setLayout(v1)

        #####################################
        #                                   #
        #   ANALYSIS TAB                    #
        #                                   #
        #####################################

        peak_min_lbl = QLabel("Min")
        peak_max_lbl = QLabel("Max")
        self.peak_min = QDoubleSpinBox()
        self.peak_max = QDoubleSpinBox()
        self.peak_min.setMinimum(-999)
        self.peak_max.setMinimum(-999)
        self.peak_min.valueChanged.connect(self.analysis_impacted)
        self.peak_max.valueChanged.connect(self.analysis_impacted)
        peak_min_unit_lbl = QLabel("V")
        peak_max_unit_lbl = QLabel("V")

        g_peak_lay = QVBoxLayout()
        g_peak_lay.addLayout(horizontalize([peak_min_lbl, self.peak_min, peak_min_unit_lbl], True))
        g_peak_lay.addLayout(horizontalize([peak_max_lbl, self.peak_max, peak_max_unit_lbl], True))
        g_peak = QGroupBox("Expected peak location")
        g_peak.setLayout(g_peak_lay)

        sg_window_lbl = QLabel("Window length")
        sg_order_lbl = QLabel("Order of polynomial fit")
        self.sg_window = QSpinBox()
        self.sg_order = QSpinBox()
        self.g_sg = QGroupBox("Use Savitzky-Golay smoothing")
        self.sg_window.valueChanged.connect(self.analysis_impacted)
        self.sg_order.valueChanged.connect(self.analysis_impacted)
        self.g_sg.toggled.connect(self.analysis_impacted)
        g_sg_lay = QVBoxLayout()
        g_sg_lay.addLayout(horizontalize([sg_window_lbl, self.sg_window], True))
        g_sg_lay.addLayout(horizontalize([sg_order_lbl, self.sg_order], True))
        self.g_sg.setCheckable(True)
        self.g_sg.setLayout(g_sg_lay)

        lp_order_lbl = QLabel("Order")
        lp_freq_lbl = QLabel("Critical frequency")
        self.lp_order = QSpinBox()
        self.lp_freq = QDoubleSpinBox()
        self.g_lp = QGroupBox("Use Low-pass Butterworth smoothing")
        self.g_lp.toggled.connect(self.analysis_impacted)
        self.lp_order.valueChanged.connect(self.analysis_impacted)
        self.lp_freq.valueChanged.connect(self.analysis_impacted)
        g_lp_lay = QVBoxLayout()
        g_lp_lay.addLayout(horizontalize([lp_order_lbl, self.lp_order], True))
        g_lp_lay.addLayout(horizontalize([lp_freq_lbl, self.lp_freq], True))
        self.g_lp.setCheckable(True)
        self.g_lp.setLayout(g_lp_lay)

        vA = QVBoxLayout()
        
        vA.addWidget(g_peak)
        vA.addWidget(self.g_sg)
        vA.addWidget(self.g_lp)
        vA.addStretch()

        wAnalysis = QWidget()
        wAnalysis.setLayout(vA)

        #####################################
        #                                   #
        #   CALCULATION TAB                 #
        #                                   #
        #####################################

        unit_lbl = QLabel("Unit")
        self.unit = QComboBox()
        for key in g.UNIT_CONV_CONC.keys():
            self.unit.addItem(key, g.UNIT_CONV_CONC[key])
        self.unit.currentIndexChanged.connect(self.changed_unit)

        ci_lbl = QLabel("Confidence level")
        self.ci = QComboBox()
        for i, c in enumerate(g.M_CONFS):
            self.ci.addItem(c, g.M_CONFS_DATA[i])
        self.ci.currentIndexChanged.connect(self.changed_value)

        self.dl_lbl_base = "Detection limit"
        self.dl_lbl = QLabel(self.dl_lbl_base)
        self.dl = QDoubleSpinBox()
        self.dl.setRange(0, 9999)
        self.dl.setDecimals(3)
        self.dl.setValue(0)
        self.dl.valueChanged.connect(self.changed_dl)

        vC = QVBoxLayout()
        vC.addLayout(horizontalize([unit_lbl, self.unit], True))
        vC.addLayout(horizontalize([ci_lbl, self.ci], True))
        vC.addLayout(horizontalize([self.dl_lbl, self.dl], True))
        vC.addStretch()

        

        wCalc = QWidget()
        wCalc.setLayout(vC)

        #############################
        #                           #
        #   SET VISIBILITY          #
        #                           #
        #############################

        self.ws_for_new = [self.dt, self.current_range]
        self.ws_for_viewish = [self.name, self.peak_min, self.peak_max,
                               self.g_sg, self.sg_window, self.sg_order,
                               self.g_lp, self.lp_order, self.lp_freq,
                               self.unit, self.ci, self.dl]

       

        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:     # if this window can actually edit the method steps

            #################################
            #                               #
            #   LAY OUT STEP EDITOR         #
            #                               #
            #################################
            
            # Step-specific inputs
            step_name_lbl = QLabel('Step name')
            self.step_name = QLineEdit()
            self.step_name.setMaxLength(8)

            data_collect_lbl = QLabel('On this step collect:')
            self.data_collect = QComboBox()
            self.data_collect.addItem('None', g.M_DATA_NONE)
            self.data_collect.addItem('Data', g.M_DATA_SIGNAL)
            self.data_collect.addItem('Background', g.M_DATA_BACKGROUND)
            
            step_type_lbl = QLabel('Step type')
            self.step_type = QComboBox()                                        # Create dropdown menu
            self.step_type.setPlaceholderText('Select...')                      # Add placeholder text for when nothing is selected
            for sp_type in g.M_TYPES:                                          # Loop thru types (defined in globals)
                self.step_type.addItem(l.sp_types[sp_type][g.L])                # Add each type to the dropdown menu
            self.step_type.currentIndexChanged.connect(self.step_type_changed)  # Each time the dropdown selection is changed, connect to fn

            self.but_add_step = QPushButton(l.sp_add_btn[g.L])
            self.but_add_step.clicked.connect(self.add_step)

            # Set up type-specific parameters if the user selects CONSTANT VOLTAGE'
            const_v_lbl = QLabel('Voltage [V]')
            self.const_v = QDoubleSpinBox()
            self.const_v.setMinimum(g.M_V_MIN)
            const_t_lbl = QLabel('Duration [s]')
            const_t = QDoubleSpinBox()
            const_t.setMaximum(g.M_T_MAX)
            
            v_const = QVBoxLayout()
            v_const.addLayout(horizontalize([const_v_lbl, self.const_v]))
            v_const.addLayout(horizontalize([const_t_lbl, const_t]))
            v_const.addStretch()
            w_const = QWidget()
            w_const.setLayout(v_const)

            # Set up type-specific parameters if the user selects RAMP 
            ramp_v_start_lbl = QLabel('Start voltage [V]')
            self.ramp_v_start = QDoubleSpinBox()
            self.ramp_v_start.setMinimum(g.M_V_MIN)
            ramp_v_end_lbl = QLabel('End voltage [V]')
            self.ramp_v_end = QDoubleSpinBox()
            self.ramp_v_end.setMinimum(g.M_V_MIN)

            ramp_scan_rate_lbl = QLabel('Scan rate [V/s]')
            self.ramp_scan_rate = QDoubleSpinBox()
            self.ramp_scan_rate.setMaximum(g.M_SCAN_RATE_MAX)
            ramp_t = QDoubleSpinBox()
            ramp_t.setDecimals(12)
            
            v_ramp = QVBoxLayout()
            v_ramp.addLayout(horizontalize([ramp_v_start_lbl, self.ramp_v_start]))
            v_ramp.addLayout(horizontalize([ramp_v_end_lbl, self.ramp_v_end]))
            v_ramp.addLayout(horizontalize([ramp_scan_rate_lbl, self.ramp_scan_rate]))
            v_ramp.addStretch()
            w_ramp = QWidget()
            w_ramp.setLayout(v_ramp)

            # Organize some repeated widgets into lists to itterate over
            self.ts = {g.M_CONSTANT: const_t,
                       g.M_RAMP: ramp_t}

            # Load the type-specific widgets into the stacked layout in order
            self.s_type = QStackedLayout()
            self.s_type.addWidget(QWidget())
            self.s_type.addWidget(w_const)
            self.s_type.addWidget(w_ramp)

            self.vStepRelays = QVBoxLayout()
            self.vStepRelays.addStretch()

            # Set up the group box where user enters step information
            v2a = QVBoxLayout()
            v2a.addLayout(horizontalize([data_collect_lbl,self.data_collect]))
            v2a.addWidget(QHLine())
            v2a.addLayout(horizontalize([step_type_lbl,self.step_type]))
            v2a.addLayout(self.s_type)

            v2b = QVBoxLayout()
            v2b.addLayout(self.vStepRelays)

            hstep = QHBoxLayout()
            hstep.addLayout(v2a)
            hstep.addWidget(QVLine())
            hstep.addLayout(v2b)

            v2 = QVBoxLayout()
            v2.addLayout(horizontalize([step_name_lbl,self.step_name]))
            v2.addLayout(hstep)
            v2.addWidget(self.but_add_step)

            self.g_step = QGroupBox(l.sp_add_step[g.L])
            self.g_step.setObjectName('add-edit-step')
            self.g_step.setLayout(v2)           
            #policy = self.g_step.sizePolicy()      # get existing size policy of g_step
            #policy.setRetainSizeWhenHidden(True)   # modify policy so that g1 takes up space regardless of whether shown or hidden
            #self.g_step.setSizePolicy(policy)      # set g_step's size policy to the modified version.

            # Buttons to manipulate steps
            but_up = QPushButton()
            but_down = QPushButton()
            self.but_add = QPushButton()
            self.but_edit = QPushButton()
            but_dup = QPushButton()
            but_del = QPushButton()
            but_up.setIcon(QIcon(g.ICON_UP))
            but_down.setIcon(QIcon(g.ICON_DOWN))
            self.but_add.setIcon(QIcon(g.ICON_PLUS))
            self.but_edit.setIcon(QIcon(g.ICON_EDIT))
            but_dup.setIcon(QIcon(g.ICON_DUP))
            but_del.setIcon(QIcon(g.ICON_TRASH))
            but_up.setToolTip('Raise')
            but_down.setToolTip('Lower')
            self.but_add.setToolTip('Add new step')
            self.but_edit.setToolTip('Edit step')
            but_dup.setToolTip('Duplicate step(s)')
            but_del.setToolTip('Delete step(s)')
            but_up.clicked.connect(self.row_move_up)
            but_down.clicked.connect(self.row_move_down)
            self.but_add.clicked.connect(self.add_new_step)
            self.but_edit.clicked.connect(self.edit_step)
            but_dup.clicked.connect(self.row_duplicate)
            but_del.clicked.connect(self.row_delete)
            self.but_add.setObjectName('ov-btn-add')

            # Create lists of buttons for managing enabled/greyed-out status
            self.buts_one_selected = [self.but_edit]
            self.buts_mult_selected = [but_up, but_down, but_dup, but_del]
            self.buts_inactive_while_editing = [self.but_add, but_up, but_down, but_dup, but_del]
            self.buts_inactive_while_adding = [self.but_edit]

            vleft = QVBoxLayout()
            vleft.addLayout(horizontalize([g1, gRelay]))
            vleft.addWidget(QHLine())
            vleft.addStretch()
            vleft.addWidget(self.g_step)
            vleft.addWidget(self.profile_chart)
            vleft.addLayout(horizontalize([but_up, but_down]))
            vleft.addLayout(horizontalize([self.but_add, self.but_edit, but_dup, but_del]))

        else:                                               # if neither NEW nor EDIT modes 
            vleft = QVBoxLayout()
            vleft.addLayout(horizontalize([g1, gRelay]))
            vleft.addWidget(QHLine())
            vleft.addStretch()
            vleft.addWidget(self.profile_chart)


        #####################################
        #                                   #
        #       LAY EVERYTHING OUT          #               
        #                                   #
        #####################################

        vright = QVBoxLayout()
        vright.addWidget(self.graph)
        vright.addWidget(self.hide_plot_lbls)
        
        hConfig = QHBoxLayout()
        hConfig.addLayout(vleft)
        hConfig.addLayout(vright)
        wConfig = QWidget()
        wConfig.setLayout(hConfig)
        
        tab_layout = QTabWidget()
        tab_layout.setTabPosition(QTabWidget.TabPosition.North)
        tab_layout.addTab(wConfig, 'Configuration')
        tab_layout.addTab(wAnalysis, 'Analysis')
        tab_layout.addTab(wCalc, 'Calculation')

        v1 = QVBoxLayout()
        v1.addWidget(self.name)
        v1.addWidget(tab_layout)
        w = QWidget()
        w.setLayout(v1)

        self.refresh_relays()
        self.setCentralWidget(w)
        
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
            self.hide_new_step_pane()
            self.init_step_form_values()

        self.init_values()

        if not self.mode == g.WIN_MODE_NEW: 
            self.set_values()

        if self.mode == g.WIN_MODE_NEW:
            self.set_mode_new()
        elif self.mode == g.WIN_MODE_EDIT:
            self.set_mode_edit()
        elif self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
            self.set_mode_viewish()
        else:
            self.set_mode_view()           
            

    def init_step_form_values(self):
        #Reset title
        self.g_step.setTitle(l.sp_add_step[g.L])
        self.but_add_step.setText(l.sp_add_btn[g.L])
       
        # Reset all values common to all runs
        self.step_name.setText('')
        self.data_collect.setCurrentIndex(0)
        self.step_type.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)

        # clear relay content within the add/edit step pane
        for i in range(self.vStepRelays.count()):
            w = self.vStepRelays.itemAt(i).widget()
            if type(w) == type(QCheckBox()):
                w.setChecked(False)

        # Reset values specific to constant voltage steps
        self.const_v.setValue(0)

        # Reset values specific to voltage ramp steps
        self.ramp_v_start.setValue(0)
        self.ramp_v_end.setValue(0)

        # Reset duration values (this could maybe move to "values common to all runs" but keeping
        #   it separate for now in case we want to implement a different way of determining the
        #   duration of some steps i.e. measuring in terms of samples per voltage or total
        #   data points collected instead of time).
        for sp_type in g.M_TYPES:
            self.ts[sp_type].setValue(0)

    def init_values(self):

        ###################
        #   ANALYSIS TAB  #
        ###################
        self.peak_min.setValue(0)
        self.peak_max.setValue(0)
        self.g_sg.setChecked(False)
        self.sg_window.setValue(2)
        self.sg_order.setValue(1)
        self.g_lp.setChecked(False)
        self.lp_order.setValue(1)
        self.lp_freq.setValue(0.05)

        ###################
        #   CALC TAB      #
        ###################
        self.dl.setValue(0)
        self.unit.setCurrentIndex(1)
        self.ci.setCurrentIndex(1)
        
        

    def set_values(self):
        #####       GET DATA        #####
        if self.path:                                   # if there is a path to a method file,
            data = get_data_from_file(self.path)        #   get the most up to date data from the file
        elif self.method_id:                            # otherwise, if there is a method id given,
            data = get_method_from_file_data(self.parent.data, self.method_id)   #  use it to grab the method data

        #####       SET NAME        #####
        self.name.setText(data[g.M_NAME])               # set name

        #####   SET CONFIG TAB      #####
        self.dt.setValue(data[g.M_SAMPLE_FREQ])                  # set dt
        cr_text = data[g.M_CURRENT_RANGE]               # set current range
        self.current_range.setCurrentIndex(g.CURRENT_RANGES.index(cr_text))
        self.relays = data[g.M_EXT_DEVICES]
        self.refresh_relays()
        self.steps = data[g.M_STEPS]                    # set steps 
        self.refresh_list()                             # rebuild visual steps list based on self.steps

        ##### SET ANALYSIS TAB     #####
        self.peak_min.setValue(data[g.M_PEAK_V_MIN])
        self.peak_max.setValue(data[g.M_PEAK_V_MAX])        
        self.g_sg.setChecked(data[g.M_SG])
        self.g_lp.setChecked(data[g.M_LP])
        if self.g_sg.isChecked():
            self.sg_window.setValue(data[g.M_SG_WINDOW])
            self.sg_order.setValue(data[g.M_SG_ORDER])
        if self.g_lp.isChecked():
            self.lp_order.setValue(data[g.M_LP_ORDER])
            self.lp_freq.setValue(data[g.M_LP_FREQ])

        ##### SET CALCULATION TAB   #####
        self.unit.setCurrentIndex(self.unit.findText(data[g.M_UNIT]))
        self.ci.setCurrentIndex(self.ci.findData(data[g.M_CONF]))
        self.dl.setValue(convert_conc_from_file_unit(data[g.M_DETECTION_LIMIT], data[g.M_UNIT]))

         
        
    #####################################
    #                                   #
    #   Handlers for changed widgets    #
    #                                   #
    #####################################

    def changed_name(self):             # routine for any name changes
        self.set_header()               # set the window header to match the name
        self.changed_value()            # indicate that a method value has been changed!
        
    def changed_value(self):            # routine for any changes to the method
        self.saved = False              # reset saved flag to signify unsaved changes
        self.status.showMessage('')     # clear any statuses being shown (ie. if it, for example, says 'Saved.' already, we want this message to disappear)

    def analysis_impacted(self):        # if an analysis is impacted
        self.analysis_change = True     # set flag
        self.changed_value()            # and run routing for a calc being impacted (changes to any analysis may impact a calc)

    def changed_unit(self):
        self.changing_unit = True
        unit = self.unit.currentText()                                          # When the unit is changed
        dl_newunit = convert_conc_from_file_unit(self.dl_val, unit)
        self.dl.setValue(dl_newunit)                                            # Update the detection limit to match the new unit
        self.dl_lbl.setText(self.dl_lbl_base + ' ['+unit+']')                   # And update the label to match as well.
        self.changed_value()
        self.changing_unit = False

    def changed_dl(self):
        if self.changing_unit:
            return
        unit = self.unit.currentText()
        self.dl_val = convert_conc_to_file_unit(self.dl.value(), unit)            
        self.changed_value()



    
        

    

    #################################
    #                               #
    #   Mode setting functions      #
    #                               #
    #################################

    def set_mode_new(self):
        self.mode = g.WIN_MODE_NEW
        self.set_header()
        self.set_button_bar([self.but_new_save])
        self.toggle_widget_editability()
        self.reset_save_trackers()

    def set_mode_edit(self):
        self.mode = g.WIN_MODE_EDIT
        self.set_header()
        self.set_button_bar([self.but_edit_save, self.but_edit_save_as])
        self.toggle_widget_editability()
        self.reset_save_trackers()

    def set_mode_view(self):
        self.mode = g.WIN_MODE_VIEW_ONLY
        self.set_header()
        self.set_button_bar([self.but_view_only])
        self.toggle_widget_editability()
        self.reset_save_trackers()

    def set_mode_viewish(self):
        self.mode = g.WIN_MODE_VIEW_WITH_MINOR_EDITS
        self.set_header()
        self.set_button_bar([self.but_edit_name_only])
        self.toggle_widget_editability()
        self.name.setText(self.name.text())             # This just sets the name text again and moves the cursor to the name field
        self.name.setSelection(0,len(self.name.text())) # Highlight name
        self.reset_save_trackers()

    def reset_save_trackers(self):
        self.analysis_change = False
        self.saved = True
        

    def set_button_bar(self, buttonList):
        """Takes in a button widget. Removes all removable buttons from layout, then adds
        button back in at the appropriate spot"""
        for but in self.buts:
            but.setParent(None)
        if self.mode_changable:
            h = QHBoxLayout()
            for but in buttonList:
                h.addWidget(but)
            self.centralWidget().layout().addLayout(h) # Add button to end of right-column layout

    def set_buttons_enabled(self, enabled=True):
        for but in self.buts:
            but.setEnabled(enabled)

    def toggle_widget_editability(self):
        """Depending on the current mode, enables/greys-out certain widgets"""
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
            to_enable = self.ws_for_new + self.ws_for_viewish
            to_not = []
        elif self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
            to_enable = self.ws_for_viewish
            to_not = self.ws_for_new
        else:
            to_enable = []
            to_not = self.ws_for_new + self.ws_for_viewish
        for w in to_enable:
            w.setEnabled(True)
        for w in to_not:
            w.setEnabled(False)


    #########################################
    #                                       #
    #   Relay / External device functions   #
    #                                       #
    # 1. add_relay                          #
    # 2. delete_relay                       #
    # 3. relay_edited                       #
    # 4. refresh_relays                     #
    #                                       #
    #########################################
    
    def add_relay(self, txt=False):
        self.saved = False
        if txt: self.relays.append(txt)
        else: self.relays.append("")
        self.refresh_relays()           # refresh list of relays in add/edit step pane

    def delete_relay(self, del_index):
        self.saved = False
        del self.relays[del_index]                                      # delete from relay list

        for step in self.steps:                   # adjust all existing relay references in steps accordingly
            if del_index in step[g.M_RELAYS_ON]:                        #   1. Delete references to deleted relay
                step[g.M_RELAYS_ON].remove(del_index)
            for j, relay_id in enumerate(step[g.M_RELAYS_ON]):  #   2. Adjust all higher indices down by 1
                if relay_id > del_index:
                    step[g.M_RELAYS_ON][j] = relay_id-1
                    
        self.refresh_relays()  

    def relay_edited(self, i):
        self.saved = False
        txt = self.vRelay.children()[i].itemAt(1).widget().text()
        self.relays[i] = txt
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
            self.vStepRelays.itemAt(i).widget().setText(txt+' on during step?')
        self.refresh_list()    


    def refresh_relays(self):
        # clear upper relay content
        for child in self.vRelay.children():
            for i in reversed(range(child.count())):
                if type(child.itemAt(i).widget()) != type(None):    # Remove all widgets within horizontal layout
                    child.itemAt(i).widget().setParent(None)
            child.layout().setParent(None)                          # Remove the H layout itself

        # reset relay boxes in upper pane     
        for i,relay in enumerate(self.relays):                      # For each relay
            txt = QLabel("Relay "+str(i+1)+" controls:")            # Create the label
            fill = get_relay_text(relay, i)                         # Get the value for the textbox
            val = QLineEdit()                                       # Create the textbox
            if relay == "":                                         # If no device name has been entered by user
                val.setPlaceholderText(fill)                        #   Set placeholder text
            else:                                                   # If device name HAS been entered by user
                val.setText(fill)                                   #   Fill it in.
            val.textEdited.connect(partial(self.relay_edited, i))   # When text is modified, do some stuff
            val.setMaxLength(16)                                    # Only allow pretty short strings

            h = QHBoxLayout()                                       # Put it all in a horizontal layout
            h.addWidget(txt)
            h.addWidget(val)
            
            if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
                delete = QPushButton('delete')                          # Add a delete button to each row
                delete.clicked.connect(partial(self.delete_relay, i))   # When the delete button is pushed, do some stuff
                h.addWidget(delete)
            else:
                val.setEnabled(False)

            self.vRelay.insertLayout(self.vRelay.count()-1, h)      # Add the layout at the bottom (but above the stretch)

            
              
        


        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:

            # Add 'add' button back in to upper pane
            self.add_relay_but = QPushButton('Add external device')
            self.add_relay_but.clicked.connect(self.add_relay)
            h = QHBoxLayout()
            h.addWidget(self.add_relay_but)
            self.vRelay.insertLayout(self.vRelay.count()-1, h)
            if len(self.relays) >= g.M_RELAY_MAX:
                self.add_relay_but.setEnabled(False)
            else:
                self.add_relay_but.setEnabled(True)

            # clear relay content within the add/edit step pane
            checked = []
            for i in reversed(range(self.vStepRelays.count())):
                if type(self.vStepRelays.itemAt(i).widget()) != type(None):
                    self.vStepRelays.itemAt(i).widget().setParent(None)

            for relay in self.relays:
                fill = get_relay_text(relay, i)                         # Get the value for the textbox
                step_chk = QCheckBox(fill+' on during step?')           # Add a checkbox to the "Add/Edit Step" pane for this relay
                self.vStepRelays.insertWidget(self.vStepRelays.count()-1, step_chk)
                
                
            

        self.refresh_list()             # refresh steps pane (as it contains references to releays)

        
    
        
        
                
            





    
    def set_step_values_for_editing(self, step):
        self.init_step_form_values()                     # initialize all form values
        
        # Modify title and button text
        self.g_step.setTitle(l.sp_edit_step[g.L])
        self.but_add_step.setText(l.sp_edit_btn[g.L])
        
        # Set top values to values from step
        self.step_name.setText(step[g.M_STEP_NAME])

        # Set correct value on data-collection dropdown
        for i in range(self.data_collect.count()):
            if self.data_collect.itemData(i) == step[g.M_DATA_COLLECT]:
                self.data_collect.setCurrentIndex(i)
                break

        # Check all the appropriate relays for this step
        for relay_index in step[g.M_RELAYS_ON]:
            self.vStepRelays.itemAt(relay_index).widget().setChecked(True)

        this_type = step[g.M_TYPE]
        self.step_type.setCurrentIndex(g.M_TYPES.index(this_type))

        # Set step-type specific properties
        duration = step[g.M_T]
        self.ts[this_type].setValue(duration)

        if this_type == g.M_CONSTANT:
            self.const_v.setValue(step[g.M_CONST_V])

        elif this_type == g.M_RAMP:
            v0 = step[g.M_RAMP_V1]
            vf = step[g.M_RAMP_V2]
            self.ramp_v_start.setValue(v0)      # set V start
            self.ramp_v_end.setValue(vf)        # set V end
            sr = self.ramp_duration_to_scan_rate(v0, vf, duration)
            self.ramp_scan_rate.setValue(sr)    # set scan rate (calculated from duration, v1, and v2)
        
    def refresh_list(self):
        """ Clears the sweep list and rebuilds it"""
        try:
            #self.erase_list_visualization()
            self.build_new_list()
            self.refresh_graph()
            self.update_highlights()
            if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
                self.update_buttons()
        except Exception as e:
            print('here, issue with refreshing the list!')
            print(e)

    '''def erase_list_visualization(self):
        """ Erases the content of the current sweep list that is displayed"""
        w = self.profile_chart.findChild(QWidget)
        lay = w.layout()
        print(w)
        print(lay)
        print(lay.count)
        try:
            for i in reversed(range(lay.count())):
                print(lay.itemAt(i).widget())
                lay.itemAt(i).widget().setParent(None)
        except Exception as e:
            print('<---issue erasing!')
            print(e)
            print('--->')
            return'''

    def update_buttons(self):
        yes = []
        no = []
        if self.editing:
            no = self.buts_inactive_while_editing
        elif self.adding:
            no = self.buts_inactive_while_adding
        elif len(self.selected) == 0:
            no = self.buts_one_selected + self.buts_mult_selected
            yes = [self.but_add]
        elif len(self.selected) == 1:
            yes = self.buts_one_selected + self.buts_mult_selected  + [self.but_add]
        else:
            no = self.buts_one_selected
            yes = self.buts_mult_selected
        
        for but in no:
            but.setEnabled(False)
        for but in yes:
            but.setEnabled(True)            


    def build_new_list(self):

        #print(self.steps)

        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)

        
        for i, step in enumerate(self.steps):
            #### TO ADD MORE WIDGETS TO THIS LAYOUT, DEFINE THEM HERE
            step_type = step[g.M_TYPE]
            w_name = QLabel(step[g.M_STEP_NAME])
            
            
            w_volt = QLabel()
            w_t = QLabel()
            t = step[g.M_T]
            
            if step_type == g.M_CONSTANT:
                w_volt = QLabel('const: '+str(step[g.M_CONST_V])+'V')
                w_t = QLabel(str(t)+'s')
            elif step_type == g.M_RAMP:
                v0 = step[g.M_RAMP_V1]
                vf = step[g.M_RAMP_V2]
                sr = self.ramp_duration_to_scan_rate(v0, vf, t)
                w_volt.setText('ramp: '+str(v0)+'V'+' --> '+str(vf)+'V')
                w_t = QLabel(str(sr)+'V/s')

            
            ws_relay = []
            for j,relay in enumerate(self.relays):
                w = QLabel()
                name = get_relay_text(relay, j)
                w.setToolTip(name+' OFF')
                if j in step[g.M_RELAYS_ON]:
                    w.setPixmap(QPixmap(g.ICON_RELAY[j]))
                    w.setToolTip(name+' ON')
                ws_relay.append(w)

            '''w_stir = QLabel()
            w_stir.setToolTip('Stirrer OFF')
            if step[g.M_STIR]:
                w_stir.setPixmap(QPixmap(g.ICON_STIR))
                w_stir.setToolTip('Stirrer ON')

            w_vib = QLabel()
            w_vib.setToolTip('Vibrator OFF')
            if step[g.M_VIBRATE]:
                w_vib.setPixmap(QPixmap(g.ICON_VIB))
                w_vib.setToolTip('Vibrator ON')'''

            w_collect = QLabel()
            w_collect.setToolTip('Data collection OFF')
            if step[g.M_DATA_COLLECT]==g.M_DATA_SIGNAL:
                w_collect.setPixmap(QPixmap(g.ICON_MEASURE))
                w_collect.setToolTip('Collecting SIGNAL')
            elif step[g.M_DATA_COLLECT]==g.M_DATA_BACKGROUND:
                w_collect.setPixmap(QPixmap(g.ICON_BACKGROUND))
                w_collect.setToolTip('Collecting BACKGROUND')
            
            '''ws = [w_name, w_volt, w_t, w_stir, w_vib, w_collect]'''
            ws = [w_name, w_volt, w_t] + ws_relay + [w_collect]
            ####### THEN ADD THEM TO THE ws LIST. THATS IT YAYYYYY 

            if (i%2 == 0):
                obj_name = g.STEP_ODD_ROW_NAME
            else:
                obj_name = g.STEP_EVEN_ROW_NAME

            for j, w in enumerate(ws):
                w.mouseReleaseEvent = partial(self.row_clicked, w)
                w.setObjectName(obj_name)
                w.setProperty('row', i)
                grid.addWidget(w, i, j)

        grid.setColumnStretch(4,1)
         
        self.w_pc = QWidget()                       # Initialize widget that sits within scroll area
        self.w_pc.setLayout(grid)
        self.w_pc.setObjectName('steps-container')
        self.profile_chart.setWidget(self.w_pc)

    def row_clicked(self, w, event):
        if not self.editing and not self.adding:
            # If the window is view-only, block the user from modifying the rows
            if self.mode == g.WIN_MODE_VIEW_ONLY or self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:                          
                return    
            keys = QApplication.keyboardModifiers()
            i = w.property('row')
            if keys == Qt.KeyboardModifier.ControlModifier:             # If this is a ctrl+click  
                if i in self.selected:                                  # If the clicked row is already selected
                    self.selected.remove(i)
                else:                                                   # If it was not already selected 
                    self.selected.append(i) 
            else:                                                       # If this is a regular click
                if (len(self.selected) == 1 and (i in self.selected)):  # If there is exactly one row selected and it was clicked
                    self.selected = []
                else:                                                   # Otherwise
                    self.selected = [i]                                 #   Set the clicked row as the only one selected
            self.update_highlights()                                    # update the highlights of the whole list
            self.update_buttons()                                       # update which buttons are greyed out


    def update_highlights(self):                    
        for i,step in enumerate(self.steps):            # Loop thru all steps
            if i in self.selected:                      # IF the step has been selected
                self.change_row_highlight(i, True)      # Make sure it is highlighted
            else:                                       # Otherwise
                self.change_row_highlight(i,False)      # Make sure it is not highlighted
        applyStyles()                                   # Apply styles (this is a processing-intensive step, good to only do as often as necessary)

    def change_row_highlight(self, i, to_highlight):
        row_ws = get_row_ws(self.profile_chart, i)                                      # Get all widgets in row i
        highlighted = self.widget_is_highlighted(row_ws[0])                             # Check if the row is already highlighted
        for w in row_ws:                                                                # Loop thru all widgets in row
            if to_highlight and not highlighted:                                        # If we're supposed to highlight and it is currently unhighlighted
                w.setObjectName(w.objectName()+g.RUNS_ROW_SELECTED_SUFFIX)              # Change the widget's object name to indicate highlighting
            elif not to_highlight and highlighted:                                      # IF we're suppose to unhighlight and it is currently highlighted
                w.setObjectName(w.objectName().replace(g.RUNS_ROW_SELECTED_SUFFIX,''))  # Change the widget's object name to indicate not highlighted
        
    def widget_is_highlighted(self, w):
        if g.RUNS_ROW_SELECTED_SUFFIX in w.objectName():    # To check whether a widget is highlighted
            return True                                     # Check whether its object name contains the selected suffix
        return False
        
        

    def row_move_up(self):
        if len(self.selected) == 0:             # if there is nothing selected, return
            return

        indices = sorted(self.selected)         # goes from top of list down
        new_selected = []
        
        if indices[0] == 0:                     # if top step is selected, do nothing (it can't go any higher!)
            return
        else:
            for i in indices:
                row = self.steps[i]
                del self.steps[i]
                self.steps.insert(i-1, row)
                new_selected.append(i-1)
            self.selected = new_selected
            self.refresh_list()
            self.changed_value()
            
    def row_move_down(self):
        if len(self.selected) == 0:             # if there is nothing selected, return
            return
        indices = sorted(self.selected)
        indices.reverse()                           # go from bottom of list up
        new_selected = []
        if indices[0] == len(self.steps)-1:         # if the final step is included, do nothing (it can't move down further!)
            return
        else:
            for i in indices:
                row = self.steps[i]
                del self.steps[i]
                self.steps.insert(i+1, row)
                new_selected.append(i+1)
            self.selected = new_selected
            self.refresh_list()
            self.changed_value()
    
    def row_duplicate(self):
        if len(self.selected) == 0:             # if there is nothing selected, return
            return
        indices = sorted(self.selected)             # sort selected indices
        index_blocks = self.blockify(indices)       # create an array of arrays to group consecutive indices
        new_selected = []
        rows_added = 0
        for block in index_blocks:                                                  # for each consecutive block of indices                  
            for i in block:                                                         # loop thru the indices
                new_selected.append(i+rows_added+len(block))                        #   store the index of where the new row will be
                new_step = deepcopy(self.steps[i+rows_added])                       #   create a totally new duplicate row and...
                self.steps.insert(i+rows_added+len(block), new_step)                #   ...insert the duplicate row there!
            rows_added = rows_added + len(block)                                    # add the adjustment for going forwards thru th list
        self.selected = new_selected
        self.refresh_list()
        self.changed_value()

            

    def edit_step(self):
        if self.g_step.isHidden():
            self.show_edit_step()
        else:
            self.hide_edit_step()

    def show_edit_step(self):
        self.editing = True
        self.update_buttons()
        self.but_edit.setIcon(QIcon(g.ICON_X))
        self.but_edit.setToolTip('Cancel')
        step = self.steps[self.selected[0]]
        self.set_step_values_for_editing(step)
        self.g_step.show()
        

    def hide_edit_step(self):
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))
        self.but_edit.setToolTip('Cancel')
        self.g_step.hide()                              # hide the add/edit step pane
        self.init_step_form_values()                     # and wipe the form 
        self.editing = False
        self.update_buttons()
        
        
    def row_delete(self):
        if len(self.selected) == 0:             # if there is nothing selected, return
            return
        indices = sorted(self.selected)
        indices.reverse()
        for i in indices:
            del self.steps[i]
        if i<len(self.steps):
            self.selected = [i]
        elif len(self.steps)>0:
            self.selected = [len(self.steps)-1]
        else:
            self.selected = []
        self.refresh_list()
        self.changed_value()

    def blockify(self, i_list):

        """ Takes in a list of integers. Returns a list of lists where all consecutive integers
        have been grouped together in sub-lists, in the same order that the original list was
        passed. For example, if the passed list is:
        [2,3,5,6,7,12,72,73,15,99,12,11,10,1]
        The following will be returned
        [[2,3],[5,6,7],[12],[72,73],[15],[99],[12,11,10],[1]]"""
        
        block_list = []
        block = []
        for j, val in enumerate(i_list):
            block.append(val)
            if (j == len(i_list)-1 or abs(i_list[j]-i_list[j+1]) != 1):
                block_list.append(block)
                block = []
        return block_list  

    def step_type_changed(self, i):
        self.s_type.setCurrentIndex(i+1) # the +1 allows for the 0th screen to be empty
        
    def add_new_step(self):
        if self.g_step.isHidden():
            self.show_new_step_pane()
        else:
            self.hide_new_step_pane()

    def show_new_step_pane(self):
        self.adding = True
        self.update_buttons()
        self.g_step.show()
        self.but_add.setIcon(QIcon(g.ICON_X))
        self.but_add.setToolTip('Cancel')

    def hide_new_step_pane(self):
        self.g_step.hide()                              # hide the pane
        self.but_add.setIcon(QIcon(g.ICON_PLUS))    # make sure the add icon is a + (instead of an x) 
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))    # make sure the add icon is a + (instead of an x)
        self.but_add.setToolTip('Add new step')
        self.adding = False
        self.editing = False
        self.init_step_form_values()                     # and wipe the form
        self.update_buttons()
        

    def add_step(self):
        
        if self.validate_step():
            step_type = g.M_TYPES[self.step_type.currentIndex()]

            self.set_duration(step_type)

            relays_on = []
            for i in range(self.vStepRelays.count()):
                w = self.vStepRelays.itemAt(i).widget()
                if type(w) == type(QCheckBox()):
                    if w.isChecked():
                        relays_on.append(i)
            
            # Grab the data that all steps contain   
            data_general = {
                g.M_STEP_NAME: self.step_name.text(),
                g.M_DATA_COLLECT: self.data_collect.currentData(), 
                g.M_RELAYS_ON: relays_on,
                g.M_TYPE: step_type,
                g.M_T: self.ts[step_type].value()
                }            
            
            ############################################ IF ADDING ANOTHER STEP TYPE, ADD ANOTHER ELIF TO THE CODE BELOW ############
            data_specific = {}                                                                                                      #
            if step_type == g.M_CONSTANT:                                                                                           #
                data_specific = {                                                                                                   #
                    g.M_CONST_V: self.const_v.value()                                                                               #                                                                                 #
                    }                                                                                                               #
                                                                                                                                    #
            elif step_type == g.M_RAMP:                                                                                             #
                data_specific = {                                                                                                   #
                    g.M_RAMP_V1: self.ramp_v_start.value(),                                                                         #
                    g.M_RAMP_V2: self.ramp_v_end.value()                                                                            #
                    }                                                                                                               #
            #########################################################################################################################

            # combine all of the above created dictionaries and store them
            new_step = data_general | data_specific

            if self.adding:
                self.steps.append(new_step)
            elif self.editing:
                i = self.selected[0]
                self.steps[i] = new_step
            self.selected = []          # clears selection and will clear highlights when list is refreshed
            self.refresh_list()         # refresh the list (to visualize the new row and clear stale highlights)
            self.hide_new_step_pane()   # close the pane that allows the user to add a new step
            self.init_step_form_values()     # reset the hidden pane to initial values
            self.changed_value()
        

    def is_checked(self, checkbox):
        if checkbox.checkState() == Qt.CheckState.Checked:
            return True
        return False

    def validate_step(self):
        #########################33##########
        #
        #   FOR TESTING ONLY, COMMENT TO RUN
        #return True
        #
        #
        #####################################

        if self.step_type.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:    # make sure there is a type selected
            show_alert(self, 'Error!', 'Please select a type of run')
            return False
        
        step_type = g.M_TYPES[self.step_type.currentIndex()]
        if self.ts[step_type].value() == 0: # make sure there is a duration
            if step_type != g.M_RAMP:       # don't flag this error if type is ramp because instead we ask for scan rate 
                show_alert(self, 'Error!', 'Please set a duration longer than 0 for this step')
                return False
    
        if step_type == g.M_RAMP:
            v1 = self.ramp_v_start.value()
            v2 = self.ramp_v_end.value()
            if v1 == v2:
                show_alert(self, 'Error!', 'The endpoints of this ramp have the same value, if this is what you want, please consider a constant volutage. Otherwise...typo?')
                return False
            if self.ramp_scan_rate.value() == 0:
                show_alert(self, 'Error!', 'Please set a scan rate greater than 0.')
                return False
            
        return True

    def start_save(self, save_as=False):
        if self.saved and not save_as:
            self.status.showMessage('All changes saved.', g.SB_DURATION)
            if self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
                self.set_mode_view()
        else:
            self.set_buttons_enabled(enabled=False)
            if self.validate_method():
                if save_as or self.mode == g.WIN_MODE_NEW:
                    self.method_save_as()
                else:
                    self.method_save()
            else:
                self.set_buttons_enabled()
    
    def method_save_as(self):     
        # get the actual filename and path from user
        initial_name = guess_filename(self.name.text())
        self.path = QFileDialog.getSaveFileName(self, 'Save method', initial_name, g.METHOD_FILE_TYPES)[0]
            
        if not self.path or self.path == '':    # if the user didn't select a path
            self.set_buttons_enabled()
            return                              # don't try to save, just return
        self.method_save()                      # save the file!

    def method_save(self):
        # if saving a local method, make sure we update impacted calcs and delete impacted analyses
        if self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
            tasks = []
            for run in self.parent.data[g.S_RUNS]:
                if run[g.R_UID_METHOD] == self.method_id:
                    reps = get_all_reps_from_run_id(self.parent.data, run[g.R_UID_SELF])
                    for rep in reps:
                        tasks.append(rep)
            # Check analyses
            analyses_to_delete = []
            if self.analysis_change:
                continue_action, analyses_to_delete = check_analysis_conflict(self.parent.data, tasks)
                if not continue_action:
                    self.set_buttons_enabled()
                    return

            # Check calcs
            calcs_to_update = []
            continue_action, calcs_to_update = check_calc_conflict(self.parent.data, tasks)
            if not continue_action:
                self.set_buttons_enabled()
                return
            
            
            
            

        # Gather all the inputs in the method into a dictionary
        data = self.gather_inputs()

        
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:     # If we are working on an .ovm (method) file
            self.start_async_overwrite(data)                                #   just dump all the data in, overwriting what is already ther
        else:                                                               # If we are workign in an .ovs (sample) file
            self.status.showMessage('Saving method...')                     #   We have to be a bit more nuanced. Using an async save
            data[g.M_UID_SELF] = self.method_id                             #   process here to update the relevant part of the existing
                                                                            #   .ovs file
            cb_suc = self.after_save_method_success
            cb_err = self.after_save_method_error

            unit = data[g.M_UNIT]
            dl = data[g.M_DETECTION_LIMIT]
            conf = data[g.M_CONF] 

            cb_analysis = partial(self.parent.start_async_save, g.SAVE_TYPE_ANALYSES_DEL, [analyses_to_delete], cb_suc, cb_err)     # Callback to delete analyses after method is saved
            cb_calcs = partial(self.parent.start_async_save, g.SAVE_TYPE_CALCS_FROM_METHOD, [unit, dl, conf, calcs_to_update], cb_analysis, cb_err)
            
            self.parent.start_async_save(g.SAVE_TYPE_METHOD_MOD, [self.method_id, data], onSuccess=cb_calcs, onError=cb_err)

    def gather_inputs(self):
        # Gather optional savgol filter parameters
        sg = {}
        if self.g_sg.isChecked():
            sg[g.M_SG] = True
            sg[g.M_SG_WINDOW] = self.sg_window.value()
            sg[g.M_SG_ORDER] = self.sg_order.value()
        else:
            sg[g.M_SG] = False
            sg[g.M_SG_WINDOW] = None
            sg[g.M_SG_ORDER] = None

        # Gather optional lowpass filter parameters
        lp = {}
        if self.g_lp.isChecked():
            sg[g.M_LP] = True
            sg[g.M_LP_ORDER] = self.lp_order.value()
            sg[g.M_LP_FREQ] = self.lp_freq.value()
        else:
            sg[g.M_LP] = False
            sg[g.M_LP_ORDER] = None
            sg[g.M_LP_FREQ] = None

        # Gather all other method parameters    
        data = {g.M_NAME: self.name.text(),
                g.M_SAMPLE_FREQ: self.dt.value(),
                g.M_CURRENT_RANGE: self.current_range.currentText(),
                g.M_EXT_DEVICES: self.relays, 
                g.M_STEPS: self.steps,
                g.M_UNIT: self.unit.currentText(),
                g.M_CONF: self.ci.currentData(),
                g.M_PEAK_V_MIN: self.peak_min.value(),
                g.M_PEAK_V_MAX: self.peak_max.value(),
                g.M_DETECTION_LIMIT: convert_conc_to_file_unit(self.dl.value(), self.unit.currentText())
                }

        #Append optional filter parameters
        for d in (sg, lp):
            for key in d.keys():
                data[key] = d[key]

        print(data)

        return data
        
    def start_async_overwrite(self, toWrite):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_overwrite_stdout)
        self.process.readyReadStandardError.connect(self.handle_overwrite_stderr)
        self.process.finished.connect(partial(self.handle_finished_overwrite))
        self.status.showMessage("Saving method...")
        print('got here!')
        
        if g.PROC_RUN_FROM == g.PROC_RUN_FROM_PYTHON:
            self.process.start('python', [g.PROC_SCRIPT_PYTHON, g.PROC_TYPE_OVERWRITE, self.path, str(toWrite)])
        else:
            self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_OVERWRITE, self.path, str(toWrite)])

        

    def handle_overwrite_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        print(stdout)

    def handle_overwrite_stderr(self):
        print('error msg:')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print(stderr)
        self.save_error_flag = True

    def handle_finished_overwrite(self):
        if self.save_error_flag:# If run errored
            self.after_save_method_error()                                                         
        else:                                                                           # If the run succeeded
            self.after_save_method_success()        
        self.save_error_flag = False                                                    # Reset the error-on-save flag
        self.process = None                                                             # Wipe the process from memory
        
    def after_save_method_success(self):
        self.saved = True
        self.status.showMessage('Method saved.', g.SB_DURATION)
        self.set_buttons_enabled()
        if self.close_on_save:
            self.close()
        elif self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
            self.set_mode_view()
        elif self.mode == g.WIN_MODE_NEW:
            self.set_mode_edit()

    def after_save_method_error(self):
        self.status.showMessage('ERROR: Method did not save.', g.SB_DURATION_ERROR)
        self.set_buttons_enabled()



    def validate_method(self):
        #################
        #   NAME        #
        #################
        print('validating!')
        if not self.name.text():                                                                # if there is no method name
            show_alert(self, 'Error!', 'Please name this method.')
            return False
        if len(self.name.text()) < 3:                                                         # if method name is too short
            show_alert(self, 'Error!', 'Method name must contain at least three characters.')
            return False

        #################
        #   CONFIG TAB  #
        #################
        if self.dt.value() == float(0):                                                       # if there is no dt set
            show_alert(self, 'Error!', 'Please select a sample frequency greater than 0.')
            return False
        if self.current_range.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:                  # if there is no current range selected
            show_alert(self, 'Error!', 'Please select a current range.')
            return False
        if len(self.steps) == 0:                                                              # if no steps have been added
            show_alert(self, 'Error!', 'Please add at least one step to the method.')
            return False
        if "" in self.relays:
            show_alert(self, 'Error!', 'Please entere a device name for all external devices/relays.')
            return False
        signal_steps = []
        background_steps = []
        for step in self.steps:
            if step[g.M_DATA_COLLECT] == g.M_DATA_SIGNAL:
                signal_steps.append(step)
            elif step[g.M_DATA_COLLECT] == g.M_DATA_BACKGROUND:
                background_steps.append(step)
        if len(signal_steps) == 0:       # More than 1 signal collection step in method
            resp = show_warning("Warning: data collection", "Just a heads up, this method will not collect any data.\nAre you sure you want to continue?")   
            if not resp: return False
        if len(signal_steps) > 1:       # More than 1 signal collection step in method
            resp = show_warning("Warning: data collection", "Just a heads up, this method has multiple data collection steps.\nAre you sure you want to continue?")   
            if not resp: return False
        if len(background_steps) > 1:   # More than 1 background collection step in method
            resp = show_warning("Warning: data collection", "Just a heads up, this method has multiple background data collection steps.\nAre you sure you want to continue?")   
            if not resp: return False
        if len(signal_steps) == 1 and len(background_steps) == 1:
            sig = signal_steps[0]
            bac = background_steps[0]
            if sig[g.M_TYPE] != bac[g.M_TYPE]:      # Signal and background steps are different types
                resp = show_warning("Warning: data collection", "Just a heads up, the data and background collection steps are of different types.\nAre you sure you want to continue?")   
                if not resp: return False
            else:
                if sig[g.M_TYPE] == g.M_CONSTANT:   # Signal and background steps are same type but values don't match (CONSTANT)
                    if sig[g.M_CONST_V] != bac[g.M_CONST_V] or sig[g.M_T] != bac[g.M_T]:
                        resp = show_warning("Warning: data collection", "Just a heads up, the data and background collection steps have differnt values.\nAre you sure you want to continue?")   
                        if not resp: return False
                        
                elif sig[g.M_TYPE] == g.M_RAMP:     # Signal and background steps are same type but values don't match (RAMP)
                    if sig[g.M_RAMP_V1] != bac[g.M_RAMP_V1] or sig[g.M_RAMP_V2] != bac[g.M_RAMP_V2] or sig[g.M_T] != bac[g.M_T]:
                        resp = show_warning("Warning: data collection", "Just a heads up, the data and background collection steps have differnt values.\nAre you sure you want to continue?")   
                        if not resp: return False

        ###################
        #   ANALYSIS TAB  #
        ###################
        if self.peak_min.value() >= self.peak_max.value():
            show_alert(self, 'Error!', 'Please ensure that a valid range is given for peak location (Analysis tab).')
            return False
        if self.g_sg.isChecked() and signal_steps:
            freq = self.dt.value()
            dur = signal_steps[0][g.M_T]
            samples = int(freq * dur)
            if self.sg_window.value() >= samples:
                show_alert(self, 'Error!', 'The Savitzky-Golay window must be smaller than '+str(samples)+', the total number of data points collected (Analysis tab).')
                return False
            if self.sg_order.value() >= self.sg_window.value():
                show_alert(self, 'Error!', 'The Savitzky-Golay order must be smaller than the window size (Analysis tab).')
                return False
           
        ###################
        #   CALC TAB      #
        ###################
        if not self.dl.value():
            resp = show_warning("Warning: calculation settings", "No detection limit has been set (Calculation tab).\nAre you sure you want to continue?")   
            if not resp: return False
            
        
        return True


    def refresh_graph(self):
        lbls = True
        if self.hide_plot_lbls.checkState() == Qt.CheckState.Checked:
            lbls = False
        self.graph.update_plot(self.steps, self.relays, show_labels=lbls, show_xticks=lbls)

    def set_header(self):  
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT :
            self.setWindowTitle('Method Builder | '+self.name.text())   
        else:
            self.setWindowTitle('View method | '+self.name.text())

    def ramp_scan_rate_to_duration(self):

        scan_rate = self.ramp_scan_rate.value()
        v0 = self.ramp_v_start.value()
        v1 = self.ramp_v_end.value()
        return abs(v0-v1)/scan_rate

    def ramp_duration_to_scan_rate(self, v0, v1, duration):
        return round(abs(v0-v1)/duration, 2)

    def set_duration(self, step_type):
        if step_type == g.M_RAMP:
            dur = self.ramp_scan_rate_to_duration()
            self.ts[step_type].setValue(dur)

    #########################################
    #                                       #
    #   Window show/hide event handlers     #
    #                                       #
    #   1. closeEvent                       # 
    #   2. accept_close                     #
    #                                       #
    #########################################
    def update_win(self):
        """Necessary function, called by parent, when data is updated. Please, do not delete!"""
        return
        
    def closeEvent(self, event):
        if not self.saved:
            confirm = saveMessageBox()
            resp = confirm.exec()
            if resp == QMessageBox.StandardButton.Save:
                event.ignore()
                self.close_on_save = True
                self.start_save()
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
        self.parent.children.remove(self)
        closeEvent.accept()
        
        
            
        
