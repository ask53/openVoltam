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

from PyQt6.QtGui import QIcon, QPixmap
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
    QScrollArea,
    QComboBox,
    QTabWidget,
    QApplication
    
    )

class WindowEditSweepProfile(QMainWindow):
    def __init__(self, path=False, uid=False):
        super().__init__()
        self.path = False
        self.steps = []
        self.selected = []
        self.editing = False
        self.adding = False

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
        self.g1 = QGroupBox(l.sp_add_step[g.L])
        v4 = QVBoxLayout()
        self.s1 = QStackedLayout()

        
        
        
        

        self.graph = QScrollArea()
        self.name = QLineEdit()
        self.name.setObjectName('ov-profile-name')
        self.name.setPlaceholderText('Profile name')

        dt_lbl = QLabel('dt')
        self.dt = QDoubleSpinBox()

        step_name_lbl = QLabel('Step name')
        self.step_name = QLineEdit()
        self.step_name.setMaxLength(8)

        self.stirrer = QCheckBox('Stirrer on during step?')
        self.vibrator = QCheckBox('Vibrator on during step?')
        
        step_type_lbl = QLabel('Step type')
        self.step_type = QComboBox()                                        # Create dropdown menu
        self.step_type.setPlaceholderText('Select...')                      # Add placeholder text for when nothing is selected
        for sp_type in g.SP_TYPES:                                          # Loop thru types (defined in globals)
            self.step_type.addItem(l.sp_types[sp_type][g.L])                # Add each type to the dropdown menu
        self.step_type.currentIndexChanged.connect(self.step_type_changed)  # Each time the dropdown selection is changed, connect to fn

        
        # Set up type-specific parameters if the user selects CONSTANT VOLTAGE'
        v_const = QVBoxLayout()
        v_const_collect = QVBoxLayout()
        g_const_collect = QGroupBox('Data collection')
        
        const_v_lbl = QLabel('Voltage [V]')
        self.const_v = QDoubleSpinBox()
        self.const_v.setMinimum(g.SP_V_MIN)
        const_t_lbl = QLabel('Duration [s]')
        const_t = QDoubleSpinBox()
        const_t.setMaximum(g.SP_T_MAX)
        
        const_collect_start = QCheckBox('Begin collecting data')
        const_collect_start.setObjectName('const-collect-start')
        const_collect_start.stateChanged.connect(partial(self.collection_state_changed, const_collect_start))
        const_collect_end = QCheckBox('Stop collecting data')
        const_collect_end.setObjectName('const-collect-end')
        const_collect_end.stateChanged.connect(partial(self.collection_state_changed, const_collect_end))
        const_collect_start_t_lbl = QLabel('Begin collection at [s]')
        const_collect_start_t = QDoubleSpinBox()
        const_collect_start_t.setMaximum(g.SP_T_MAX)
        const_collect_end_t_lbl = QLabel('Stop collection at [s]')
        const_collect_end_t = QDoubleSpinBox()
        const_collect_end_t.setMaximum(g.SP_T_MAX)

        w_const_collect_start = QWidget()
        w_const_collect_start.setLayout(horizontalize([const_collect_start_t_lbl, const_collect_start_t]))
        w_const_collect_start.setObjectName('const-collect-start-layout')
        w_const_collect_end = QWidget()
        w_const_collect_end.setLayout(horizontalize([const_collect_end_t_lbl, const_collect_end_t]))
        w_const_collect_end.setObjectName('const-collect-end-layout')

        v_const_collect.addWidget(const_collect_start)
        v_const_collect.addWidget(w_const_collect_start)
        v_const_collect.addWidget(const_collect_end)
        v_const_collect.addWidget(w_const_collect_end)
        v_const_collect.addStretch()
        g_const_collect.setLayout(v_const_collect)
        
        v_const.addLayout(horizontalize([const_v_lbl, self.const_v]))
        v_const.addLayout(horizontalize([const_t_lbl, const_t]))
        v_const.addWidget(g_const_collect)
        v_const.addStretch()
        w_const = QWidget()
        w_const.setLayout(v_const)
        

        # Set up type-specific parameters if the user selects VOLTAGE RAMP (Ramps from V1 to V2 over time)
        v_ramp = QVBoxLayout()
        v_ramp_collect = QVBoxLayout()
        g_ramp_collect = QGroupBox('Data collection')
        
        ramp_v_start_lbl = QLabel('Start voltage [V]')
        self.ramp_v_start = QDoubleSpinBox()
        self.ramp_v_start.setMinimum(g.SP_V_MIN)
        ramp_v_end_lbl = QLabel('End voltage [V]')
        self.ramp_v_end = QDoubleSpinBox()
        self.ramp_v_end.setMinimum(g.SP_V_MIN)
        ramp_t_lbl = QLabel('Duration [s]')
        ramp_t = QDoubleSpinBox()
        ramp_t.setMaximum(g.SP_T_MAX)
        
        ramp_collect_start = QCheckBox('Begin collecting data')
        ramp_collect_start.setObjectName('ramp-collect-start')
        ramp_collect_start.stateChanged.connect(partial(self.collection_state_changed,ramp_collect_start))
        ramp_collect_end = QCheckBox('Stop collecting data')
        ramp_collect_end.setObjectName('ramp-collect-end')
        ramp_collect_end.stateChanged.connect(partial(self.collection_state_changed,ramp_collect_end))
        ramp_collect_start_v_lbl = QLabel('Begin collection at [V]')
        ramp_collect_start_v = QDoubleSpinBox()
        ramp_collect_start_v.setMinimum(g.SP_V_MIN)
        ramp_collect_end_v_lbl = QLabel('Stop collection at [V]')
        ramp_collect_end_v = QDoubleSpinBox()
        ramp_collect_end_v.setMinimum(g.SP_V_MIN)

        w_ramp_collect_start = QWidget()
        w_ramp_collect_start.setLayout(horizontalize([ramp_collect_start_v_lbl, ramp_collect_start_v]))
        w_ramp_collect_start.setObjectName('ramp-collect-start-layout')
        w_ramp_collect_end = QWidget()
        w_ramp_collect_end.setLayout(horizontalize([ramp_collect_end_v_lbl, ramp_collect_end_v]))
        w_ramp_collect_end.setObjectName('ramp-collect-end-layout')

        v_ramp_collect.addWidget(ramp_collect_start)
        v_ramp_collect.addWidget(w_ramp_collect_start)
        v_ramp_collect.addWidget(ramp_collect_end)
        v_ramp_collect.addWidget(w_ramp_collect_end)
        v_ramp_collect.addStretch()
        g_ramp_collect.setLayout(v_ramp_collect)
        
        v_ramp.addLayout(horizontalize([ramp_v_start_lbl, self.ramp_v_start]))
        v_ramp.addLayout(horizontalize([ramp_v_end_lbl, self.ramp_v_end]))
        v_ramp.addLayout(horizontalize([ramp_t_lbl, ramp_t]))
        v_ramp.addWidget(g_ramp_collect)
        v_ramp.addStretch()
        w_ramp = QWidget()
        w_ramp.setLayout(v_ramp)
        
        # Organize measurement widgets into lists to itterate over

        self.ts = {g.SP_CONSTANT: const_t,
                   g.SP_RAMP: ramp_t}
        self.measure_starts = {g.SP_CONSTANT: const_collect_start,
                               g.SP_RAMP: ramp_collect_start}
        self.measure_stops = {g.SP_CONSTANT: const_collect_end,
                              g.SP_RAMP: ramp_collect_end}
        self.measure_start_ts = {g.SP_CONSTANT: const_collect_start_t,
                                 g.SP_RAMP: ramp_collect_start_v}
        self.measure_stop_ts = {g.SP_CONSTANT: const_collect_end_t,
                                g.SP_RAMP: ramp_collect_end_v}
        

        self.hidden_inputs = [w_const_collect_start,
                              w_const_collect_end,
                              w_ramp_collect_start,
                              w_ramp_collect_end]

        # Load the widgets into the stacked layout in order 
        self.s1.addWidget(QWidget())
        self.s1.addWidget(w_const)
        self.s1.addWidget(w_ramp)

        self.but_add_step = QPushButton(l.sp_add_btn[g.L])
        self.but_add_step.clicked.connect(self.add_step)

        v4.addLayout(horizontalize([step_name_lbl,self.step_name]))
        v4.addWidget(self.stirrer)
        v4.addWidget(self.vibrator)
        v4.addLayout(horizontalize([step_type_lbl,self.step_type]))
        v4.addLayout(self.s1)
        v4.addWidget(self.but_add_step)

        
                          
                                
                                
        
        self.g1.setLayout(v4)           
        policy = self.g1.sizePolicy()           # get existing size policy of g1
        policy.setRetainSizeWhenHidden(True)    # modify policy so that g1 takes up space regardless of whether shown or hidden
        self.g1.setSizePolicy(policy)           # set g1's size policy to the modified version.
        
        self.profile_chart = QScrollArea()          # Initialize scroll area
        
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
        
        v3.addWidget(self.profile_chart)
        v3.addLayout(horizontalize([but_up, but_down]))
        v3.addLayout(horizontalize([self.but_add, self.but_edit, but_dup, but_del]))
        
        h2.addWidget(self.g1)
        h2.addLayout(v3)
        
        w_custom = QWidget()
        w_custom.setLayout(h2)    # update this with custom layout! 
        w_standard = QLabel('nothing here yet...')

        self.builder = QTabWidget()
        self.builder.setTabPosition(QTabWidget.TabPosition.North)
        self.builder.addTab(w_custom, 'custom')
        self.builder.addTab(w_standard, 'standard')

        
        
        but_save = QPushButton('Save')

        v2.addWidget(self.name)
        v2.addStretch()
        v2.addLayout(horizontalize([dt_lbl, self.dt], True))
        
        
        h1.addLayout(v2)
        h1.addWidget(self.graph)
        
        v1.addLayout(h1)
        v1.addWidget(self.builder)
        v1.addWidget(but_save)

        self.init_form_values()
        self.hide_new_step_pane()
        
        w = QWidget()
        w.setLayout(v1)
        self.setCentralWidget(w)
        self.update_buttons()

    def init_form_values(self):
        # Modify title and button text
        self.g1.setTitle(l.sp_add_step[g.L])
        self.but_add_step.setText(l.sp_add_btn[g.L])
        
        # Reset all values common to all runs
        self.step_name.setText('')
        self.stirrer.setCheckState(Qt.CheckState.Unchecked)
        self.vibrator.setCheckState(Qt.CheckState.Unchecked)
        self.step_type.setCurrentIndex(g.QT_NOTHING_SELECTED_INDEX)

        # Reset values specific to constant voltage steps

        self.const_v.setValue(0)

        # Reset values specific to voltage ramp steps
        self.ramp_v_start.setValue(0)
        self.ramp_v_end.setValue(0)

        # Reset values related to measurement
        for sp_type in g.SP_TYPES:
            self.ts[sp_type].setValue(0)
            self.measure_starts[sp_type].setCheckState(Qt.CheckState.Unchecked)
            self.measure_stops[sp_type].setCheckState(Qt.CheckState.Unchecked)
            self.measure_start_ts[sp_type].setValue(0)
            self.measure_stop_ts[sp_type].setValue(0)

        # Hide inputs that only appear when checkbox is selected
        for w in self.hidden_inputs:
            w.hide()

    def set_form_values(self, step):
        # Modify title and button text
        self.g1.setTitle(l.sp_edit_step[g.L])
        self.but_add_step.setText(l.sp_edit_btn[g.L])

        ##################################################
        #
        #   HERE, FINISH PUTTING VALUES INTO THE FORM
        #
        ############################################################################################

        

    def refresh_list(self):
        """ Clears the sweep list and rebuilds it"""
        try:
            self.erase_list_visualization()
            self.build_new_list()
            self.update_highlights()
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
        buts_to_enable = []
        buts_to_disable = []
        if self.editing:
            buts_to_disable = self.buts_inactive_while_editing
        elif self.adding:
            buts_to_disable = self.buts_inactive_while_adding
        elif len(self.selected) == 0:
            buts_to_disable = self.buts_one_selected + self.buts_mult_selected
            buts_to_enable = [self.but_add]
        elif len(self.selected) == 1:
            buts_to_enable = self.buts_one_selected + self.buts_mult_selected  + [self.but_add]
        else:
            buts_to_disable = self.buts_one_selected
            buts_to_enable = self.buts_mult_selected
        
        for but in buts_to_disable:
            but.setEnabled(False)
        for but in buts_to_enable:
            but.setEnabled(True)

            
                


    def build_new_list(self):

        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)

        
        for i, step in enumerate(self.steps):
            #### TO ADD MORE WIDGETS TO THIS LAYOUT, DEFINE THEM HERE
            step_type = step[g.SP_TYPE]
            w_name = QLabel(step[g.SP_NAME])
            
            
            w_volt = QLabel()
            if step_type == g.SP_CONSTANT:
                w_volt = QLabel('const: '+str(step[g.SP_CONST_V])+'V')
            elif step_type == g.SP_RAMP:
                w_volt.setText('ramp: '+str(step[g.SP_RAMP_V1])+'V'+' --> '+str(step[g.SP_RAMP_V2])+'V')
            

            w_t = QLabel(str(step[g.SP_T])+'s')

            w_stir = QLabel()
            w_stir.setToolTip('Stirrer OFF')
            if step[g.SP_STIR]:
                w_stir.setPixmap(QPixmap(g.ICON_STIR))
                w_stir.setToolTip('Stirrer ON')

            w_vib = QLabel()
            w_vib.setToolTip('Vibrator OFF')
            if step[g.SP_VIBRATE]:
                w_vib.setPixmap(QPixmap(g.ICON_VIB))
                w_vib.setToolTip('Vibrator ON')

            w_collect = QLabel('m')
            
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
        if self.editing:                                            # If there is an edit in process, 
            return                                                  # block the user from modifying the rows at all
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
    ###############################################################################################################################################    
    def edit_step(self):
        try:
            if self.g1.isHidden():
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
        self.set_form_values(step)
        self.g1.show()
        

    def hide_edit_step(self):
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))
        self.g1.hide()                              # hide the add/edit step pane
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
        self.s1.setCurrentIndex(i+1) # the +1 allows for the 0th screen to be empty


    def collection_state_changed(self, checkbox, state):
        
        """This runs when a checkbox is supposed to hide/display some other
        content each time it is toggled. Works by finding the layout to
        toggle based on the checkbox's assigned name and the layout's corresponding
        name. More specifically, the layout must
            (a) be wrapped in a QWidget and
            (b) have the name: [checkbox name]-layout.
        So if the checkbox's name is 'steve', then the QWidget that wraps the
        layout must be named 'steve-layout'. If the checkbox is selected, then the
        layout will be shown. Otherwise it will be hidden"""
        
        lay = self.findChild(QWidget, checkbox.objectName()+'-layout')
        if state == Qt.CheckState.Checked.value:
            lay.show()
        else:
            lay.hide()
        
        
    def add_new_step(self):
        if self.g1.isHidden():
            self.show_new_step_pane()
        else:
            self.hide_new_step_pane()

    def show_new_step_pane(self):
        self.adding = True
        self.update_buttons()
        self.g1.show()
        self.but_add.setIcon(QIcon(g.ICON_X))

    def hide_new_step_pane(self):
        self.g1.hide()                              # hide the pane
        self.but_add.setIcon(QIcon(g.ICON_PLUS))    # make sure the add icon is a + (instead of an x) 
        self.but_edit.setIcon(QIcon(g.ICON_EDIT))    # make sure the add icon is a + (instead of an x) 
        self.adding = False
        self.editing = False
        self.init_form_values()                     # and wipe the form
        self.update_buttons()
        

    def add_step(self):
        if self.validate_step():
            step_type = g.SP_TYPES[self.step_type.currentIndex()]
            self.convert_measurement_voltages_to_time()

            # Grab the data that all steps contain   
            data_general = {
                g.SP_NAME: self.step_name.text(),
                g.SP_STIR: self.is_checked(self.stirrer),
                g.SP_VIBRATE: self.is_checked(self.vibrator),
                g.SP_TYPE: step_type
                }
            
            # Grab the data related to measurement 
            data_measurement = {
                g.SP_START_COLLECT: self.is_checked(self.measure_starts[step_type]),
                g.SP_END_COLLECT: self.is_checked(self.measure_stops[step_type]),
                g.SP_T: self.ts[step_type].value()
                }
            if data_measurement[g.SP_START_COLLECT]:
                data_measurement[g.SP_START_COLLECT_T] = self.measure_start_ts[step_type].value()
            if data_measurement[g.SP_END_COLLECT]:
                data_measurement[g.SP_END_COLLECT_T] = self.measure_stop_ts[step_type].value() 

            ############################################ IF ADDING ANOTHER STEP TYPE, ADD ANOTHER ELIF TO THE CODE BELOW ############
            data_specific = {}                                                                                                      #
            if step_type == g.SP_CONSTANT:                                                                                          #
                data_specific = {                                                                                                   #
                    g.SP_CONST_V: self.const_v.value()                                                                              #                                                                                 #
                    }                                                                                                               #
                                                                                                                                    #
            elif step_type == g.SP_RAMP:                                                                                            #
                data_specific = {                                                                                                   #
                    g.SP_RAMP_V1: self.ramp_v_start.value(),                                                                        #
                    g.SP_RAMP_V2: self.ramp_v_end.value()                                                                           #
                    }                                                                                                               #
            #########################################################################################################################

            # combine all of the above created dictionaries and store them

            new_step = data_general | data_measurement | data_specific
            if self.adding:
                self.steps.append(new_step)
            elif self.editing:
                i = self.selected[0]
                self.steps[i] = new_step
            self.selected = []          # clears selection and will clear highlights when list is refreshed
            self.refresh_list()         # refresh the list (to visualize the new row and clear stale highlights)
            self.hide_new_step_pane()   # close the pane that allows the user to add a new step
            self.init_form_values()     # reset the hidden pane to initial values
            print(self.steps)
        

    def is_checked(self, checkbox):
        if checkbox.checkState() == Qt.CheckState.Checked:
            return True
        return False

    def validate_step(self):
        #########################33##########
        #
        #   FOR TESTING ONLY, COMMENT TO RUN
        return True
        #
        #
        #####################################
        
        if self.step_type.currentIndex() == g.QT_NOTHING_SELECTED_INDEX:    # make sure there is a type selected
            show_alert(self, 'Error!', 'Please select a type of run')
            return False
        step_type = g.SP_TYPES[self.step_type.currentIndex()]
        if self.ts[step_type].value() == 0:                                   # make sure there is a duration
            show_alert(self, 'Error!', 'Please set a duration longer than 0 for this step')
            return False
        if step_type == g.SP_CONSTANT:
            t = self.ts[step_type].value()
            if self.is_checked(self.measure_starts[step_type]):
                if self.measure_start_ts[step_type].value() > t:
                    show_alert(self, 'Error!', 'Please check the measurement start time, it seems to be longer than the duration of this step.')
                    return False
            if self.is_checked(self.measure_stops[step_type]):
                if self.measure_stop_ts[step_type].value() > t:
                    show_alert(self, 'Error!', 'Please check the measurement stop time, it seems to be longer than the duration of this step.')
                    return False
        if step_type == g.SP_RAMP:
            v1 = self.ramp_v_start.value()
            v2 = self.ramp_v_end.value()
            if v1 == v2:
                show_alert(self, 'Error!', 'The endpoints of this ramp have the same value, if this is what you want, please consider a constant volutage. Otherwise...typo?')
                return False
            if self.is_checked(self.measure_starts[step_type]):
                if not self.is_between(self.measure_start_ts[step_type].value(), v1, v2):
                    show_alert(self, 'Error!', 'Please check the measurement start voltage, its out of the voltage range of this step.')
                    return False
            if self.is_checked(self.measure_stops[step_type]):
                if not self.is_between(self.measure_stop_ts[step_type].value(), v1, v2):
                    show_alert(self, 'Error!', 'Please check the measurement stop voltage, its out of the voltage range of this step.')
                    return False
        if self.is_checked(self.measure_starts[step_type]) and self.is_checked(self.measure_stops[step_type]):
            if self.measure_start_ts[step_type].value() == self.measure_stop_ts[step_type].value():
                show_alert(self, 'Error!', 'It is very challenging to both begin and stop collecting data at the exact same time, please check those parameters.')
                return False
        return True

    

    def is_between(self, val, x1, x2):
        """returns true if val is between x1 and x2, inclusive.
        Otherwise, returns false"""
        
        v1 = min(x1, x2)
        v2 = max(x1, x2)
        if (val >= v1 and val <= v2):
            return True
        return False

    def calc_time_from_voltage(self, v1, v2, vm, t):
        return t*(vm-v1)/(v2-v1)

    def convert_measurement_voltages_to_time(self):
        """ Asumes form is filled out correctly (ie. has been validated"""
        step_type = g.SP_TYPES[self.step_type.currentIndex()]

        if step_type == g.SP_RAMP:
            v1 = self.ramp_v_start.value()                                                                        
            v2 = self.ramp_v_end.value()
            t = self.ts[step_type].value()
            if self.is_checked(self.measure_starts[step_type]):
                vm = self.measure_start_ts[step_type].value()
                self.measure_start_ts[step_type].setValue(self.calc_time_from_voltage(v1, v2, vm, t))
            if self.is_checked(self.measure_stops[step_type]):
                vm = self.measure_stop_ts[step_type].value()
                self.measure_stop_ts[step_type].setValue(self.calc_time_from_voltage(v1, v2, vm, t))

    '''def resize(self, event):
        try:
            outer = self.profile_chart
            inner = self.w_pc
            scroll_area_resized(outer, inner, event)
        except Exception as e:
            print(e)'''
      
