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

Thus the WindowMethod() object can either be passed a path to an .ovm file(as in
case #1) or a dictionary of data (as in case #2). When a path is given, the user
is given options for "save" (save changes to original path) and "save as" (save
changes to a new file, without modifying the original). When data is passed, the
user can only select "save" and will be prompted to decide where to save the file.

Both .ovs and .ovm files use tabular json format (an extension of json that allows
for tabular, comma-separated-value type data to be embedded within a json.

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

TABLE OF CONTENTS

A. Imports
B. WindowMethod()
    1. __init__(self, path=False, data=False, view_only=False, parent=False, view_only_edit=True)
        Initializes and opens window based on passed arguments
    
    2. init_form_values(self)
	initializes the values in the form to preset blank values
		
    3. set_values(self)
	Sets the values of the form to reflect the stored data of the
	method, either from the passed path or passed data
		
    4. set_step_values_for_editing(self, step)
	Sets the values of the step input form in preparation for editing.
	Pulls values from 'step' argument to fill form.
		
    5. refresh_list(self)
        Refreshes the list of steps to reflect the most updated steps saved
        
    6. erase_list_visualization(self)
        Erases the list of steps
        
    7. update_buttons(self)
        Based on the current status (adding a new step, editing an existing step, neither) and
        how many steps have been added, enables and disables the relevant buttons (up/down/add/edit/dup/delete).
        
    8. build_new_list(self)
        Builds a new list of steps with brand new widgets based on self.steps
        
    9. row_clicked(self, w, event)
        Event handler for clicking on widget 'w' in a row in the steps display.
        Can handle regular clicks and ctrl+click
        It manages which steps are currently selected in self.selected
        and manages which rows are highlighted.
        
    10. update_highlights(self)
        Makes sure correct rows (only those in self.selected) are highlighted
        
    11. change_row_highlight(self, i, to_highlight)
        either highlights row i if to_highlight == True or unhighlights it if not
    
    12. widget_is_highlighted(self, w):
        returns True if widget 'w' is highlighted, otherwise returns False.
        
    13. row_move_up(self)
        Moves all selected rows up one position.

    14. row_move_down(self)
        Moves all selected rows down one position.
        
    15. row_duplicate(self)
        Duplicates all selected rows and places each new row below the row of which it is a duplicate.
        
    16. edit_step(self)
        Event handler for click on "edit" button. Either opens the editing pane and loads values if
        nothing is currently being edited. Otherwise, closes the editing pane.
        
    17. show_edit_step(self)
        Loads the relevant info from the selected step into the editing pane then shows the editing pane.
        
    18. hide_edit_step(self)
        Resets the values in the editing pane and hides it (does NOT save step)
        
    19. row_delete(self)
        Deletes all selected rows.
        
    20. blockify(self, i_list)
        Takes in a list of integers. Returns a list of lists where all consecutive integers
        have been grouped together in sub-lists, in the same order that the original list was
        passed. (See example in function description)
        
    21. step_type_changed(self, i)
        Event handler whenever the type is changed for a step. Pulls up a new layout
        from the stacked layout
        
    22. add_new_step(self)
        Event handler for click on "add" button. Either opens the step pane with blank values if
        no step is currently being added. Otherwise, closes the step pane.
        
    23. show_new_step_pane(self)
        Shows the add-new-step pane
    
    24. hide_new_step_pane(self)
        Resets and hides the new step pane
        
    25. add_step(self)
        Pulls all the data from the new step pane and validates it.
        If it is valid, adds the step to the end of the self.steps
        list, updates the step list, and resets and closes the step pane.
        
    26. is_checked(self, checkbox)
        Takes in a QCheckBox object and returns True if it is checked, False if not
        
    27. validate_step(self)
        A bunch of validation rule checks for a step that is being added or edited.
        If a rule is missed, it displays and alert and returns False.
        If all checks are passed, returns True.
        
    28. start_save(self, save_type)
        Event handler for someone pushing the "save" or "save as" button.
        First, validates the whole method. If valid,
        Calls the appropriate save function
        
    29. method_save_as(self)
        Asks the user to identify a location and filename to save, then callse
        the method_save() function.
        
    30. method_save(self)
        Pulls the method file together and saves it as an .osm file.
	
    31. validate_method(self)
        A bunch of validation rule checks for the overall method (either for a new method or one
        that is being edited).
        If a rule is missed, it displays and alert and returns False.
        If all checks are passed, returns True.
        
    32. refresh_graph(self)
        Using self.steps and the checkbox that determines whether or not labels are displayed
        on the graph, refreshes the graph to match the current steps.
        
    33. set_header(self)
        Sets the window header based on arguments and method name
        
    34. ramp_scan_rate_to_duration(self)
        converts the values entered in a ramp step for v1, v2, and scan rate
        into a duration in secords, returns the duraction.
        
    35. ramp_duration_to_scan_rate(self, v0, v1, duration)
        converts the passed arguments v0, v1, and duration into a scan rate
        returns the scan rate
        
    36. set_duration(self, step_type)
        takes in a step_type and, if it is a step where duration must be calculated
        from the user-entered parameters, calculates it and sets the hidden field,
        self.ts[step_type] to that duration. This requires that there is a hidden
        QDoubleSpinBox stored in the self.ts array for EVERY step type. 

UPDATE HISTORY

26-Nov-2025    aaron k    First draft of code and documentation complete


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

from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from wins.sample import QVLine
from embeds.methodPlot import MethodPlot

from functools import partial

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
        self.adding = False     # flag for whether step is being added
        self.editing = False    # flag for whether step is being edited
        self.close_on_save = False
        self.process = False
        self.save_error_flag = False
        self.steps = []
        self.selected = []
        self.status = self.statusBar()

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
        self.dt.valueChanged.connect(self.changed_value)

        current_range_lbl = QLabel("Device current range")  # Current range
        self.current_range = QComboBox()
        self.current_range.setPlaceholderText('Select...')
        for cr in g.CURRENT_RANGES:    
            self.current_range.addItem(cr)
        self.current_range.currentIndexChanged.connect(self.changed_value)

        # Graph stuff
        self.hide_plot_lbls = QCheckBox('Hide plot labels')
        self.hide_plot_lbls.stateChanged.connect(self.refresh_graph)
        self.graph = MethodPlot()
        graph_area = QScrollArea()
        graph_area.setObjectName('ov-graph-area')
        graph_area.setWidget(self.graph)
 
        self.profile_chart = QScrollArea()          # Initialize scroll area

        # Create buttons for the different window states
        self.but_new_save = QPushButton('Save')
        self.but_edit_save = QPushButton('Save')
        self.but_edit_save_as = QPushButton('Save as')
        self.but_view_only = QPushButton('Edit name')
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
        g1 = QGroupBox('Method parameters')
        g1.setLayout(v1)

        self.ws_for_new = [self.dt, self.current_range]
        self.ws_for_viewish = [self.name]

        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:     # if this window can actually edit the method steps

            # Step-specific inputs
            step_name_lbl = QLabel('Step name')
            self.step_name = QLineEdit()
            self.step_name.setMaxLength(8)

            self.data_collect = QCheckBox('Collect data during step?')
            self.stirrer = QCheckBox('Stirrer on during step?')
            self.vibrator = QCheckBox('Vibrator on during step?')
            
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

            # Set up the group box where user enters step information
            v2 = QVBoxLayout()
            v2.addLayout(horizontalize([step_name_lbl,self.step_name]))
            v2.addWidget(self.data_collect)
            v2.addWidget(QHLine())
            v2.addWidget(self.stirrer)
            v2.addWidget(self.vibrator)
            v2.addWidget(QHLine())
            v2.addLayout(horizontalize([step_type_lbl,self.step_type]))
            v2.addLayout(self.s_type)
            v2.addWidget(self.but_add_step)

            self.g_step = QGroupBox(l.sp_add_step[g.L]) 
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

            # Create vertical layout of the steps chart above the buttons
            v3 = QVBoxLayout()
            v3.addWidget(self.profile_chart)
            v3.addLayout(horizontalize([but_up, but_down]))
            v3.addLayout(horizontalize([self.but_add, self.but_edit, but_dup, but_del]))

            # Create horizontal layout of new-step pane and steps chart/buttons
            h1 = QHBoxLayout()
            h1.addWidget(self.g_step)
            h1.addLayout(v3)

            # Put it all inside tabs for custom and standard method builder...DELETE THIS?
            w_custom = QWidget()
            w_custom.setLayout(h1)    # update this with custom layout! 
            w_standard = QLabel('nothing here yet...')

            self.builder = QTabWidget()
            self.builder.setTabPosition(QTabWidget.TabPosition.North)
            self.builder.addTab(w_custom, 'custom')
            self.builder.addTab(w_standard, 'standard')

            v4 = QVBoxLayout()
            v4.addWidget(g1)
            v4.addStretch()
            v4.addWidget(self.hide_plot_lbls)

            h2 = QHBoxLayout()
            h2.addLayout(v4)
            h2.addWidget(graph_area)

            v5 = QVBoxLayout()
            v5.addWidget(self.name)
            v5.addLayout(h2)

            wtop = QWidget()
            wtop.setLayout(v5)
            
            split = QSplitter()
            split.setOrientation(Qt.Orientation.Vertical)
            split.addWidget(wtop)
            split.addWidget(self.builder)

            v6 = QVBoxLayout()
            v6.addWidget(split)
            w = QWidget()
            w.setLayout(v6)

        else:
            v1 = QVBoxLayout()
            h1 = QHBoxLayout()
            v2 = QVBoxLayout()
            h2 = QHBoxLayout()

            h2.addStretch()
            h2.addWidget(self.hide_plot_lbls)
            v2.addWidget(g1)
            v2.addWidget(self.profile_chart)
            v2.addLayout(h2)
            h1.addLayout(v2)
            h1.addWidget(self.graph)
            v1.addWidget(self.name)
            v1.addLayout(h1)

            w = QWidget()
            w.setLayout(v1)

        self.setCentralWidget(w)
        
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
            self.hide_new_step_pane()
            self.init_form_values()
        if not self.mode == g.WIN_MODE_NEW: 
            try:
                self.set_values()
            except Exception as e:
                print('here!')
                print(e)


        if self.mode == g.WIN_MODE_NEW:
            self.set_mode_new()
        elif self.mode == g.WIN_MODE_EDIT:
            self.set_mode_edit()
        elif self.mode == g.WIN_MODE_VIEW_WITH_MINOR_EDITS:
            self.set_mode_viewish()
        else:
            self.set_mode_view()

        self.saved = True
        
            
            

    def init_form_values(self):
        # Modify title and button text
        self.g_step.setTitle(l.sp_add_step[g.L])
        self.but_add_step.setText(l.sp_add_btn[g.L])
        
        # Reset all values common to all runs
        self.step_name.setText('')
        self.data_collect.setCheckState(Qt.CheckState.Unchecked)
        self.stirrer.setCheckState(Qt.CheckState.Unchecked)
        self.vibrator.setCheckState(Qt.CheckState.Unchecked)
        self.step_type.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)

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

    def set_values(self):
        if self.path:                                   # if there is a path to a method file,
            data = get_data_from_file(self.path)        #   get the most up to date data from the file
        elif self.method_id:                            # otherwise, if there is a method id given,
            data = get_method_from_file_data(self.parent.data, self.method_id)   #  use it to grab the method data
        self.name.setText(data[g.M_NAME])               # set name
        self.dt.setValue(data[g.M_SAMPLE_FREQ])                  # set dt
        cr_text = data[g.M_CURRENT_RANGE]               # set current range
        self.current_range.setCurrentIndex(g.CURRENT_RANGES.index(cr_text))
        self.steps = data[g.M_STEPS]                    # set steps 
        self.refresh_list()                             # rebuild visual steps list based on self.steps

    #####################################
    #                                   #
    #   Handlers for changed widgets    #
    #                                   #
    #####################################

    def changed_name(self):
        self.saved = False
        self.set_header()
        self.status.showMessage('')

    def changed_value(self):
        self.saved = False
        self.status.showMessage('')

    

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

    def set_mode_edit(self):
        self.mode = g.WIN_MODE_EDIT
        self.set_header()
        self.set_button_bar([self.but_edit_save, self.but_edit_save_as])
        self.toggle_widget_editability()

    def set_mode_view(self):
        self.mode = g.WIN_MODE_VIEW_ONLY
        self.set_header()
        self.set_button_bar([self.but_view_only])
        self.toggle_widget_editability()

    def set_mode_viewish(self):
        self.mode = g.WIN_MODE_VIEW_WITH_MINOR_EDITS
        self.set_header()
        self.set_button_bar([self.but_edit_name_only])
        self.toggle_widget_editability()
        self.name.setText(self.name.text())             # This just sets the name text again and moves the cursor to the name field
        self.name.setSelection(0,len(self.name.text())) # Highlight name

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











    
    def set_step_values_for_editing(self, step):
        self.init_form_values()                     # initialize all form values
        
        # Modify title and button text
        self.g_step.setTitle(l.sp_edit_step[g.L])
        self.but_add_step.setText(l.sp_edit_btn[g.L])

        # Set top values to values from step
        self.step_name.setText(step[g.M_STEP_NAME])
        
        if step[g.M_DATA_COLLECT]:
            self.data_collect.setCheckState(Qt.CheckState.Checked)
        
        if step[g.M_STIR]:
            self.stirrer.setCheckState(Qt.CheckState.Checked)

        if step[g.M_VIBRATE]:
            self.vibrator.setCheckState(Qt.CheckState.Checked)

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
            self.erase_list_visualization()
            self.build_new_list()
            self.refresh_graph()
            self.update_highlights()
            if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
                self.update_buttons()
        except Exception as e:
            print(e)

    def erase_list_visualization(self):
        """ Erases the content of the current sweep list that is displayed"""
        w = self.profile_chart.findChild(QWidget)
        lay = w.layout()
        try:
            for i in reversed(range(lay.count())): 
                lay.itemAt(i).widget().setParent(None)
        except:
            return

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

            w_stir = QLabel()
            w_stir.setToolTip('Stirrer OFF')
            if step[g.M_STIR]:
                w_stir.setPixmap(QPixmap(g.ICON_STIR))
                w_stir.setToolTip('Stirrer ON')

            w_vib = QLabel()
            w_vib.setToolTip('Vibrator OFF')
            if step[g.M_VIBRATE]:
                w_vib.setPixmap(QPixmap(g.ICON_VIB))
                w_vib.setToolTip('Vibrator ON')

            w_collect = QLabel()
            w_collect.setToolTip('Data collection OFF')
            if step[g.M_DATA_COLLECT]:
                w_collect.setPixmap(QPixmap(g.ICON_MEASURE))
                w_collect.setToolTip('Data collection ON')
            
            ws = [w_name, w_volt, w_t, w_stir, w_vib, w_collect]
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
                self.steps.insert(i+rows_added+len(block), self.steps[i+rows_added])#   insert the duplicate row there!
            rows_added = rows_added + len(block)                                    # add the adjustment for going forwards thru th list
        self.selected = new_selected
        self.refresh_list()
        self.changed_value()

    def edit_step(self):
        try:
            if self.g_step.isHidden():
                self.show_edit_step()
            else:
                self.hide_edit_step()
                
        except Exception as e:
            print(e)

    def show_edit_step(self):
        self.editing = True
        self.update_buttons()
        self.but_edit.setIcon(QIcon(g.ICON_X))
        step = self.steps[self.selected[0]]
        self.set_step_values_for_editing(step)
        self.g_step.show()
        

    def hide_edit_step(self):
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))
        self.g_step.hide()                              # hide the add/edit step pane
        self.init_form_values()                     # and wipe the form 
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

    def hide_new_step_pane(self):
        self.g_step.hide()                              # hide the pane
        self.but_add.setIcon(QIcon(g.ICON_PLUS))    # make sure the add icon is a + (instead of an x) 
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))    # make sure the add icon is a + (instead of an x) 
        self.adding = False
        self.editing = False
        self.init_form_values()                     # and wipe the form
        self.update_buttons()
        

    def add_step(self):
        
        if self.validate_step():
            step_type = g.M_TYPES[self.step_type.currentIndex()]

            self.set_duration(step_type)
            
            # Grab the data that all steps contain   
            data_general = {
                g.M_STEP_NAME: self.step_name.text(),
                g.M_DATA_COLLECT: self.is_checked(self.data_collect),
                g.M_STIR: self.is_checked(self.stirrer),
                g.M_VIBRATE: self.is_checked(self.vibrator),
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
            self.init_form_values()     # reset the hidden pane to initial values
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
        '''if self.step_name.text() == '':    # make sure there is a name selected
            show_alert(self, 'Error!', 'Please name your step')
            return False'''
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
            if self.ramp_scan_rate == 0:
                show_alert(self, 'Error!', 'Please set a scan rate greater than 0.')
                return False
            
        return True

    def start_save(self, save_as=False):
        if self.saved:
            self.status.showMessage('Method saved.', g.SB_DURATION)
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
            return                              # don't try to save, just return
        self.method_save()                      # save the file!

    def method_save(self):
        data = {g.M_NAME: self.name.text(),
                g.M_SAMPLE_FREQ: self.dt.value(),
                g.M_CURRENT_RANGE: self.current_range.currentText(),
                g.M_STEPS: self.steps}
        if self.mode == g.WIN_MODE_NEW or self.mode == g.WIN_MODE_EDIT:
            self.start_async_overwrite(data)
        else:
            self.status.showMessage('Saving method...')
            data[g.M_UID_SELF] = self.method_id
            self.parent.start_async_save(g.SAVE_TYPE_METHOD_MOD, [self.method_id, data], onSuccess=self.after_save_method_success, onError=self.after_save_method_error)

    def start_async_overwrite(self, toWrite):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_overwrite_stdout)
        self.process.readyReadStandardError.connect(self.handle_overwrite_stderr)
        self.process.finished.connect(partial(self.handle_finished_overwrite))

        self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_OVERWRITE, self.path, str(toWrite)])
        self.status.showMessage("Saving method...")

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

    def after_save_method_error(self):
        self.status.showMessage('ERROR: Method did not save.', g.SB_DURATION_ERROR)
        self.set_buttons_enabled()



    def validate_method(self):
        if not self.name.text():                                                                # if there is no method name
            show_alert(self, 'Error!', 'Please name this method.')
            return False
        elif len(self.name.text()) < 3:                                                         # if method name is too short
            show_alert(self, 'Error!', 'Method name must contain at least three characters.')
            return False
        elif self.dt.value() == float(0):                                                       # if there is no dt set
            show_alert(self, 'Error!', 'Please select a sample frequency greater than 0.')
            return False
        elif self.current_range.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:                  # if there is no current range selected
            show_alert(self, 'Error!', 'Please select a current range.')
            return False
        elif len(self.steps) == 0:                                                              # if no steps have been added
            show_alert(self, 'Error!', 'Please add at least one step to the method.')
            return False
      
        return True

    def refresh_graph(self):
        lbls = True
        if self.hide_plot_lbls.checkState() == Qt.CheckState.Checked:
            lbls = False
        self.graph.update_plot(self.steps, show_labels=lbls, show_xticks=lbls)

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
            confirm = saveMessageBox(self)
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
        
        
            
        
