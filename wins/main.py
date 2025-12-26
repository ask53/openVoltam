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
    QGroupBox,
    QApplication
    
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
        self.config_pane_displayed = False
        self.setObjectName('window-sample')
        self.selected = []                  # for storing which runs are selected
        self.prog_check_flag = False
        self.num_runs = 0
        self.children = [self.w_view_sample, self.w_edit_sample, self.w_run_config, self.w_run]

            

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
        
        
        but_view = QPushButton('info')
        but_config = QPushButton('NEW RUN')
        but_calc = QPushButton('Calculate')
        but_res_sample = QPushButton('Sample results')

        but_view.clicked.connect(self.view_sample_info)
        but_config.clicked.connect(self.config_run)
        but_calc.clicked.connect(self.config_run_with_uid)
        
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
        self.selected = []                                                  # re-init selected list b/c we have reloaded all runs and none 
                                                                            #   are selected to start.
        self.w_run_history_area.setParent(None)                             # remove run history pane from layout
        self.widgetize_run_history()                                        # get updated run history as a widget    
        self.centralWidget().layout().addWidget(self.w_run_history_area)    # add the updated run history back to layout

        print('here!')
        self.w_view_sample.setTextFromFile()                                # Update info in view-sample pane
        

    def config_run(self):
        try:
            self.w_run_config.reset_form()
            self.w_run_config.show()
            
        except Exception as e:
            print(e)

    def config_run_with_uid(self):
        try:
            ##############################################################
            #
            #   PLACEHOLDER!!!   modify this with actual UID of selected run
            #
            uid = 'run-0'
            #
            ##############################################################
            self.w_run_config.reset_form()
            self.w_run_config.set_form(uid)
            self.w_run_config.show()
        except Exception as e:
            print(e)



















    def do_nothing_with_widget(self, w):
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
        return w

    def widgetize_run_history(self):
        
        qss_name_even = 'run-cell-even'                     # name for styling even cells
        qss_name_odd = 'run-cell-odd'                       # name for styling odd cells
        
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
            for j, rep in enumerate(run[g.R_REPLICATES]):
                rep_name = l.r_rep_abbrev[g.L] + ' '+str(j)
                rep_status = rep[g.R_STATUS]
                rep_time = 'TIMESTAMP WHEN RUN COMPLETED'
                rep_notes = rep[g.R_NOTES]
                rep_proc = 'PROCESSING ICONS HERE'
                rep_strs = [rep_name,rep_status,rep_time,rep_notes,rep_proc]
                if row%2 != 0: qss_name = qss_name_even
                else: qss_name = qss_name_odd
                rep_id = rep[g.R_UID_SELF]
                ws_rep = []
                for s in rep_strs:
                    w = self.create_w(s, qss_name, self.rep_clicked, run_id, rep_id)
                    ws_rep.append(w)

                    
                row = self.add_row_to_main(ws_rep, row, h_offset=1)

            
            # Vertically merge all the first cells for this run's replicates and add run information
            run_name = 'Run '+str(i)
            run_type = l.rc_types[run[g.R_TYPE]][g.L]
            method_name = get_method_from_file_data(self.data, run[g.R_UID_METHOD])[g.M_NAME]
            run_notes = run[g.R_NOTES]
            run_str = '<b>'+run_name+'</b><br>'
            run_str = run_str + 'Type: '+run_type+'<br>'
            run_str = run_str + 'Method: '+method_name+'<br>'
            run_str = run_str + 'Notes: '+run_notes

            if i%2 == 0: qss_name = qss_name_even
            else: qss_name = qss_name_odd

            w = self.create_w(run_str, qss_name, self.run_clicked, run_id)
            
            self.add_row_to_main([w], start_row, v_merge=row-start_row)

        #self.num_runs = row+1
        self.grid.setColumnStretch(len(headers)-1,1)                    # Set column stretch on last col so grid fills whole window

        self.w_run_history_container = QWidget()
        self.w_run_history_container.setLayout(self.grid)
        self.w_run_history_container.setObjectName('runs-container')
        self.w_run_history_area.setWidget(self.w_run_history_container)
        

    def rep_clicked(self, w, event):
        print('--------')
        keys = QApplication.keyboardModifiers()
        btn = event.button()

        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:    # regular right click
            print('regular right click')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.NoModifier:   # regular left click
            print('regular left click!')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ControlModifier:   # ctrl+left click
            print('ctrl+click')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ShiftModifier:   # shift+left click
            print('shift+click')
            
        print('run:',w.property('ov-run'))
        print('rep:',w.property('ov-rep'))

    def run_clicked(self, w, event):
        print('--------')
        keys = QApplication.keyboardModifiers()
        btn = event.button()

        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:    # regular right click
            print('regular right click')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.NoModifier:   # regular left click
            print('regular left click!')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ControlModifier:   # ctrl+left click
            print('ctrl+click')

        elif btn == Qt.MouseButton.LeftButton and keys == Qt.KeyboardModifier.ShiftModifier:   # shift+left click
            print('shift+click')
            
        print('run:',w.property('ov-run'))
        print('rep:',w.property('ov-rep'))
        

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

    def setEnabledChildren(self, enable):
        """Takes in a boolean, "enable" and sets all children's enabled status
        to that boolena, either enabling or disabling all"""
        for win in self.children:
            win.setEnabled(enable)

    def start_run(self, uid):
        self.w_run.set_run_uid(uid)
        self.w_run.show()

    def closeEvent(self, event):
        for win in self.children:
            win.close()
        event.accept()


class TitleLbl(QLabel):
    def __init__(self, name):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(name)
                 
    def updateTitleLbl(self, new_name):
        self.setText(new_name)
