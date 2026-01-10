"""
window_sample.py

This file defines a class WindowSample which creates a window object
that can be used to do a bunch of things. This is the main window that the
user will primarily use while operating the GUI.

The user can configure new runs, initiate runs, collect data, analyze data,
export data, view all past runs and analysis, and perhaps run calculations
"""
# import global vars, language pack, and functions
import ov_globals as g
import ov_lang as l
from ov_functions import *

# import necessary windows
from wins.sample import WindowSample
from wins.method import WindowMethod
from wins.runConfig import WindowRunConfig
from wins.runView import WindowRunView

# import other necessary python tools
from os.path import join as joindir
from os.path import exists
from functools import partial
from ast import literal_eval

# import PyQt6/PySide6 stuff
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import QDate, Qt, QProcess
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
    QMenu,
    QInputDialog,
    QProgressBar,
    QMessageBox
)

#######
#   FOR TESTING ONLY
import sys, os
#
###########

# Define class for Home window
class WindowMain(QMainWindow):  

    def __init__(self, parent, path):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.path = path
        self.parent = parent
        self.data = {}
        self.children = []
        self.setObjectName('window-sample')
        self.layout = {}                  # for storing an outline of runs and reps and which are selected
        self.select_all_prog_check_flag = False
        self.save_error_flag = False
        self.read_error_flag = False
        self.export_error_msg = ''
        self.status = self.statusBar()
        self.progress_bar = QProgressBar()
        self.process = None

        #####################
        #                   #
        #   status bar      #
        #                   #
        #####################
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMaximumWidth(g.SB_PROGRESS_BAR_WIDTH)  # Set a fixed width
        self.progress_bar.setVisible(False)     # Hide it initially
        self.status.addPermanentWidget(self.progress_bar)

        #####################
        #                   #
        #   begin data read #
        #                   #
        ##################### 
        self.start_async_read()

        #####################
        #                   #
        #   menu bar        #
        #                   #
        #####################
        menu = self.menuBar()

        # add labels ("actions") for menu bar
        action_sample_new = QAction(l.new_sample[g.L], self)
        action_sample_open = QAction(l.open_sample[g.L], self)
        action_sample_close = QAction('Close', self)
        
        action_method_new = QAction(l.new_config[g.L], self)
        action_method_open = QAction(l.open_config[g.L], self)
        action_method_run_view = QAction('View run method', self)
        action_method_run_edit = QAction('Change run method name', self)

        action_run_new = QAction('New run', self)
        action_run_new_from = QAction('New run from config', self)
        action_run_redo = QAction('Redo run', self)
        action_run_view = QAction('View info', self)
        action_run_edit = QAction('Edit info', self)
        action_run_export = QAction('Export as CSV', self)
        action_run_delete = QAction('Delete', self)

        action_rep_redo = QAction('Redo replicate', self)
        action_rep_edit = QAction('Edit note', self)
        action_rep_export = QAction('Export as CSV', self)
        action_rep_delete = QAction('Delete', self)

        action_analyze_start = QAction('Analyze', self)
        action_analyze_results = QAction('Results', self)
        
        
        # connect menu bar labels with slots 
        action_sample_new.triggered.connect(parent.new_sample)                      # this first group of menu functions come from the home window (parent)
        action_sample_open.triggered.connect(parent.open_sample)
        action_sample_close.triggered.connect(self.close)

        action_method_new.triggered.connect(parent.new_method)
        action_method_open.triggered.connect(parent.open_method)
        action_method_run_view.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_ONLY))
        action_method_run_edit.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_WITH_MINOR_EDITS))

        action_run_new.triggered.connect(partial(self.new_win_config_run, g.WIN_MODE_NEW))
        action_run_new_from.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_NEW))
        action_run_redo.triggered.connect(self.redo_run)
        action_run_view.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_VIEW_ONLY))
        action_run_edit.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_EDIT))
        action_run_export.triggered.connect(self.export_selected_reps_as_csv)
        action_run_delete.triggered.connect(self.delete_runs)

        action_rep_redo.triggered.connect(self.redo_run)
        action_rep_edit.triggered.connect(self.edit_rep_note)
        action_rep_export.triggered.connect(self.export_selected_reps_as_csv)
        action_rep_delete.triggered.connect(self.delete_reps)

        '''action_analyze_start.triggered.connect()
        action_analyze_results.triggered.connect()'''

        

        

        

        
        

        # Add menu top labels then populate the menus with the above slotted labels
        file_menu = menu.addMenu(l.menu_sample[g.L])
        file_menu.addAction(action_sample_new)
        file_menu.addAction(action_sample_open)
        file_menu.addSeparator()
        file_menu.addAction(action_sample_close)
        
        file_menu = menu.addMenu(l.menu_config[g.L])      
        file_menu.addAction(action_method_new)
        file_menu.addAction(action_method_open)
        file_menu.addSeparator()
        file_menu.addAction(action_method_run_view)
        file_menu.addAction(action_method_run_edit)

        file_menu = menu.addMenu(l.menu_run[g.L])
        file_menu.addAction(action_run_new)
        file_menu.addAction(action_run_new_from)
        file_menu.addSeparator()
        file_menu.addAction(action_run_redo)
        file_menu.addSeparator()
        file_menu.addAction(action_run_view)
        file_menu.addAction(action_run_edit)
        file_menu.addSeparator()
        file_menu.addAction(action_method_run_view)
        file_menu.addAction(action_method_run_edit)
        file_menu.addSeparator()
        file_menu.addAction(action_run_export)
        file_menu.addSeparator()
        file_menu.addAction(action_run_delete)

        file_menu = menu.addMenu('Replicate')
        file_menu.addAction(action_rep_redo)
        file_menu.addSeparator()
        file_menu.addAction(action_rep_edit)
        file_menu.addSeparator()
        file_menu.addAction(action_rep_export)
        file_menu.addSeparator()
        file_menu.addAction(action_rep_delete)

        file_menu = menu.addMenu('Analysis')
        file_menu.addAction(action_analyze_start)
        file_menu.addAction(action_analyze_results)

        self.actions_run_one_only = [action_run_new_from,
                                     action_run_redo,
                                     action_run_view,
                                     action_run_edit,
                                     action_method_run_view,
                                     action_method_run_edit]
        self.actions_run_one_plus = [action_run_export,
                                     action_run_delete]
        self.actions_rep_one_only = [action_rep_redo,
                                     action_rep_edit]
        self.actions_rep_one_plus = [action_rep_export,
                                     action_rep_delete]
        

        #####################################
        #                                   #
        #   right-click ("context") menu    #
        #                                   #
        #####################################
        
        self.contextmenu_run = QMenu(self)      # Menu for when run is clicked
        self.contextmenu_rep = QMenu(self)      # Menu for when rep is clicked

        self.runAction_runAgain = self.contextmenu_run.addAction("New run from config")
        self.runAction_redoRun = self.contextmenu_run.addAction("Redo this run")
        self.contextmenu_run.addSeparator()
        self.runAction_viewConfig = self.contextmenu_run.addAction("View run info")
        self.runAction_editConfig = self.contextmenu_run.addAction("Edit run info")
        self.contextmenu_run.addSeparator()
        self.runAction_viewMethod = self.contextmenu_run.addAction("View method")
        self.runAction_editMethod = self.contextmenu_run.addAction("Edit method name")
        self.contextmenu_run.addSeparator()
        self.runAction_viewData = self.contextmenu_run.addAction("Graph data from run(s) [DOES NOTHING YET]")
        self.runAction_exportData = self.contextmenu_run.addAction("Export CSV of run(s)")
        self.contextmenu_run.addSeparator()
        self.runAction_delete = self.contextmenu_run.addAction("Delete run(s)")

        self.runAction_redoRep = self.contextmenu_rep.addAction("Redo this rep")
        self.contextmenu_rep.addSeparator()
        self.repAction_editNote = self.contextmenu_rep.addAction("Edit replicate note")
        self.contextmenu_rep.addSeparator()
        self.repAction_viewData = self.contextmenu_rep.addAction("Graph replicate(s) data [DOES NOTHING YET]")
        self.repAction_exportData = self.contextmenu_rep.addAction("Export CSV of rep(s)")
        self.contextmenu_rep.addSeparator()
        self.repAction_delete = self.contextmenu_rep.addAction("Delete replicates(s)")

        self.runAction_runAgain.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_NEW))
        self.runAction_redoRun.triggered.connect(self.redo_run)
        self.runAction_viewConfig.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_VIEW_ONLY))
        self.runAction_editConfig.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_EDIT))
        self.runAction_viewMethod.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_ONLY))
        self.runAction_editMethod.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_WITH_MINOR_EDITS))
        self.runAction_exportData.triggered.connect(self.export_selected_reps_as_csv)
        self.runAction_delete.triggered.connect(self.delete_runs)
        
        self.runAction_redoRep.triggered.connect(self.redo_run)
        self.repAction_editNote.triggered.connect(self.edit_rep_note)
        self.repAction_exportData.triggered.connect(self.export_selected_reps_as_csv)
        self.repAction_delete.triggered.connect(self.delete_reps)

        self.runActions_oneOnly = [self.runAction_runAgain,
                                   self.runAction_redoRun,
                                   self.runAction_editConfig,
                                   self.runAction_viewConfig,
                                   self.runAction_viewMethod,
                                   self.runAction_editMethod]
        self.repActions_oneOnly = [self.repAction_editNote,
                                   self.runAction_redoRep]
        
        #####################
        #                   #
        #   page layout     #
        #                   #
        #####################

        lay = QVBoxLayout()
        
        but_view = QPushButton('info')
        but_config = QPushButton('NEW RUN')
        but_calc = QPushButton('Calculate')
        but_res_sample = QPushButton('Sample results')
        self.buts = [but_view, but_config, but_calc, but_res_sample]
        
        but_view.clicked.connect(self.new_win_sample)
        but_config.clicked.connect(partial(self.new_win_config_run, g.WIN_MODE_NEW))
            
        vl1 = QVLine()
        vl2 = QVLine()
        vl3 = QVLine()

        self.lbl_sample_name = TitleLbl("")
        
        l_sample_header = QHBoxLayout()
        l_sample_header.addWidget(self.lbl_sample_name)
        l_sample_header.addWidget(but_view)
        l_sample_header.addWidget(vl1)
        l_sample_header.addStretch()
        l_sample_header.addWidget(vl2)
        l_sample_header.addWidget(but_config)
        l_sample_header.addWidget(vl3)
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
        
        self.w_run_history_area = QScrollArea()
        
        # Add all of these three widgets to our vertical layout
        lay.addWidget(w_sample_header)
        lay.addWidget(self.w_run_header)
        lay.addWidget(self.w_run_history_area)

        setWsEnabled(self.buts, False)
        
        # Display! 
        self.w = QWidget()
        self.w.setLayout(lay)
        self.setCentralWidget(self.w)
        

    def update_win(self):
        try:
            sample_name = self.data[g.S_NAME]
            self.setWindowTitle(sample_name)                                    # Set the sample window title
            self.lbl_sample_name.updateTitleLbl(sample_name)                    # Set the sample name
            pos = self.w_run_history_area.verticalScrollBar().sliderPosition()  # Get scroll bar slider position
            self.w_run_history_area.setParent(None)                             # remove run history pane from layout
            self.widgetize_runs()                                               # get updated run history as a widget    
            self.centralWidget().layout().addWidget(self.w_run_history_area)    # add the updated run history back to layout
            self.update_highlights()
            self.update_menu()
            self.w_run_history_area.verticalScrollBar().setSliderPosition(pos)  # set scrollbar slider to previous position
            self.update_children()
        except Exception as e:
            print(e)
        
        
    #############################################
    #                                           #
    #   Functions for creating run layout       #
    #                                           #
    #   1. widgetize_runs                       #
    #   2. do_nothing                           #
    #   3. create_w                             #
    #   4. add_row_to_main                      #
    #                                           #
    #############################################

    def widgetize_runs(self):
        layout_old = self.layout.copy()                     # Store copy of old layout
        self.layout = {}                                    # Reinit self.layout to be refilled 
        
        self.grid = QGridLayout()                           # init grid layout (that is inside scroll area)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(0)
        
        # create column headers and add them to the grid layout
        headers = ['RUN INFO','REPLICATE', 'STATUS', 'LAST ATTEMPTED', 'NOTES', 'PROCESSING']
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
                rep_time = rep[g.R_TIMESTAMP_REP]
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
                    w = self.create_w(html_escape(s), qss_name, self.rep_clicked, run_id, rep_id)
                    ws_rep.append(w)   
                row = self.add_row_to_main(ws_rep, row, h_offset=1)
                self.layout[run_id]['reps'].append(rep_id)
            
            # Vertically merge all the first cells for this run's replicates and add run information
            run_name = 'Run '+str(i)
            run_type = l.rc_types[run[g.R_TYPE]][g.L]
            method_name = get_method_from_file_data(self.data, run[g.R_UID_METHOD])[g.M_NAME]
            run_notes = run[g.R_NOTES]
            run_str = '<u>'+html_escape(run_name)+'</u><br>'
            run_str = run_str + '<b>'+'Type'+'</b>: '+html_escape(run_type)+'<br>'
            run_str = run_str + '<b>'+'Method'+'</b>: '+html_escape(method_name)+'<br>'
            run_str = run_str + '<b>'+'Notes'+'</b>: '+html_escape(run_notes)

            if i%2 == 0: qss_name = 'run-even'
            else: qss_name = 'run-odd'

            w = self.create_w(run_str, qss_name, self.run_clicked, run_id)
            
            self.add_row_to_main([w], start_row, v_merge=row-start_row)

        self.grid.setColumnStretch(len(headers)-1,1)

        # update self.layout to ensure that highlights maintain over update
        for run in layout_old:
            if run in self.layout:
                for rep in layout_old[run]['selected']:
                    if rep in self.layout[run]['reps']:
                        self.layout[run]['selected'].append(rep)
        
        self.w_run_history_container = QWidget()
        self.w_run_history_container.setLayout(self.grid)
        self.w_run_history_container.setObjectName('runs-container')
        self.w_run_history_area.setWidget(self.w_run_history_container)

    def do_nothing(self, w):
        """This is necessary so that each widget has a callback function if clicked.
        Pls don't delete even tho is looks oh so deleteable!"""
        return

    def create_w(self, s, qss_name, onclick_fn=do_nothing, run_id=False, rep_id=False, word_wrap=True):
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
        w.setTextFormat(Qt.TextFormat.RichText)
        w.setWordWrap(word_wrap)
        w.setObjectName(qss_name)
        w.mouseReleaseEvent = partial(onclick_fn, w)
        w.setProperty('ov-run', run_id)
        w.setProperty('ov-rep', rep_id)     
        w.setProperty('ov-qss-name', qss_name)          # store qss name for easy access later (to reset styles)
        w.setProperty('ov-selected-qss-name', 'selected-'+qss_name)
        return w

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

    #############################################
    #                                           #
    #   Click handlers                          #
    #                                           #
    #   1. rep_clicked                          #
    #   2. run_clicked                          #
    #                                           #
    #############################################

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
        self.update_menu()
        self.update_select_all_checkbox()
        self.update_highlights()                                                            # update styles to apply hightlighting
        


    def run_clicked(self, w, event):
        keys = QApplication.keyboardModifiers()
        btn = event.button()
        run = w.property('ov-run')

        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:    # regular right click
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

        self.update_menu()
        self.update_select_all_checkbox()
        self.update_highlights()

    #####################################################
    #                                                   #
    #   Functions involved in selecting runs or reps    #
    #                                                   #
    #   1. rep_is_selected                              #
    #   2. all_reps_of_run_are_selected                 #
    #   3. this_entire_run_and_nothing_else_is_selected #
    #   4. all_reps_are_selected                        #
    #   5. N_reps_selected                              #
    #   6. N_runs_selected                              #
    #   7. add_rep_to_selected                          #
    #   8. remove_rep_from_selected                     #
    #   9. add_run_to_selected                          #
    #   10. remove_run_from_selected                    #
    #   11. add_all_to_selected                         #
    #   12. clear_selected                              #
    #   13. update_highlights                           #   
    #   14. select_all_lbl_clicked                      #   
    #   15. select_all_toggle                           #
    #   16. update_select_all_checkbox                  #
    #   17. update_menu                                 #
    #                                                   #
    #####################################################

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

    def select_all_lbl_clicked(self, event):        # this exists so that the "select all" label can be clicked
        self.cb_all.toggle()                        #   as well as the checkbox itself

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
        self.update_menu()

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

    def update_menu(self):
        runs = self.N_runs_selected()
        reps = self.N_reps_selected()
        yes = []
        no = []
        # For reps 
        if reps == 0:
            no = self.actions_rep_one_only + self.actions_rep_one_plus
        elif reps == 1:
            yes = self.actions_rep_one_only + self.actions_rep_one_plus
        else:
            yes = self.actions_rep_one_plus
            no = self.actions_rep_one_only

        # For runs
        if runs == 0:
            no = no + self.actions_run_one_only + self.actions_run_one_plus
        elif runs == 1:
            yes = yes + self.actions_run_one_only + self.actions_run_one_plus
        else:
            yes = yes + self.actions_run_one_plus
            no = no + self.actions_run_one_only

        for action in yes:
            action.setEnabled(True)
        for action in no:
            action.setEnabled(False)

    


    #############################################
    #                                           #
    # Handlers for right-click "context" menus  #
    #                                           #
    #   1. open_rightclick_menu_run             #
    #   2. open_rightclick_menu_rep             #
    #                                           #
    #############################################

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

    #############################################
    #                                           #
    # Menu functions and their friends          #
    #                                           #
    #   a. get_single_selected_run              #
    #   b. get_single_selected_rep              #
    #   c. get_all_selected_runs                #
    #   d. get_all_selected_reps                #
    #   e. get_all_reps_in_runs                 #
    #                                           #
    #   1. edit_rep_note                        #
    #   2. open_run_config_with_uid             #
    #   3. open_method_with_uid                 #
    #   4. export_selected_reps_as_csv          #
    #   5. redo_run                             #
    #   6. delete_runs                          #
    #   7. delete_reps                          #
    #   8. confirm_delete                       #
    #                                           #
    #############################################

    def get_single_selected_run(self):
        """Loops through layout, returns ID of first selected run.
        If no runs are selected, returns False."""
        for run in self.layout:                         # Loop thru layout
            if self.all_reps_of_run_are_selected(run):  # if this run is selected
                return(run)                             # return unique ID of this run
        return False

    def get_single_selected_rep(self):
        """Loops through layout, returns (runID, repID) for first selected rep.
        If no reps are selected, returns (False, False)."""
        for run in self.layout:
            if self.layout[run]['selected']:
                return (run, self.layout[run]['selected'][0])
        return (False, False)

    def get_all_selected_runs(self):
        runs = []
        for run in self.layout:
            if self.all_reps_of_run_are_selected(run):
                runs.append(run)
        return runs

    def get_all_selected_reps(self):
        reps = []
        for run in self.layout:
            for rep in self.layout[run]['selected']:
                reps.append((run,rep))
        return reps

    def get_all_reps_in_runs(self, runs):
        """ Takes in a list of run ids. Returns all reps that correpond to each
        of those runs in a list of tuples with format:
        [(runID_1), repID_1), (runID_2, repID_2), ... ,(runID_N, repID_N)]"""
        reps = []
        for run in self.layout:
            if run in runs:
                for rep in self.layout[run]['reps']:
                    reps.append((run, rep))
        return reps


    def edit_rep_note(self):
        """Opens a dialog """
        (run_id, rep_id) = self.get_single_selected_rep()
        rep = get_rep(self.data, (run_id, rep_id))
        note = rep[g.R_NOTES]

        #if note:
        title = "Replicate Note | "+run_id+': '+rep_id
        input_text, ok = QInputDialog.getText(self, title, "", text=note)

        if ok:
            if rep[g.R_NOTES] != input_text:
                rep[g.R_NOTES] = input_text
                print(rep)
                self.start_async_save(g.SAVE_TYPE_REP_MOD, [(run_id, rep_id), rep])

    def open_run_config_with_uid(self, mode):
        """Finds the first selected run (assumes there is only one run selected!)
        and opens up a new run configuration window with all of the parameters
        preset to match the currently selected run"""
        run_id = self.get_single_selected_run()
        if run_id:
            self.new_win_config_run(mode, run_id)

    def open_method_with_uid(self, mode):
        try:
            run_id = self.get_single_selected_run()
            if run_id:
                method_id = ''
                for run in self.data[g.S_RUNS]:
                    if run[g.R_UID_SELF] == run_id:
                        method_id = run[g.R_UID_METHOD]
                        break
                if method_id:   
                    self.new_win_method_by_id(mode, method_id)
        except Exception as e:
            print(e)

    def export_selected_reps_as_csv(self):
        reps = self.get_all_selected_reps()
        dest = get_path_from_user(self, 'folder')
        if dest:
            self.start_async_export(reps, dest)

    def redo_run(self):
        msg_box = QMessageBox()    
        msg_box.setWindowTitle("Just checking...") 
        msg_box.setText('This modifies a previous run.\nAll data and analysis for this run will be lost.\nAre you sure you want to rerun?\n\n(To create a *new run* with this run\'s configuration,  select "New run from config".)')
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

        # customize button language text for multi-language support
        but_save = msg_box.button(QMessageBox.StandardButton.Ok)
        but_save.setText('Rerun')
        but_canc = msg_box.button(QMessageBox.StandardButton.Cancel)
        but_canc.setText('Cancel')

        resp = msg_box.exec()
            
        if resp == QMessageBox.StandardButton.Ok:
            reps = self.get_all_selected_reps()
            self.new_win_view_run(reps)

    def delete_runs(self):
        if self.confirm_delete():
            runs = self.get_all_selected_runs()                     # Get selected runs (ignore selected reps that aren't part of selected runs)
            reps = self.get_all_reps_in_runs(runs)                  # Get all reps of selected runs
            self.start_async_save(g.SAVE_TYPE_REP_DELETE, [reps])

    def delete_reps(self):
        if self.confirm_delete():
            reps = self.get_all_selected_reps()                     # Get all selected reps
            self.start_async_save(g.SAVE_TYPE_REP_DELETE, [reps])

    def confirm_delete(self):
        title = 'Confirm delete'
        text = 'This will permanently delete all configurations and data associated with the selected runs or replicates.\n\nIf you are sure you want to delete, type DELETE below.'
        text, ok = QInputDialog.getText(self, title, text)

        if ok:
            if text == 'DELETE':
                return True
        return False
        
        

        
        
        
        
        

        
        



    #############################################
    #                                           #
    #   Functions for opening new windows       #
    #                                           #
    #   1. new_win_sample                       #
    #   2. new_win_config_run                   #
    #   3. new_win_view_run                     #
    #   4. new_win_method_by_id                 #
    #   5. X
    #   6.
    #
    #   9. new_win_one_of_type                  #
    #   10. new_win_one_with_value              #
    #   11. update_children                     #
    #                                           #
    #############################################

    def new_win_sample(self):
        self.new_win_one_of_type(WindowSample(self, g.WIN_MODE_VIEW_ONLY))

    def new_win_config_run(self, mode, run_id=False):
        self.new_win_one_of_type(WindowRunConfig(self, mode, run_id))

    def new_win_view_run(self, tasks):
        self.new_win_one_of_type(WindowRunView(self, tasks))

    def new_win_method_by_id(self, mode, m_id, changable=True):
        self.new_win_one_with_value(WindowMethod(self, mode, method_id=m_id, mode_changable=changable), 'method_id', m_id)

    def new_win_method_by_path(self, mode, path, changable=True):
        self.new_win_one_with_value(WindowMethod(self, mode, path=path, mode_changable=changable), 'path', path)

    def new_win_one_of_type(self, obj):
        """Takes in a new object to create as child window of self.
        Checks whether a window with matching type already exists.
        If it does, activates (bring-to-front) that window and returns it.
        If not, creates that window, show, it and returns it.
        Returns: window object."""
        for win in self.children:       
            if type(win) == type(obj):  # If there is already a child window with matching type
                win.activateWindow()    # activate it and return it
                return win
        
        self.children.append(obj)       # If there isn't already one, append the new window to the list of children
        self.children[-1].show()        # Show the window
        return self.children[-1]        # And return it

    def new_win_one_with_value(self, obj, key, value):
        for win in self.children:
            if type(win) == type(obj):
                if win.__dict__[key] == value:
                    win.activateWindow()
                    return win
        
        self.children.append(obj)
        self.children[-1].show()
        return self.children[-1]

    def update_children(self):
        for win in self.children:
            win.update_win()
        
        


            


















    #############################################
    #                                           #
    #   Functions for asynchronous export       #
    #                                           #
    #   1. start_async_export                   #
    #   2. handle_export_stdout                 #
    #   3. handle_export_stderr                 #
    #   4. handle_finished_export               #
    #                                           #
    #############################################

    def start_async_export(self, reps, destPath):
        if not self.process:
            self.export_success = []
            self.export_fail = []
            self.export_error_msg = ''
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_export_stdout)
            self.process.readyReadStandardError.connect(self.handle_export_stderr)
            self.process.finished.connect(self.handle_finished_export)
            self.status.showMessage("Exporting...")
            self.progress_bar.setVisible(True)
            self.process.start("python", ['processes/export.py', self.path, destPath, str(reps)])

    def handle_export_stdout(self):
        print('normal msg!')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        outs = stdout.split('\r\n')
        for out in outs:
            if out:
                self.export_success.append(out)

    def handle_export_stderr(self):
        print('error msg:')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        #print(stderr)
        errs = stderr.split('\r\n')                 # If multiple errors come in at once, split them up              
        for err in errs:                            # Loop thru them all
            if err:                             
                try:
                    literal_eval(err)               # Check if is anything other than string
                    self.export_fail.append(err)    # if so, it is tuple! store it
                except:
                    self.export_error_msg = err     # Set the flag and store the message
                    print(err)                      

    def handle_finished_export(self):
        if not self.export_fail and not self.export_error_msg:     # complete success!   
            self.status.showMessage("Export complete", g.SB_DURATION)
        elif not self.export_error_msg:                            # some reps w no data didn't export
            self.status.showMessage("WARNING: Some reps could not be exported.", g.SB_DURATION_ERROR)
            
        else:                                                       # error message from export process
            self.status.showMessage("ERROR: Export could not complete.", g.SB_DURATION_ERROR)
        self.show_export_results_dialog(self.export_success, self.export_fail, self.export_error_msg)
        self.progress_bar.setVisible(False)
        self.export_error_flag = False
        self.process = None

    def show_export_results_dialog(self, yes, no, error=False):
        title = "Export complete."
        msg = "Export complete.\n"
        if error:
            msg = "ERROR MESSAGE:\n"
            msg = msg+error+'\n'
        if no:
            msg = msg+"\nWarning: Failed to export:\n"
            for rep in no:
                rep = literal_eval(rep)
                msg = msg+rep[0]+': '+rep[1]+'\n'
        if yes:
            msg = msg + "\nSuccessully exported:\n"
            for rep in yes:
                rep = literal_eval(rep)
                msg = msg+rep[0]+': '+rep[1]+'\n'

        if no: title = "Warning: some replicates failed to export"
        if error: title = "ERROR on export"
        show_alert(self, title, msg)
        
        



    #############################################
    #                                           #
    #   Functions for asynchronous data read    #
    #                                           #
    #   1. start_async_read                     #
    #   2. handle_read_stdout                   #
    #   3. handle_read_stderr                   #
    #   4. handle_finished_read                 #
    #                                           #
    #############################################

    def start_async_read(self):
        if not self.process:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_read_stdout)
            self.process.readyReadStandardError.connect(self.handle_read_stderr)
            self.process.finished.connect(self.handle_finished_read)
            self.status.showMessage("Loading data...")
            self.progress_bar.setVisible(True)
            self.process.start("python", ['processes/read.py', self.path])

    def handle_read_stdout(self):
        #print('load normal msg!')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.data = literal_eval(stdout)

    def handle_read_stderr(self):
        print('load error msg!')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print(stderr)
        self.read_error_flag = True

    def handle_finished_read(self):
        if self.read_error_flag:
            self.status.showMessage("ERROR: Data read could not complete.", g.SB_DURATION)
        else:
            self.status.showMessage("Data loaded!", g.SB_DURATION)
            self.update_win()
            setWsEnabled(self.buts, True)                                   #   Enable buttons
        self.progress_bar.setVisible(False)
        self.read_error_flag = False
        self.process = None
        


    #############################################
    #                                           #
    #   Functions for asynchronous data save    #
    #                                           #
    #   1. start_async_save                     #
    #   2. handle_save_stdout                   #
    #   3. handle_save_stderr                   #
    #   4. handle_finished_save                 #
    #                                           #
    #############################################

    def start_async_save(self, saveType, params, onSuccess=False, onError=False):
        if not self.process:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_save_stdout)
            self.process.readyReadStandardError.connect(self.handle_save_stderr)
            self.process.finished.connect(partial(self.handle_finished_save, onSuccess, onError))
            self.process.start("python", ['processes/save.py', self.path, saveType, str(params)])
            self.status.showMessage("Saving...")
            self.progress_bar.setVisible(True)

    def handle_save_stdout(self):
        print('normal msg:')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        try:
            data = literal_eval(stdout)
            self.data = data
        except:
            print(data)

    def handle_save_stderr(self):
        print('error msg:')
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        print(stderr)
        self.save_error_flag = True

    def handle_finished_save(self, onSuccess, onError):
        #print('here in finished handler!')
        try:
            self.progress_bar.setVisible(False)                                             # Rehide the progress bar
            self.process = None                                                             # Wipe the process from memory
            if self.save_error_flag:                                                        # If run errored
                self.save_error_flag = False                                                #   Reset flag
                self.status.showMessage("ERROR: Save could not complete.", g.SB_DURATION)   #   Show error message
                if onError:                                                                 #   If there is an onError callback fn
                    onError()                                                               #   run it! 
            else:                                                                           # If the run succeeded
                self.status.showMessage("Saved!", g.SB_DURATION)                            #   Show success message
                self.update_win()                                                           #   Update main window with new data
                if onSuccess:                                                               #   If there is an onSuccess callback fn
                    onSuccess()                                                             #   run it!
                                                                     
        except Exception as e:
            print(e)

            
    #############################################
    #                                           #
    #   Functions that modify children wins     #
    #                                           #
    #############################################

    def set_enabled_children(self, enabled=True):
        for win in self.children:
            win.setEnabled(enabled)

    #############################################
    #                                           #
    #   Close window event handler              #
    #                                           #
    #############################################

    def closeEvent(self, event):
        while self.children:                # loop through children until children is empty
            self.children[0].close()        # closing the 0th child window (closing pops it from list)

        self.parent.children.remove(self)   # remove reference to this window from parent for memory cleanup
        event.accept()
        

class TitleLbl(QLabel):
    def __init__(self, name):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(name)
                 
    def updateTitleLbl(self, new_name):
        self.setText(new_name)


        
        

    
