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
from wins.runView import WindowRunView

# import other necessary python tools
from os.path import join as joindir
from os.path import exists
from functools import partial
from tkinter.filedialog import askopenfilename as askOpenFileName
import csv


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
    QGroupBox,
    QApplication,
    QMenu
    
)

#######
#   FOR TESTING ONLY
import sys, os
#
###########

# Define class for Home window
class WindowMain(QMainWindow):  

    def __init__(self, path, parent):
        super().__init__()
        
        self.path = path
        self.parent = parent
        self.data = {}
        self.w_view_sample = WindowSample(self.path, self, update_on_save=True, view_only=True)
        self.w_edit_sample = WindowSample(self.path, self, update_on_save=True, view_only=False)
        self.w_run_config = WindowRunConfig(self)
        self.w_run = WindowRunView(self)
        self.ws_view_run_config = []
        self.config_pane_displayed = False
        self.setObjectName('window-sample')
        self.layout = {}                  # for storing an outline of runs and reps and which are selected
        self.select_all_prog_check_flag = False
        self.num_runs = 0
        self.children = [[self.w_view_sample, self.w_edit_sample, self.w_run_config, self.w_run], self.ws_view_run_config]

            

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



        #####################################
        #                                   #
        #   right-click ("context") menu    #
        #                                   #
        #####################################
        
        self.contextmenu_run = QMenu(self)      # Menu for when run is clicked
        self.contextmenu_rep = QMenu(self)      # Menu for when rep is clicked

        self.runAction_runAgain = self.contextmenu_run.addAction("Run from config")
        self.contextmenu_run.addSeparator()
        self.runAction_editNote = self.contextmenu_run.addAction("Edit run info [DOES NOTHING YET]")
        self.contextmenu_run.addSeparator()
        self.runAction_viewConfig = self.contextmenu_run.addAction("View config")
        self.runAction_viewData = self.contextmenu_run.addAction("Graph data from run(s) [DOES NOTHING YET]")
        self.runAction_exportData = self.contextmenu_run.addAction("Export CSV of run(s)")
        self.contextmenu_run.addSeparator()
        self.runAction_delete = self.contextmenu_run.addAction("Delete run(s) [DOES NOTHING YET]")

        self.repAction_editNote = self.contextmenu_rep.addAction("Edit replicate note [DOES NOTHING YET]")
        self.contextmenu_rep.addSeparator()
        self.repAction_viewData = self.contextmenu_rep.addAction("Graph replicate(s) data [DOES NOTHING YET]")
        self.repAction_exportData = self.contextmenu_rep.addAction("Export CSV of rep(s)")
        self.contextmenu_rep.addSeparator()
        self.repAction_delete = self.contextmenu_rep.addAction("Delete replicates(s) [DOES NOTHING YET]")

        self.runAction_runAgain.triggered.connect(self.config_run_with_uid)
        self.runAction_exportData.triggered.connect(self.export_runs_to_csv)
        self.runAction_viewConfig.triggered.connect(self.view_config)
        

        self.repAction_exportData.triggered.connect(self.export_reps_to_csv)

        

        self.runActions_oneOnly = [self.runAction_runAgain, self.runAction_editNote, self.runAction_viewConfig]
        self.repActions_oneOnly = [self.repAction_editNote]


        


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
        
        
        but_view = QPushButton('info')
        but_config = QPushButton('NEW RUN')
        but_calc = QPushButton('Calculate')
        but_res_sample = QPushButton('Sample results')

        but_view.clicked.connect(self.view_sample_info)
        but_config.clicked.connect(self.config_run)
        
        v1 = QVLine()
        v2 = QVLine()
        v3 = QVLine()
        
        l_sample_header = QHBoxLayout()
        l_sample_header.addWidget(self.lbl_sample_name)
        l_sample_header.addWidget(but_view)
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


        ###########################################################################################################################
        #
        #   Define the second row ("run header")
        #   (For now, just the "select all" checkbox, might move this later (holdover from when this was a row of buttons...
        #
 
        l_run_header = QHBoxLayout()

        self.cb_all = QCheckBox()
        lbl_cb_all = QLabel("Select all")

        self.cb_all.stateChanged.connect(partial(self.select_all_toggle, self.cb_all))  # connect checkbox to select_all_toggle function
        lbl_cb_all.mouseReleaseEvent = self.select_all_lbl_clicked                      # when label is clicked, toggle checkbox

        l_run_header.addWidget(self.cb_all)
        l_run_header.addWidget(lbl_cb_all)

        l_run_header.addStretch()

        self.w_run_header = QWidget()                    # create a widget to hold the layout (which can be styled)
        self.w_run_header.setLayout(l_run_header)        # add the layout to the widget
        self.w_run_header.setObjectName("run-header-row")# add a name to target with QSS

        #
        #
        ############################################################################################################################


        # Grab the run history as a widget
        try:
            self.widgetize_run_history()
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
        # Add all of these three widgets to our vertical layout
        lay.addWidget(w_sample_header)
        lay.addWidget(self.w_run_header)
        lay.addWidget(self.w_run_history_area)

        # Display! 
        self.w = QWidget()
        self.w.setLayout(lay)
        self.setCentralWidget(self.w)
        
        

    def select_all_lbl_clicked(self, event):        # this exists so that the "select all" label can be clicked
        self.cb_all.toggle()                        #   as well as the checkbox itself

    def load_sample_info(self):                     # this grabs all data from file and lays it out on the window
                                                    # this can be called to update the window when the file has been updated
        if self.path:                               # if there is a path, read in the data
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
        try:
            self.w_edit_sample.setTextFromFile()        # update content
            if self.w_edit_sample.isHidden():           # if window is closed,
                self.w_edit_sample.show()               # show it
            else:                                       # if it is showing,
                self.w_edit_sample.activateWindow()     # bring it to front
        except Exception as e:
            print(e)

    def update_displayed_info(self):
        self.load_sample_info()                                             # reload the sample info from file
        self.set_sample_info()                                          
                                                                            #   are selected to start.
        self.w_run_history_area.setParent(None)                             # remove run history pane from layout
        self.widgetize_run_history()                                        # get updated run history as a widget    
        self.centralWidget().layout().addWidget(self.w_run_history_area)    # add the updated run history back to layout

        print('here!')
        self.w_view_sample.setTextFromFile()                                # Update info in view-sample pane
        

    def config_run(self):
        self.w_run_config.set_form()
        self.w_run_config.show()
            
    def config_run_with_uid(self):
        """Finds the first selected run (assumes there is only one run selected!)
        and opens up a new run configuration window with all of the parameters
        preset to match the currently selected run"""
        for run in self.layout:                         # Loop thru layout
            if self.all_reps_of_run_are_selected(run):  # if this run is selected
                break                                   # break so that run=unique ID of run of interest

        self.w_run_config.set_form(run)                 # set the run config window to match config from run
        self.w_run_config.show()                        # show the run config window

    def view_config(self):
        #########################################
        #
        #
        #       HERE
        #   1. Append new window to self.ws_view_run_config
        #       ^-- figure out how to manage references to windows
        #       a. when window is closed, make sure to delete reference
        #   2. Launch new window!
        #   3. Modify runConfig.py for view-only! 
        
        return
        

    def do_nothing_with_widget(self, w):
        """This is necessary so that each widget has a callback function if clicked.
        Pls don't delete even tho is looks oh so deleteable!"""
        return

    def add_row_to_main(self, ws, row, h_offset=0, v_merge=1, h_merge=1):
        """
        Adds a new row of QWidgets to the self.grid object. Requires there being one self.grid object.
        Arguments:
            ws             List: of widgets to add to row
            row            Int: index of the row to add to the grid
            h_offset=0     Int: column offset of first widget (eg. if h_offset==2, this leaves first 2 cols
                           blank and ws[0] is placed in 2nd column)
            v_merge=1      Int: # of rows to merge together vertically
            h_merge=1      Int: # of columns to merge together horizontally
        Returns:
            The incremented row index
        """
        for i, w in enumerate(ws):
            self.grid.addWidget(w, row, i+h_offset, v_merge, h_merge)
        return row+1
    
    def create_w(self, s, qss_name, onclick_fn=do_nothing_with_widget, run_id=False, rep_id=False, word_wrap=True):
        """
        Returns a QLabel widget according the following arguments:
            s:          String: contains the text of the label
            qss_name    String: will be accessed by Qt Style Sheet for styling
            onclick_fn  Function handle: that runs when widget is clicked (default: do nothing)
            run_id      String: The UID of the related run (default False for cases where widget is not connected to specific run)
            rep_id      String: The UID of the related replicate (default False for cases where widget is not connected to specific replicate)
            word_wrap   Boolean: True to enable word wrapping, False to disable
        Sets the QLabel's current object name to qss_name (this can be modified elsewhere to adjust styling)
        Also creates properties within the QLabel (see documentation for QObject) for:
            ov-run (contains run=id)
            ov-rep (contains rep-id)
            ov-qss-name (contains qss_name for resetting styles)
        """
        
        w = QLabel(s)
        w.setWordWrap(word_wrap)
        w.setObjectName(qss_name)
        w.mouseReleaseEvent = partial(onclick_fn, w)
        w.setProperty('ov-run', run_id)
        w.setProperty('ov-rep', rep_id)     
        w.setProperty('ov-qss-name', qss_name)          # store qss name for easy access later (to reset styles)
        w.setProperty('ov-selected-qss-name', 'selected-'+qss_name)
        return w

    def widgetize_run_history(self):
        
        self.w_run_history_area = QScrollArea()             # init the scroll area
        self.w_run_history_area.resizeEvent = self.resize

        self.grid = QGridLayout()                           # init grid layout (that is inside scroll area)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(0)

        # create column headers and add them to the grid layout
        headers = ['RUN INFO','REPLICATE', 'STATUS', 'COMPLETED', 'NOTES', 'PROCESSING']
        w_heads = []
        for header in headers:
            w = self.create_w(header, qss_name='run-col-header')
            w_heads.append(w)

        row = 0
        row = self.add_row_to_main(w_heads, row)

        # Loop through all runs in sample's dataset
        for i, run in enumerate(self.data[g.S_RUNS]):

            # For each run, create a row for each replicate and add it to the grid, leaving the first cell of each row blank
            start_row = row
            run_id = run[g.R_UID_SELF]
            self.layout[run_id] = {'selected':[],'reps':[]}                     # initialize holing spot for run data 
            for j, rep in enumerate(run[g.R_REPLICATES]):
                rep_name = l.r_rep_abbrev[g.L] + ' '+str(j)
                rep_status = rep[g.R_STATUS]
                rep_time = 'TIMESTAMP WHEN RUN COMPLETED'
                rep_notes = rep[g.R_NOTES]
                rep_proc = 'PROCESSING ICONS HERE'
                rep_strs = [rep_name,rep_status,rep_time,rep_notes,rep_proc]

                is_last = False
                if j == len(run[g.R_REPLICATES])-1: is_last=True                # figure out if current rep is last of run

                if (i+j)%2 == 0 and is_last: qss_name = 'run-rep-even-last'     # even rows that are last rep of run
                elif (i+j)%2 != 0 and is_last: qss_name = 'run-rep-odd-last'    # odd rows that are last rep of run
                elif (i+j)%2 == 0: qss_name = 'run-rep-even'                    # regular even rows
                else: qss_name = 'run-rep-odd'                                  # regular odd rows
                
                rep_id = rep[g.R_UID_SELF]
                ws_rep = []
                for s in rep_strs:
                    w = self.create_w(s, qss_name, self.rep_clicked, run_id, rep_id)
                    ws_rep.append(w)

                    
                row = self.add_row_to_main(ws_rep, row, h_offset=1)
                self.layout[run_id]['reps'].append(rep_id)

            
            # Vertically merge all the first cells for this run's replicates and add run information
            run_name = 'Run '+str(i)
            run_type = l.rc_types[run[g.R_TYPE]][g.L]
            method_name = get_method_from_file_data(self.data, run[g.R_UID_METHOD])[g.M_NAME]
            run_notes = run[g.R_NOTES]
            run_str = '<u>'+run_name+'</u><br>'
            run_str = run_str + '<b>'+'Type'+'</b>: '+run_type+'<br>'
            run_str = run_str + '<b>'+'Method'+'</b>: '+method_name+'<br>'
            run_str = run_str + '<b>'+'Notes'+'</b>: '+run_notes

            if i%2 == 0: qss_name = 'run-even'
            else: qss_name = 'run-odd'

            w = self.create_w(run_str, qss_name, self.run_clicked, run_id)
            
            self.add_row_to_main([w], start_row, v_merge=row-start_row)

        #self.num_runs = row+1
        self.grid.setColumnStretch(len(headers)-1,1)                    # Set column stretch on last col so grid fills whole window

        self.w_run_history_container = QWidget()
        self.w_run_history_container.setLayout(self.grid)
        self.w_run_history_container.setObjectName('runs-container')
        self.w_run_history_area.setWidget(self.w_run_history_container)
        

    def rep_clicked(self, w, event):
        keys = QApplication.keyboardModifiers()
        btn = event.button()
        run = w.property('ov-run')
        rep = w.property('ov-rep')

        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:        # regular right click
            if not self.rep_is_selected(run, rep):                                              # If the clicked rep is not selected
                self.clear_selected()                                                           # Make it the only one selected
                self.add_rep_to_selected(run, rep)
                self.update_highlights()
            self.open_rightclick_menu_rep(event)                                                # Open right-click context menu

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.NoModifier:       # regular left click                                                            
            N = self.N_reps_selected()                                                          # Get # of reps selected
            rep_is_selected = self.rep_is_selected(run, rep)
            self.clear_selected()                                                               # Clear all selections
            if N > 1:                                                                           # If there were multiple selected, 
                self.add_rep_to_selected(run, rep)                                              # select the clicked rep (regardless of status)
            elif not rep_is_selected:                                                           # if 1 or 0 selected, not including clicked one
                self.add_rep_to_selected(run, rep)                                              # select clicked rep (if clicked rep is already only selection, this deselects it)

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ControlModifier:  # ctrl+left click
            if not self.rep_is_selected(run, rep):                                              # if clicked row not selected
                self.add_rep_to_selected(run, rep)                                              # add it to selection
            else:                                                                               # otherwise,
                self.remove_rep_from_selected(run, rep)                                         # remove it from selection

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ShiftModifier:    # shift+left click
            print('shift+click --- TODO: Add shift+click implemntation!!!')
            ###################3
            #
            #   ADD SHIFT+CLICK IMPLEMENTATION HERE...
            #
            ##################
        self.update_select_all_checkbox()
        self.update_highlights()                                                            # update styles to apply hightlighting
        


    def run_clicked(self, w, event):
        keys = QApplication.keyboardModifiers()
        btn = event.button()
        run = w.property('ov-run')

        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:    # regular right click
            print('regular right click')
            if not self.all_reps_of_run_are_selected(run):
                self.clear_selected()
                self.add_run_to_selected(run)
                self.update_highlights()
            self.open_rightclick_menu_run(event)

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.NoModifier:   # regular left click
            this_entire_run_is_only_selection = self.this_entire_run_and_nothing_else_is_selected(run)
            self.clear_selected()
            if not this_entire_run_is_only_selection:
                self.add_run_to_selected(run)
                
        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ControlModifier:  # ctrl+left click
            if self.all_reps_of_run_are_selected(run):                                            # if all reps of run are already selected
                self.remove_run_from_selected(run)                                              # deselect them all! 
            else:                                                                               # if they are not ALL selected (some or none are)
                self.add_run_to_selected(run)                                                   # Select them all! 

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ShiftModifier:   # shift+left click
            print('shift+click --- TODO: Add shift+click implemntation!!!')
            ###################3
            #
            #   ADD SHIFT+CLICK IMPLEMENTATION HERE...
            #
            ##################

        self.update_select_all_checkbox()
        self.update_highlights() 

    def rep_is_selected(self, run, rep):
        """Takes in a widget and returns True if that widget is part of a selected row.
        Otherwise, returns False"""
        if rep in self.layout[run]['selected']:
            return True
        return False
        
    def all_reps_of_run_are_selected(self, run):
        """Takes in a run id and returns True if all reps from that run are selected.
        Otherwise, returns False"""
        if len(self.layout[run]['selected']) == len(self.layout[run]['reps']):
            return True
        return False

    def this_entire_run_and_nothing_else_is_selected(self, run_id):
        """ Takes in a run ID and returns True if this entire run is selected
        and nothing else is selected (this-and-only-this). Otherwise, returns False,"""
        for run in self.layout:
            if run == run_id:
                if not self.all_reps_of_run_are_selected(run):
                    return False
            else:
                if len(self.layout[run]['selected']) != 0:
                    return False
        return True

    def all_reps_are_selected(self):
        """Returns True if all reps are selected.
        Otherwise, returns False"""
        for run in self.layout:
            if not self.all_reps_of_run_are_selected(run):
                return False
        return True

    def N_reps_selected(self):
        """ Returns Int, # of replicates currently selected"""
        N = 0
        for run in self.layout:
            N = N + len(self.layout[run]['selected'])
        return N

    def N_runs_selected(self):
        """ Returns Int, # of runs currently selected"""
        N = 0
        for run in self.layout:
            if self.all_reps_of_run_are_selected(run):
                N = N + 1
        return N

    def add_rep_to_selected(self, run, rep):
        """Adds a specific replicate of a specific run to the list of selected replicates. Takes:
                run    String. Unique ID of run in dataset
                rep    String. Unique ID of replicate of run to add
        Before pushing the (run,rep) tuple, checks if it is already selected. If so, does not
            add it to the selected list again. """
        if not rep in self.layout[run]['selected']: # Only add if this rep of this run is not already selected 
            self.layout[run]['selected'].append(rep)
    
    def remove_rep_from_selected(self, run, rep):
        """Removes a specific replicate of a specific run from the list of selected replicates. Takes:
                run    String. Unique ID of run in dataset
                rep    String. Unique ID of replicate of run to remove"""
        try:
            self.layout[run]['selected'].remove(rep)
        except Exception:
            pass            # if rep is not selected, ignore
        
    def add_run_to_selected(self, run_id):
        """Adds all replicates of a specific run to the list of selected replicates. Takes:
                run    String. Unique ID of run in dataset"""

        self.layout[run_id]['selected'] = self.layout[run_id]['reps'].copy()

    def remove_run_from_selected(self, run_id):
        """Removes all replicates of a specific run from the list of selected replicates. Takes:
            run    String. Unique ID of run in dataset"""

        self.layout[run_id]['selected'] = []

    def add_all_to_selected(self):
        """Adds all replicates in dataset to the list of selected replicates."""
        for run in self.layout:
            self.add_run_to_selected(run)

    def clear_selected(self):
        for run in self.layout:
            self.layout[run]['selected'] = []
    
    def update_highlights(self):
        """Using the current state of the self.layout list, modifies the objectName
        of relevant widgets to either remove selected status (if not on the list) or
        add selected status (if on the list). It assumes that each widget within the
        Run History Container (the QScrollArea that holds the run information) contains
        the following properties:
            ov-run               String. Unique ID of run in dataset
            ov-rep               String. Unique ID of replicate in dataset
            ov-selected-qss-name String. Set objectName to this for QSS stylings if selected
            ov-qss-name          String. Set objectName to this for QSS stylings if NOT selected
        This function loops through all widgets and if the widgets run and rep ids are listed
        on the selected list, it sets their objectName to their selected name. If they're not
        on the selected list, it sets their objectName to ther NOT selected name.
        """
        ws = self.w_run_history_container.children()            # grab all table widgets
        for w in ws:
            run = w.property('ov-run')
            rep = w.property('ov-rep')
            select = False
            if run:                                             # excludes any non-run or rep widgets (eg. headers)
                if rep:                                         # For all widgets that are part of a replicate row
                    if rep in self.layout[run]['selected']:     # set name for selected reps
                        select = True
                else:                                           # For all widgets that are part of a run (but not a rep!)
                    if self.all_reps_of_run_are_selected(run):  # set name for all runs that have all reps selected
                        select = True
                if select:
                    w.setObjectName(w.property('ov-selected-qss-name'))
                else:
                    w.setObjectName(w.property('ov-qss-name'))
        applyStyles()                                           #Grab QSS Stylesheet and apply it, now that names have been changed
      
    def select_all_toggle(self, w):
        """Click handler for select-all checkbox. This runs when select-all checkbox is checked
        programatically or by the user. The first step is to filter out programatic changes.
        Then, if box is check, all replicates are selected. If unchecked, nothing is selected."""
        if self.select_all_prog_check_flag:         # 1. If this function was triggered programatically
            self.select_all_prog_check_flag = False # Reset flag and ignore (return)
            return
        if w.checkState() == Qt.CheckState.Checked: # 2. if this function was triggered by a user click and the box is now checked
            self.add_all_to_selected()              # Add all reps to selected
        else:                                       # If triggered by a user click and box is now unchecked
            self.clear_selected()                      # Remove all selected
        self.update_highlights()

    def update_select_all_checkbox(self):
        """This function adjusts the state of the select-all checkbox programatically. To indicate that
        the change was programatic, before making a changes, the self.select_all_prog_check_flag is
        set. The two conditions that cause action are:
            1. If all reps are selected but select-all checkobx is not checked, check it!
            2. If NOT all reps are selected but select-all checkobx is checked, uncheck it!"""
        if self.all_reps_are_selected() and self.cb_all.checkState() != Qt.CheckState.Checked:
            self.select_all_prog_check_flag = True
            self.cb_all.setChecked(True)
        elif not self.all_reps_are_selected() and self.cb_all.checkState() != Qt.CheckState.Unchecked:
            self.select_all_prog_check_flag = True
            self.cb_all.setChecked(False)

    def open_rightclick_menu_run(self, event):
        """Opens the right-click context menu for runs. Takes in a mouseclick QEvent object
        that contains the location of the click. Menu is displayed at that location"""
        runs_selected = self.N_runs_selected()      # Get count of selected runs
        is_enabled = False
        if runs_selected == 1:                      # If just 1 run selected
            is_enabled = True                       # Enable all menu actions
        if runs_selected > 0:                       # If any # of runs selected at all
            for action in self.runActions_oneOnly:  # Setup which actions are enabled
                action.setEnabled(is_enabled)
            self.contextmenu_run.exec(event.globalPosition().toPoint())     # And show the menu!

    def open_rightclick_menu_rep(self, event):
        """Opens the right-click context menu for reps. Takes in a mouseclick QEvent object
        that contains the location of the click. Menu is displayed at that location"""
        reps_selected = self.N_reps_selected()      # Get count of selected replicates
        is_enabled = False
        if reps_selected == 1:                      # If just 1 rep selected
            is_enabled = True                       # Enable all menu actions
        if reps_selected > 0:                       # If any reps at all are selected
            for action in self.repActions_oneOnly:  # Setup which actions are enabled
                action.setEnabled(is_enabled)
            self.contextmenu_rep.exec(event.globalPosition().toPoint())     # And show the menu! 

    
    def get_run_data(self, run):
        """Takes in:
            run    String. Unique ID of run in dataset
        Returns:
            The dictionary from the Runs list in the dataset whose unique ID matches run_id"""
        return next(filter(lambda x: x[g.R_UID_SELF] == run, self.data[g.S_RUNS]), None)

    def get_rep_data(self, run, rep):
        """Takes in:
            run    String. Unique ID of run in dataset
            rep    String. Unique ID of replicate in dataset
        Returns:
            The dictionary of raw data that corresponds to rep of run."""
        run_data = self.get_run_data(run)
        rep_data = next(filter(lambda x: x[g.R_UID_SELF] == rep, run_data[g.R_REPLICATES]), None)
        return rep_data[g.R_DATA]

    def export_to_csv_message(self, yes, no):
        try:
            title = "Export complete."
            msg = "Export complete.\n"
            if no:
                msg = msg+"\nERROR: Failed to export:\n"
                for rep in no:
                    msg = msg+rep[0]+': '+rep[1]+'\n'
                title = "Warning: some replicates failed to export"
            if yes:
                msg = msg + "\nSuccessully exported:\n"
                for rep in yes:
                    msg = msg+rep[0]+': '+rep[1]+'\n'  
            show_alert(self, title, msg)
        except Exception as e:
            print(e)
                

    def export_runs_to_csv(self):
        path = get_path_from_user('folder')
        saved = []
        errored = []
        if path:
            for run in self.layout:
                if self.all_reps_of_run_are_selected(run):
                    for rep in self.layout[run]['selected']:
                        success = self.export_rep_to_csv(path, run, rep)
                        if success:
                            saved.append((run, rep))
                        else:
                            errored.append((run, rep))
            self.export_to_csv_message(saved, errored)
            

    def export_reps_to_csv(self):
        path = get_path_from_user('folder')
        saved = []
        errored = []
        if path:
            for run in self.layout:
                for rep in self.layout[run]['selected']:
                    success = self.export_rep_to_csv(path, run, rep)
                    if success:
                        saved.append((run, rep))
                    else:
                        errored.append((run, rep))
            self.export_to_csv_message(saved, errored)
                    
    def export_rep_to_csv(self, loc, run, rep):
        try:
            keys = []
            data = self.get_rep_data(run, rep)
            '''if not data:
                show_alert(self, "Heads up!", "No data available to export from "+run+", "+rep+".")
                return'''
                
            for key in data[0]:
                keys.append(key)

            samplename=self.path.split('/')[-1]             # get filename from path 
            groups = samplename.split('.')                  # begin removing the extension (split at all periods)
            samplename = '.'.join(groups[:len(groups)-1])   #   finish removing the extension (rejoin all with periods except for last)
            filename = samplename+'_'+run+'_'+rep           # add on the run and rep IDs
            path = loc+'/'+filename                         # append filename to path
            suffix = ''
            i = 1
            while exists(path+suffix+'.csv'):               # while the file already exists
                suffix = '_COPY'+str(i)                     # tack on a suffix
                i = i+1                                     # and increment the counter until we find a filename that is not taken!
            path = path+suffix+'.csv'                       # generate that novel filename
                
     
            with open(path, 'w', encoding='UTF8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys) # Tell the writer we are writing from a dictionary with 'keys' as headers
                writer.writeheader()                        # Write the header row
                writer.writerows(data)                      # Write the data
            return True
                
                
        except Exception as e:
            return False
        
        
        #for 
        print('---')
        print(run)
        print(rep)
        return




            

    


    def resize(self, event):
        outer = self.w_run_history_area
        inner = self.w_run_history_container
        scroll_area_resized(outer, inner, event)

    def setEnabledChildren(self, enable):
        """Takes in a boolean, "enable" and sets all child window's enabled status
        to that boolean, either enabling or disabling all"""
        for l in self.children:
            for win in l:
                win.setEnabled(enable)

    def start_run(self, uid):
        self.w_run.set_run_uid(uid)
        self.w_run.show()

    def closeEvent(self, event):
        for l in self.children:
            for win in l:
                win.close()
        event.accept()


class TitleLbl(QLabel):
    def __init__(self, name):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(name)
                 
    def updateTitleLbl(self, new_name):
        self.setText(new_name)
