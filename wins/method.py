"""
method.py

This file defines a class WindowMethod which creates a window object
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

from wins.sample import QVLine
from embeds.methodPlot import MethodPlot

from functools import partial
from tkinter.filedialog import asksaveasfilename as askSaveAsFileName

from PyQt6.QtCore import Qt
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
    QSplitter,
    QScrollArea,
    QComboBox,
    QTabWidget,
    QApplication
    
    )

class WindowMethod(QMainWindow):
    def __init__(self, path=False, data=False, uid=False, view_only=False, parent=False, view_only_edit=True):
        super().__init__()
        self.steps = []
        self.selected = []
        self.editing = False
        self.adding = False
        self.view_only = view_only
        self.path = path
        self.data = data
        

        v1 = QVBoxLayout()
        v1top = QVBoxLayout()
        v1bot = QVBoxLayout()
        h1 = QHBoxLayout()
        v2 = QVBoxLayout()
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()
        self.g1 = QGroupBox(l.sp_add_step[g.L])
        v4 = QVBoxLayout()
        self.s1 = QStackedLayout()
        g2 = QGroupBox('Method parameters')
        v5 = QVBoxLayout()
        split1 = QSplitter()
        split1.setOrientation(Qt.Orientation.Vertical)

        
        
        
        

        
        
        self.name = QLineEdit()
        self.name.setObjectName('ov-method-name')
        self.name.setPlaceholderText('Profile name')
        self.name.textChanged.connect(self.set_header)

        
        
        
        # Define method-wide parameters
        dt_lbl_0 = QLabel('Sample every')
        self.dt = QDoubleSpinBox()
        dt_lbl_1 = QLabel('second(s).')

        current_ranges = ['1uA', '10 uA', '100 uA', '1,000 uA', '10,000 uA']
        current_range_lbl = QLabel("Device current range")
        self.current_range = QComboBox()
        self.current_range.setPlaceholderText('Select...')
        for cr in current_ranges:    
            self.current_range.addItem(cr)

        # Graph stuff
        self.hide_plot_lbls = QCheckBox('Hide plot labels')
        self.hide_plot_lbls.stateChanged.connect(self.refresh_graph)
        self.graph = MethodPlot()
        graph_area = QScrollArea()
        graph_area.setObjectName('ov-graph-area')
        graph_area.setWidget(self.graph)
        
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

        
        # Set up type-specific parameters if the user selects CONSTANT VOLTAGE'
        v_const = QVBoxLayout()
        
        const_v_lbl = QLabel('Voltage [V]')
        self.const_v = QDoubleSpinBox()
        self.const_v.setMinimum(g.M_V_MIN)
        const_t_lbl = QLabel('Duration [s]')
        const_t = QDoubleSpinBox()
        const_t.setMaximum(g.M_T_MAX)
        
        v_const.addLayout(horizontalize([const_v_lbl, self.const_v]))
        v_const.addLayout(horizontalize([const_t_lbl, const_t]))
        v_const.addStretch()
        w_const = QWidget()
        w_const.setLayout(v_const)
        

        # Set up type-specific parameters if the user selects VOLTAGE RAMP (Ramps from V1 to V2 over time)
        v_ramp = QVBoxLayout()
        
        ramp_v_start_lbl = QLabel('Start voltage [V]')
        self.ramp_v_start = QDoubleSpinBox()
        self.ramp_v_start.setMinimum(g.M_V_MIN)
        ramp_v_end_lbl = QLabel('End voltage [V]')
        self.ramp_v_end = QDoubleSpinBox()
        self.ramp_v_end.setMinimum(g.M_V_MIN)
        ramp_t_lbl = QLabel('Duration [s]')
        ramp_t = QDoubleSpinBox()
        ramp_t.setMaximum(g.M_T_MAX)
        
        v_ramp.addLayout(horizontalize([ramp_v_start_lbl, self.ramp_v_start]))
        v_ramp.addLayout(horizontalize([ramp_v_end_lbl, self.ramp_v_end]))
        v_ramp.addLayout(horizontalize([ramp_t_lbl, ramp_t]))
        v_ramp.addStretch()
        w_ramp = QWidget()
        w_ramp.setLayout(v_ramp)
        
        # Organize some repeated widgets into lists to itterate over

        self.ts = {g.M_CONSTANT: const_t,
                   g.M_RAMP: ramp_t}

        # Load the widgets into the stacked layout in order 
        self.s1.addWidget(QWidget())
        self.s1.addWidget(w_const)
        self.s1.addWidget(w_ramp)

        self.but_add_step = QPushButton(l.sp_add_btn[g.L])
        self.but_add_step.clicked.connect(self.add_step)

        v4.addLayout(horizontalize([step_name_lbl,self.step_name]))
        v4.addWidget(self.data_collect)
        v4.addWidget(QHLine())
        v4.addWidget(self.stirrer)
        v4.addWidget(self.vibrator)
        v4.addWidget(QHLine())
        v4.addLayout(horizontalize([step_type_lbl,self.step_type]))
        v4.addLayout(self.s1)
        v4.addWidget(self.but_add_step)

        
                          
                                
                                
        
        self.g1.setLayout(v4)           
        #policy = self.g1.sizePolicy()           # get existing size policy of g1
        #policy.setRetainSizeWhenHidden(True)    # modify policy so that g1 takes up space regardless of whether shown or hidden
        #self.g1.setSizePolicy(policy)           # set g1's size policy to the modified version.
        
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
        but_save_as = QPushButton('Save as')
        if self.path:
            but_save.clicked.connect(partial(self.start_save, 'save'))
            but_save_as.clicked.connect(partial(self.start_save, 'save-as'))
        else:
            but_save.clicked.connect(partial(self.start_save, 'save-as'))


        v5.addLayout(horizontalize([dt_lbl_0, self.dt, dt_lbl_1], True))
        v5.addLayout(horizontalize([current_range_lbl, self.current_range], True))
        g2.setLayout(v5)

        
        
        v2.addWidget(g2)
        v2.addStretch()
        v2.addWidget(self.hide_plot_lbls)

        h1.addLayout(v2)
        h1.addWidget(graph_area)

        
        v1top.addWidget(self.name)
        v1top.addLayout(h1)
        v1bot.addWidget(self.builder)
        
        if self.path:
            v1bot.addLayout(horizontalize([but_save, but_save_as]))
        else:
            v1bot.addWidget(but_save)
        wtop = QWidget()
        wbot = QWidget()
        wtop.setLayout(v1top)
        wbot.setLayout(v1bot)
        split1.addWidget(wtop)
        split1.addWidget(wbot)

        self.init_form_values()
        self.hide_new_step_pane()
        if self.path or self.data:
            self.set_values()
        self.update_buttons()
        self.set_header()

        if self.view_only:
            try:
                but_edit = QPushButton('Edit method')
                but_edit.clicked.connect(partial(parent.edit_config, path=self.path))
                but_refresh = QPushButton()
                but_refresh.setIcon(QIcon(g.ICON_REFRESH))
                but_refresh.setToolTip('Refresh')
                but_refresh.clicked.connect(self.set_values)
                if not view_only_edit:
                    but_edit.setEnabled(False)
                    but_refresh.setEnabled(False)
                v1 = QVBoxLayout()
                h1 = QHBoxLayout()
                v2 = QVBoxLayout()
                h2 = QHBoxLayout()

                h2.addWidget(but_edit)
                h2.addWidget(but_refresh)
                h2.addStretch()
                h2.addWidget(self.hide_plot_lbls)
                v2.addWidget(g2)
                v2.addWidget(self.profile_chart)
                v2.addLayout(h2)
                h1.addLayout(v2)
                h1.addWidget(self.graph)
                v1.addWidget(self.name)
                v1.addLayout(h1)

                self.name.setEnabled(False)
                self.dt.setEnabled(False)

                w = QWidget()
                w.setLayout(v1)
                self.setCentralWidget(w)
            except Exception as e:
                print(e)
        else:
        
            self.setCentralWidget(split1)

    def init_form_values(self):
        # Modify title and button text
        self.g1.setTitle(l.sp_add_step[g.L])
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
        if self.path:
            data = get_data_from_file(self.path)
        elif self.data:
            data = self.data
        self.name.setText(data[g.M_NAME])
        self.dt.setValue(data[g.M_DT])
        self.steps = data[g.M_STEPS]
        self.refresh_list()
        self.set_header()
        
        
    def set_form_values_for_editing(self, step):
        self.init_form_values()                     # initialize all form values
        
        # Modify title and button text
        self.g1.setTitle(l.sp_edit_step[g.L])
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
        t_tot = step[g.M_T]
        self.ts[this_type].setValue(t_tot)

        if this_type == g.M_CONSTANT:
            self.const_v.setValue(step[g.M_CONST_V])

        elif this_type == g.M_RAMP:
            self.ramp_v_start.setValue(step[g.M_RAMP_V1])
            self.ramp_v_end.setValue(step[g.M_RAMP_V2])
        
    def refresh_list(self):
        """ Clears the sweep list and rebuilds it"""
        try:
            self.erase_list_visualization()
            self.build_new_list()
            self.refresh_graph()
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
            step_type = step[g.M_TYPE]
            w_name = QLabel(step[g.M_STEP_NAME])
            
            
            w_volt = QLabel()
            if step_type == g.M_CONSTANT:
                w_volt = QLabel('const: '+str(step[g.M_CONST_V])+'V')
            elif step_type == g.M_RAMP:
                w_volt.setText('ramp: '+str(step[g.M_RAMP_V1])+'V'+' --> '+str(step[g.M_RAMP_V2])+'V')
            

            w_t = QLabel(str(step[g.M_T])+'s')

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
        if self.editing or self.view_only:                          # If there is an edit in process or if we are on a view-only window, 
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
        self.set_form_values_for_editing(step)
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
            step_type = g.M_TYPES[self.step_type.currentIndex()]
            
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
            if step_type == g.M_CONSTANT:                                                                                          #
                data_specific = {                                                                                                   #
                    g.M_CONST_V: self.const_v.value()                                                                              #                                                                                 #
                    }                                                                                                               #
                                                                                                                                    #
            elif step_type == g.M_RAMP:                                                                                            #
                data_specific = {                                                                                                   #
                    g.M_RAMP_V1: self.ramp_v_start.value(),                                                                        #
                    g.M_RAMP_V2: self.ramp_v_end.value()                                                                           #
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
            print(self.steps)
        

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
        if self.ts[step_type].value() == 0:                                   # make sure there is a duration
            show_alert(self, 'Error!', 'Please set a duration longer than 0 for this step')
            return False
    
        if step_type == g.M_RAMP:
            v1 = self.ramp_v_start.value()
            v2 = self.ramp_v_end.value()
            if v1 == v2:
                show_alert(self, 'Error!', 'The endpoints of this ramp have the same value, if this is what you want, please consider a constant volutage. Otherwise...typo?')
                return False
            
        return True

    def start_save(self, save_type):
        if self.validate_sweep_profile():
            if save_type == 'save-as':
                self.sp_save_as()
            else:
                self.sp_save()
    
    def sp_save_as(self):     
        # get the actual filename and path from user
        self.path = askSaveAsFileName(          # open a save file dialog which returns the file object
            filetypes=[(l.filetype_sp_lbl[g.L], g.SWEEP_PROFILE_FILE_TYPES)],
            defaultextension=g.SWEEP_PROFILE_EXT,
            confirmoverwrite=True,
            initialfile=guess_filename(self.name.text()))
        if not self.path or self.path == '':    # if the user didn't select a path
            return                              # don't try to save, just return
        self.sp_save()                          # save the file!

    def sp_save(self):
        data = {g.M_NAME: self.name.text(),
                g.M_DT: self.dt.value(),
                g.M_STEPS: self.steps}
        write_data_to_file(self.path, data)

    def validate_sweep_profile(self):
        # If you want to add validation to the overall sweep profile, do so here!
        #   Maybe to min and max dt?
        return True

    def refresh_graph(self):
        lbls = True
        if self.hide_plot_lbls.checkState() == Qt.CheckState.Checked:
            lbls = False
        self.graph.update_plot(self.steps, lbls)

    def set_header(self):
        if self.view_only:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_view[g.L]+self.name.text())   
        elif self.path:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_edit[g.L]+self.name.text())
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.c_edit_header_new[g.L]+self.name.text())
        
            
        
