"""
window_sample.py

This file defines a class WindowSample which creates a window object
that can be used to do a bunch of things. This is the main window that the
user will primarily use while operating the GUI.

The user can configure new runs, initiate runs, collect data, analyze data,
export data, view all past runs and analysis, and perhaps run calculations
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

#from wins.viewSample import WindowViewSample
from wins.sample import WindowSample
from wins.runConfig import WindowRunConfig

# import other necessary python tools
from os.path import join as joindir
from functools import partial
from tkinter.filedialog import askopenfilename as askOpenFileName

from PyQt6.QtTest import QTest
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTableWidget,
    QWidget,
    QLabel,
    QToolTip,
    QHeaderView,
    QCheckBox,
    QScrollArea,
    QGroupBox
    
)

# Define class for Home window
class WindowMain(QMainWindow):  

    def __init__(self, path, parent):
        super().__init__()
        
        self.path = path
        self.parent = parent
        self.data = {}
        self.w_view_sample = WindowSample(self.path, self, update_on_save=True, view_only=True)
        self.w_edit_sample = WindowSample(self.path, self, update_on_save=True, view_only=False)
        self.config_pane_displayed = False
        self.setObjectName('window-sample')
        self.selected = []                  # for storing which runs are selected
        self.prog_check_flag = False
        self.num_runs = 0

        #print(self.data)
            

        #####################
        #                   #
        #   menu bar        #
        #                   #
        #####################
        menu = self.menuBar()

        # add labels ("actions") for menu bar
        action_new_sample = QAction(l.new_sample[g.L], self)
        action_open_sample = QAction(l.open_sample[g.L], self)
        action_new_config = QAction(l.new_config[g.L], self)
        action_open_config = QAction(l.open_config[g.L], self)
        action_edit_config = QAction(l.edit_config[g.L], self)

        # connect menu bar labels with slots 
        action_new_sample.triggered.connect(parent.new_sample)                      # this first group of menu functions come from the home window (parent)
        action_open_sample.triggered.connect(parent.open_sample)
        action_new_config.triggered.connect(parent.new_config)
        action_open_config.triggered.connect(parent.open_config)
        action_edit_config.triggered.connect(parent.edit_config)

        # Add menu top labels then populate the menus with the above slotted labels
        file_menu = menu.addMenu(l.menu_sample[g.L])
        file_menu.addAction(action_new_sample)
        file_menu.addAction(action_open_sample)
        
        file_menu = menu.addMenu(l.menu_config[g.L])
        file_menu.addAction(action_new_config)
        file_menu.addAction(action_open_config)
        file_menu.addSeparator()
        file_menu.addAction(action_edit_config)

        file_menu = menu.addMenu(l.menu_run[g.L])


        #####################
        #                   #
        #   page layout     #
        #                   #
        #####################
        
        self.load_sample_info()                                                 # reads sample info into self.data
        self.set_sample_info()

        

        lay = QVBoxLayout()                             # this is the main vertical layout we'll add things to

        #
        #   Define the top row ("sample header")
        #
        
        
        but_view = QPushButton('Sample info')
        but_edit = QPushButton('Edit sample')
        but_config = QPushButton('NEW RUN')
        but_calc = QPushButton('Calculate')
        but_res_sample = QPushButton('Sample results')

        but_view.clicked.connect(self.view_sample_info)
        but_edit.clicked.connect(self.edit_sample)
        but_config.clicked.connect(self.config_run)
        
        v1 = QVLine()
        v2 = QVLine()
        v3 = QVLine()
        
        l_sample_header = QHBoxLayout()
        l_sample_header.addWidget(self.lbl_sample_name)
        l_sample_header.addWidget(but_view)
        l_sample_header.addWidget(but_edit)
        l_sample_header.addWidget(v1)
        l_sample_header.addStretch()
        l_sample_header.addWidget(v2)
        l_sample_header.addWidget(but_config)
        l_sample_header.addWidget(v3)
        l_sample_header.addWidget(but_calc)
        l_sample_header.addWidget(but_res_sample)

        w_sample_header = QWidget()                         # create a widget to hold the layout (which can be styled)
        w_sample_header.setLayout(l_sample_header)          # add the layout to the widget
        w_sample_header.setObjectName("sample-header")      # add a name to target with QSS

    
        #
        #   Define the second row ("run header")
        #
 
        l_run_header = QHBoxLayout()

        self.cb_all = QCheckBox()
        lbl_cb_all = QLabel("Select all")

        self.cb_all.stateChanged.connect(partial(self.select_all_toggle, self.cb_all))  # connect checkbox to select_all_toggle function
        lbl_cb_all.mouseReleaseEvent = self.select_all_lbl_clicked                      # when label is clicked, toggle checkbox

        but_view_config = QPushButton('Details')
        but_edit = QPushButton('Edit')
        but_del = QPushButton('Delete')
        but_export_raw = QPushButton('Export')
        but_view_plots = QPushButton('Graph')
        but_analyze = QPushButton('Analyze')
        but_view_results = QPushButton('Results')
        but_export_results = QPushButton('Export')

        but_view_config.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_edit.setObjectName(g.RUNS_BUT_ONE_NAME)
        but_del.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_export_raw.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_view_plots.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_analyze.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_view_results.setObjectName(g.RUNS_BUT_ANY_NAME)
        but_export_results.setObjectName(g.RUNS_BUT_ANY_NAME)

        l_run_header.addWidget(self.cb_all)
        l_run_header.addWidget(lbl_cb_all)

        l_run = QHBoxLayout()
        l_run.addWidget(but_view_config)
        l_run.addWidget(but_edit)
        l_run.addWidget(but_del)
        gb_run = QGroupBox("Run info")
        gb_run.setLayout(l_run)

        l_raw = QHBoxLayout()
        l_raw.addWidget(but_export_raw)
        l_raw.addWidget(but_view_plots)
        l_raw.addWidget(but_analyze)
        gb_raw = QGroupBox("Raw data")
        gb_raw.setLayout(l_raw)

        l_res = QHBoxLayout()
        l_res.addWidget(but_view_results)
        l_res.addWidget(but_export_results)
        gb_res = QGroupBox("Run results")
        gb_res.setLayout(l_res)
        
        l_run_header.addWidget(gb_run)
        l_run_header.addWidget(gb_raw)
        l_run_header.addWidget(gb_res)
        l_run_header.addStretch()

        self.w_run_header = QWidget()                    # create a widget to hold the layout (which can be styled)
        self.w_run_header.setLayout(l_run_header)        # add the layout to the widget
        self.w_run_header.setObjectName("run-header-row")# add a name to target with QSS


        # Grab the run history as a widget
        self.widgetize_run_history()
        
        # Add all of these three widgets to our vertical layout
        lay.addWidget(w_sample_header)
        lay.addWidget(self.w_run_header)
        lay.addWidget(self.w_run_history_area)

        # make sure all buttons are appropriately enabled/disabled to start
        self.update_button_states()

        # Display! 
        self.w = QWidget()
        self.w.setLayout(lay)
        self.setCentralWidget(self.w)
        
        

    def select_all_lbl_clicked(self, event):        # this exists so that the "select all" label can be clicked
        self.cb_all.toggle()                        #   as well as the checkbox itself

    def load_sample_info(self):                     # this grabs all data from file and lays it out on the window
                                                    # this can be called to update the window when the file has been updated
        if self.path:                                # if there is a path, read in the data
            self.data = get_data_from_file(self.path)

    def set_sample_info(self):      
        #self.w_view_sample = WindowSample(self.path, self, view_only=True)  # Update info in view sample pane (even if hidden)
        sample_name = self.data[g.S_NAME]                       
        self.setWindowTitle(sample_name)                        # Set the sample window title to the sample name
        try:
            self.lbl_sample_name.updateTitleLbl(sample_name)    # Set the Title label to the sample name...if this 
        except:                                                 #   throws and error, there is not yet a title label
            self.lbl_sample_name = TitleLbl(sample_name)        #   so create one! 



    def view_sample_info(self):
        self.w_view_sample.setTextFromFile()        # update content
        if self.w_view_sample.isHidden():           # if window is closed,
            self.w_view_sample.show()               # show it
        else:                                       # if it is showing,
            self.w_view_sample.activateWindow()     # bring it to front

    def edit_sample(self):
        self.w_edit_sample.setTextFromFile()        # update content
        if self.w_edit_sample.isHidden():           # if window is closed,
            self.w_edit_sample.show()               # show it
        else:                                       # if it is showing,
            self.w_edit_sample.activateWindow()     # bring it to front

    def update_displayed_info(self):
        self.load_sample_info()                                             # reload the sample info from file
        self.set_sample_info()                                          
        self.selected = []                                                  # re-init selected list b/c we have reloaded all runs and none 
                                                                            #   are selected to start.
        self.w_run_history_area.setParent(None)                             # remove run history pane from layout
        self.widgetize_run_history()                                        # get updated run history as a widget    
        self.centralWidget().layout().addWidget(self.w_run_history_area)    # add the updated run history back to layout

        print('here!')
        self.w_view_sample.setTextFromFile()                                # Update info in view-sample pane
        

    def config_run(self):
        try:
            self.w_run_config = WindowRunConfig(self, 'run-0')
            self.w_run_config.show()
        except Exception as e:
            print(e)
        

    def widgetize_run_history(self):
        demo = [{
            'name': 'run_1',
            'type':'blank',
            'sweep':'20s As ramp -1.7 to 0.4V',
            'timestamp': '2025-10-15 08:56pm',
            'comment':'Blank test run'},{
                'name':'run_2',
            'type':'sample',
            'sweep':'20s As ramp -1.7 to 0.4V w background',
            'timestamp': '2025-10-15 09:02pm',
            'comment':'No diultion'},{
                'name': 'run_3',
            'type':'sample',
            'sweep':'20s As ramp -1.7 to 0.4V w background',
            'timestamp': '2025-10-15 09:09pm',
            'comment':'No diultion'},{
                'name': 'run_6',
            'type':'sample',
            'sweep':'20s As ramp -1.7 to 0.4V w background',
            'timestamp': '2025-10-15 09:32pm',
            'comment':'No diultion'}]
        self.w_run_history_area = QScrollArea()
        self.w_run_history_area.resizeEvent = self.resize

        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)
        headers = ['Run began','Type', 'Sweep profile','Notes']
        w_heads = [0,0,0,0]
        for i, header in enumerate(headers):
            w_heads[i] = QLabel(header)
            w_heads[i].setObjectName('run-col-header')
            grid.addWidget(w_heads[i], 0, i+1)
            




        
        for i, run in enumerate(demo):
            w_cb = QCheckBox()
            w_cb.setObjectName(run['name'])         ##### <--- THIS IS WHERE THE RUN UID GETS STORED!!!
            w_cb.stateChanged.connect(partial(self.row_toggle,w_cb))
            w_type = QLabel(run['type'])
            w_sweep = QLabel(run['sweep'])
            w_comment = QLabel(run['comment'])
            w_time = QLabel(run['timestamp'])

            w_type.mouseReleaseEvent = partial(self.row_clicked, w_type)
            w_sweep.mouseReleaseEvent = partial(self.row_clicked, w_sweep)
            w_comment.mouseReleaseEvent = partial(self.row_clicked, w_comment)
            w_time.mouseReleaseEvent = partial(self.row_clicked, w_time)

            if (i%2 == 0):
                obj_name =g.RUNS_ODD_ROW_NAME
            else:
                obj_name =g.RUNS_EVEN_ROW_NAME

            w_type.setObjectName(obj_name)
            w_sweep.setObjectName(obj_name)
            w_comment.setObjectName(obj_name)
            w_time.setObjectName(obj_name)
            
            grid.addWidget(w_cb, i+1, 0)
            grid.addWidget(w_type, i+1, 2)
            grid.addWidget(w_sweep, i+1, 3)
            grid.addWidget(w_comment, i+1, 4)
            grid.addWidget(w_time, i+1, 1)

        self.num_runs = i+1
        grid.setColumnStretch(4,1)

        self.w_run_history_container = QWidget()
        self.w_run_history_container.setLayout(grid)
        self.w_run_history_container.setObjectName('runs-container')
        self.w_run_history_area.setWidget(self.w_run_history_container)
        

    def row_clicked(self, w, event):
        ws = self.get_row_ws(w)
        for w in ws:
            if isinstance(w, QCheckBox):
                w.toggle()
                break

    def select_all_toggle(self, w):
        if self.prog_check_flag:                        # if the select all checkbox has been modified programatically
            self.prog_check_flag = False                # reset the flag
            return                                      # and do nothing
        else:                                           # otherwise, it was a user click!
            state = w.checkState()
            state_to_set = Qt.CheckState.Unchecked      # figure out what to set all the run checkboxes to (checked or unchecked)
            if (state == Qt.CheckState.Checked):
                state_to_set = Qt.CheckState.Checked

            for w in self.w_run_history_container.children():       # loop thru all the widgets in the grid
                if isinstance(w, QCheckBox):            # for each checkbox
                    w.setCheckState(state_to_set)         # set the checkbox to the state determined above
                    
    def row_toggle(self, w, state):
        run_id = w.objectName()
        if (state == Qt.CheckState.Checked.value):              # if the checkbox is now checked
            if run_id not in self.selected:                     #  and if that row is not already listed as selected (altho this should be redundant)
                self.selected.append(run_id)                    #   add the current run uid to the list of selected runs     
                self.highlight_row(w)                           #   and highlight the row
                if (len(self.selected) == self.num_runs):       #   if this is the final row now selected (all rows are selected)
                    if (self.cb_all.checkState() == Qt.CheckState.Unchecked):
                        self.cb_all.toggle()
        elif run_id in self.selected:                               # if the the checkbox is now not checked and the row is currently listed as selected
            self.selected.remove(run_id)                            #  remove it from the selected list,
            self.unhighlight_row(w)                                 #  remove the highlighting,
            if (self.cb_all.checkState() == Qt.CheckState.Checked): # and if the 'select-all' box is checked
                self.prog_check_flag = True                         # set the flag that we modified a checkbox programatically
                self.cb_all.toggle()                                # and uncheck the "select all" checkbox
        self.update_button_states()

    def highlight_row(self, w):                                             # Highlights the row that contains the widget w        
        row = self.get_row_ws(w)                                            # find all widgets in row that contains w                                             
        for w in row:                                                       # loop through them
            if not isinstance(w, QCheckBox):                                # for all widgets that are not checkboxes
                w.setObjectName(w.objectName()+g.RUNS_ROW_SELECTED_SUFFIX)  #   update the widget name to indicate it sholud display as selected
        applyStyles()                                                       # when complete, update the styles across the app

    def unhighlight_row(self, w):                                                       # Unhighlights the row that contains the widget w 
        row = self.get_row_ws(w)                                                        # find all widgets in row that contains w 
        for w in row:                                                                   # loop through them
            if not isinstance(w, QCheckBox):                                            # for all widgets that are not checkboxes
                w.setObjectName(w.objectName().replace(g.RUNS_ROW_SELECTED_SUFFIX,''))  #   update the widget name to indicate it sholud no longer be highlighted
        applyStyles()                                                                   # when complete, update the styles across the app
 
    ###################### REDO THE GET ROW, HIGHLIGHT, AND SELECTION FUNCTIONS
        # USING THE GLOBAL FUNCTIONS AND THE FACT THAT WE CAN ADD A
        # ROW PROPERTY TO EACH WIDGET WHEN WE PLACE IT IN THE GRIDDDD
        ###################################################################################################################################################################################################
    def get_row_ws(self, widget_to_find):
        '''Takes in a widget that is on the table of runs
        loops through that table and returns a list of all
        widgets on the same row as the given widget, in order
        from left to right'''
        all_ws = self.w_run_history_container.children()    # grab all table widgets
        row_ws = []                             
        found_row = False
        for w in all_ws:    
            if isinstance(w, QCheckBox):        # if the widget is a checkbox, that means its the start of a new row
                if found_row:                   # if the previous row was the row we were seeking
                    break                       #   break! we did it! 
                row_ws = [w]                    # otherwise, begin storing the values in this array
            else:                               # if the the widget is NOT a checkbox, its an ordinary row element
                row_ws.append(w)                #  append it to the list

            if (w == widget_to_find):           # if the current widget is the widget we were seeking
                found_row = True

        return row_ws

    def update_button_states(self):
        rows = len(self.selected)
        enable_buts = []
        disable_buts = []
        if rows == 0:
            disable_buts = self.w_run_header.findChildren(QPushButton)
        elif rows == 1:
            enable_buts = self.w_run_header.findChildren(QPushButton)
        elif rows > 1:
            disable_buts = self.w_run_header.findChildren(QPushButton, g.RUNS_BUT_ONE_NAME)
            enable_buts = self.w_run_header.findChildren(QPushButton, g.RUNS_BUT_ANY_NAME)
            
        for but in disable_buts:
            but.setEnabled(False)
        for but in enable_buts:
            but.setEnabled(True)

    


    def resize(self, event):
        outer = self.w_run_history_area
        inner = self.w_run_history_container
        scroll_area_resized(outer, inner, event)


class TitleLbl(QLabel):
    def __init__(self, name):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(name)
                 
    def updateTitleLbl(self, new_name):
        self.setText(new_name)
