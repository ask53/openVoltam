"""
window_sample.py

This file defines a class WindowSample which creates a window object
that can be used to do a bunch of things. This is the main window that the
user will primarily use while operating the GUI.

The user can configure new runs, initiate runs, collect data, analyze data,
export data, view all past runs and analysis, and perhaps run calculations
"""
# import global vars, language pack, and functions
from global_scripts import ov_globals as g
from global_scripts import ov_lang as l
from global_scripts.ov_functions import *

# import necessary windows
from wins.sample import WindowSample
from wins.method import WindowMethod
from wins.runConfig import WindowRunConfig
from wins.runView import WindowRunView
from wins.resultsView import WindowResultsView
from wins.analyze import WindowAnalyze
from wins.calculate import WindowCalculate

# import other necessary python tools
from os.path import join as joindir
from os.path import exists
from functools import partial
from ast import literal_eval
from time import sleep

# import PyQt6/PySide6 stuff
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QAction, QFont, QIcon
from PyQt6.QtCore import QDate, Qt, QProcess, QSize, QMargins
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedLayout,
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
    QMessageBox,
    QLineEdit,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView
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
        self.layout_old = {}
        self.tabs = None
        self.tab_ids = []
        self.current_tab = 0
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
        action_method_run_edit = QAction('Edit run method', self)

        action_run_new = QAction('New run', self)
        action_run_new_from = QAction('New run from config', self)
        action_run_view = QAction('View info', self)
        action_run_edit = QAction('Edit info', self)
        action_run_export = QAction('Export as CSV', self)
        action_run_delete = QAction('Delete', self)

        action_rep_edit = QAction('Edit note', self)
        action_rep_export = QAction('Export as CSV', self)
        action_rep_delete = QAction('Delete', self)

        action_analyze_peaks = QAction('Analyze', self)
        action_analyze_calculate = QAction('Calculate', self)
        action_analyze_results = QAction('Results', self)
        
        # connect menu bar labels with slots 
        action_sample_new.triggered.connect(parent.new_session)                      # this first group of menu functions come from the home window (parent)
        action_sample_open.triggered.connect(parent.open_session)
        action_sample_close.triggered.connect(self.close)

        action_method_new.triggered.connect(parent.new_method)
        action_method_open.triggered.connect(parent.open_method)
        action_method_run_view.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_ONLY))
        action_method_run_edit.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_WITH_MINOR_EDITS))

        action_run_new.triggered.connect(partial(self.new_win_config_run, g.WIN_MODE_NEW))
        action_run_new_from.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_NEW))
        action_run_view.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_VIEW_ONLY))
        action_run_edit.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_EDIT))
        action_run_export.triggered.connect(self.export_selected_reps_as_csv)
        action_run_delete.triggered.connect(self.delete_reps)

        action_rep_edit.triggered.connect(self.edit_rep_note)
        action_rep_export.triggered.connect(self.export_selected_reps_as_csv)
        action_rep_delete.triggered.connect(self.delete_reps)

        action_analyze_peaks.triggered.connect(self.anayze_data_selected_reps)
        action_analyze_calculate.triggered.connect(partial(self.new_win_calculator, g.WIN_MODE_NEW))
        action_analyze_results.triggered.connect(partial(self.new_win_calculator, g.WIN_MODE_RIGHT))
        
        

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
        file_menu.addAction(action_rep_edit)
        file_menu.addSeparator()
        file_menu.addAction(action_rep_export)
        file_menu.addSeparator()
        file_menu.addAction(action_rep_delete)

        file_menu = menu.addMenu('Analysis')
        file_menu.addAction(action_analyze_peaks)
        file_menu.addAction(action_analyze_calculate)
        file_menu.addAction(action_analyze_results)

        self.actions_run_one_only = [action_run_new_from,
                                     action_run_view,
                                     action_run_edit,
                                     action_method_run_view,
                                     action_method_run_edit]
        self.actions_run_one_plus = [action_run_export,
                                     action_run_delete,
                                     action_analyze_peaks]
        self.actions_rep_one_only = [action_rep_edit]
        self.actions_rep_one_plus = [action_rep_export,
                                     action_rep_delete,
                                     action_analyze_peaks]
        

        #####################################
        #                                   #
        #   right-click ("context") menu    #
        #                                   #
        #####################################
        
        self.context_menu = QMenu(self)      # Menu for when run is clicked
        #self.contextmenu_rep = QMenu(self)      # Menu for when rep is clicked

        self.a_runAgain = self.context_menu.addAction("New run from config")
        self.context_menu.addSeparator()
        self.a_viewConfig = self.context_menu.addAction("Run info")
        self.a_viewMethod = self.context_menu.addAction("Method info")
        self.move_to_menu = QMenu('Move to...')
        self.move_to_menu_actions = []
        self.context_menu.addMenu(self.move_to_menu)
        
        self.context_menu.addSeparator()
        self.a_editRepNote = self.context_menu.addAction("Edit rep note")
        self.context_menu.addSeparator()
        self.a_graph = self.context_menu.addAction("Graph")
        self.a_analyze = self.context_menu.addAction("Analyze")
        self.a_export = self.context_menu.addAction("Export")
        self.context_menu.addSeparator()
        self.a_delete = self.context_menu.addAction("Delete")



        





        '''self.repAction_editNote = self.contextmenu_rep.addAction("Edit replicate note")
        self.contextmenu_rep.addSeparator()
        self.repAction_viewData = self.contextmenu_rep.addAction("Graph")
        self.repAction_analyzeData = self.contextmenu_rep.addAction("Analyze")
        self.repAction_exportData = self.contextmenu_rep.addAction("Export")
        self.contextmenu_rep.addSeparator()
        self.repAction_delete = self.contextmenu_rep.addAction("Delete replicates(s)")'''

        self.a_runAgain.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_NEW))
        self.a_viewConfig.triggered.connect(partial(self.open_run_config_with_uid, g.WIN_MODE_VIEW_ONLY))
        self.a_viewMethod.triggered.connect(partial(self.open_method_with_uid, g.WIN_MODE_VIEW_ONLY))
        self.a_editRepNote.triggered.connect(self.edit_rep_note)
        self.a_graph.triggered.connect(self.view_data_selected_reps)
        self.a_analyze.triggered.connect(self.anayze_data_selected_reps)
        self.a_export.triggered.connect(self.export_selected_reps_as_csv)
        self.a_delete.triggered.connect(self.delete_reps)
        
        '''self.repAction_editNote.triggered.connect(self.edit_rep_note)
        self.repAction_viewData.triggered.connect(self.view_data_selected_reps)
        self.repAction_analyzeData.triggered.connect(self.anayze_data_selected_reps)
        self.repAction_exportData.triggered.connect(self.export_selected_reps_as_csv)
        self.repAction_delete.triggered.connect(self.delete_reps)'''

        self.run_actions_one = [self.a_runAgain,
                                self.a_viewConfig,
                                self.a_viewMethod]
        self.rep_actions_one = [self.a_editRepNote]
        
        #####################
        #                   #
        #   page layout     #
        #                   #
        #####################

        lay = QVBoxLayout()
        
        but_view = QPushButton()
        but_view.setIcon(QIcon(g.ICON_EDIT))
        but_samp = QPushButton('New sample')
        but_config = QPushButton('New run')
        but_calc = QPushButton('Calculate')
        but_res_sample = QPushButton('Results')
        self.buts = [but_view, but_samp, but_res_sample]
        
        but_view.clicked.connect(self.edit_session_name)
        but_samp.clicked.connect(self.new_sample)
        but_config.clicked.connect(self.new_run)
        #but_config.clicked.connect(partial(self.new_win_config_run, g.WIN_MODE_NEW))
        #but_calc.clicked.connect(partial(self.new_win_calculator, g.WIN_MODE_NEW))
        but_res_sample.clicked.connect(partial(self.new_win_calculator, g.WIN_MODE_RIGHT))

        self.lbl_sample_name = TitleLbl("")
        self.lbl_sample_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        l_session_header = QHBoxLayout()
        l_session_header.addWidget(self.lbl_sample_name)
        l_session_header.addWidget(but_view)
        l_session_header.addStretch()
        l_session_header.addWidget(but_samp)
        l_session_header.addWidget(QVLine())
        l_session_header.addWidget(but_config)
        l_session_header.addWidget(QVLine())
        l_session_header.addWidget(but_calc)
        l_session_header.addWidget(but_res_sample)

        w_session_header = QWidget()                         # create a widget to hold the layout (which can be styled)
        w_session_header.setLayout(l_session_header)          # add the layout to the widget
        w_session_header.setObjectName("session-header")      # add a name to target with QSS

        # Create a placeholder widget where the main window will go
        lay_ph = QVBoxLayout()
        lay_ph.addWidget(QWidget())
        lay_ph.addStretch()
        w_ph = QTabWidget()
        w_ph.setLayout(lay_ph)
        
        # Add both of these widgets to our vertical layout
        lay.addWidget(w_session_header)     # add the header
        lay.addWidget(w_ph)                 # add a placeholder widget for the main area

        setWsEnabled(self.buts, False)

        #####################
        #                   #
        #   begin data read #
        #                   #
        ##################### 
        self.start_async_read()
        
        # Display! 
        self.w = QWidget()
        self.w.setLayout(lay)
        self.setCentralWidget(self.w)
        
    def update_win(self):
        try:
            
            self.layout_old = self.layout.copy()                # Store copy of old layout
            self.layout = {}                                    # Reinit self.layout to be refilled 
            sample_name = self.data[g.S_NAME]
            self.setWindowTitle(sample_name)                                    # Set the sample window title
            self.lbl_sample_name.updateTitleLbl(sample_name)                    # Set the sample name
            print('1')
            self.set_move_to_menu()
            self.set_main_area()
            print('2')
            self.update_highlights()
            print('2a')
            self.update_menu()
            print('3')
            self.update_children()
            #self.resizeEvent(None)
        except Exception as e:
            print(e)


    def set_move_to_menu(self):
        self.move_to_menu.clear()
        for i, s in enumerate(self.data[g.S_SAMPLES]):
            action = self.move_to_menu.addAction(s[g.SA_NAME])
            action.triggered.connect(partial(self.move_to, i))
            self.move_to_menu_actions.append(action)
        
        

    def move_to(self, i):
        """moves a selected run (with all its reps) to the sample with index i"""
        print('moving to '+str(i))
        
        
        
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

    def set_main_area(self):
        if self.tabs:
            self.current_tab = self.tabs.currentIndex()     # save current tab

        # If there are samples, create tabbed layout
        d = self.data

        
        for insert_i, w in enumerate(self.centralWidget().children()):
            if type(w) == type(QTabWidget()):
                w.setParent(None)
                break
        
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_changed)
        self.tab_ids = []
        
        for i, sample in enumerate(d[g.S_SAMPLES]):
            # Set up sample header
            lbl_s_name = QLabel("<div style='font-size: 16pt'>"+sample[g.SA_NAME]+"</div>")
            lbl_s_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl_s_name.setWordWrap(True)
            desc = self.get_sample_description(sample)
            lbl_desc = QLabel(desc)
            lbl_desc.setWordWrap(True)
            lbl_desc.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

            but_edit = QPushButton()
            but_edit.setIcon(QIcon(g.ICON_EDIT))
            but_edit.clicked.connect(self.edit_sample)
            but_del = QPushButton()
            but_del.setIcon(QIcon(g.ICON_TRASH))

            v = QVBoxLayout()
            v.addWidget(lbl_s_name)
            v.addLayout(horizontalize([but_edit, but_del]))
            
            if desc:
                v.addWidget(lbl_desc)
            
            w0 = QWidget()
            w0.setLayout(v)
            color_index = i%7
            w0.setObjectName('sample-'+str(color_index))

            v2 = QVBoxLayout()
            v2.addWidget(w0)
            v2.addStretch()

            h = QHBoxLayout()
            h.addLayout(v2)
            
            # IF there are runs, setup sample tree
            runs = get_runs_in_sample(self.data, sample[g.R_UID_SELF])
            if runs:
                w_cust=self.widgetize_runs(sample[g.R_UID_SELF])
                h.addWidget(w_cust)
            else:                       # if there are not runs
                #v.addStretch()          # add a stretch to the layout to keep everything nice and tidy
                h.addStretch()

            
            w = QWidget()
            #w.setLayout(v)
            w.setLayout(h)
            
            self.tabs.addTab(w, sample[g.SA_NAME])
            self.tab_ids.append(sample[g.R_UID_SELF])

        self.centralWidget().layout().insertWidget(insert_i, self.tabs)  # insert tab widget to same spot previous tab widget was located (this preserves stretches, animationes, etc.)
        self.tabs.setCurrentIndex(self.current_tab)         # activate tab (this is needed to stay on same tab during ongoing use, rather than jumping to tab 0)
        applyStyles()

    
    def get_sample_description(self, s):
        """Takes in a sample object, s, returns html string of description"""
        d = ''
        if s[g.SA_DATE_COLLECTED] and s[g.SA_DATE_COLLECTED] != g.QT_DEFAULT_DATE:
            d = d + '<b>Date collected</b>: '+s[g.SA_DATE_COLLECTED] + '<br>'
        if s[g.SA_LOC_COLLECTED] and not self.is_only_whitespace(s[g.SA_LOC_COLLECTED]):
            d = d + '<b>Location</b>: '+s[g.SA_LOC_COLLECTED] + '<br>'
        if s[g.SA_COLLECTED_BY] and not self.is_only_whitespace(s[g.SA_COLLECTED_BY]):
            d = d + '<b>By</b>: '+s[g.SA_COLLECTED_BY] + '<br>'
        if s[g.SA_NOTES] and not self.is_only_whitespace(s[g.SA_NOTES]):
            d = d + '<b>Notes</b>: '+s[g.SA_NOTES] + '<br>'
        d = d[0:-4]                                                             # remove final <br>
        return d

    def is_only_whitespace(self, s):
        """returns True is string s is only whitespace (spaces, tabs, returns, etc.)
        and False otherwise"""
        if  "".join(s.split()) == "":
            return True
        return False
        
    def edit_sample(self):
        try:
            s_id = self.get_current_sample_id()
            self.new_win_one_with_value(WindowSample(self, mode=g.WIN_MODE_EDIT, sample_id=s_id), "sample_id", s_id)
        except Exception as e:
            print(e)

    def get_current_sample_id(self):
        i = self.tabs.currentIndex()
        return self.tab_ids[i]
        

    def new_sample(self):
        try:
            self.new_win_one_of_type(WindowSample(self, g.WIN_MODE_NEW))
        except Exception as e:
            print(e)

    def new_run(self):
        sample_id = self.get_current_sample_id()
        self.new_win_config_run(g.WIN_MODE_NEW, sample_id=sample_id)

    def tab_changed(self):
        if not self.tab_ids:
            return
        try:
            i = self.tabs.currentIndex()
            sample_id = self.tab_ids[i]
            for run in self.layout.keys():
                if self.layout[run]['sample_id'] != sample_id:
                    self.layout[run]['selected'] = []
            self.update_highlights()
            self.scroll_area_resized()
        except Exception as e:
            print('here in the tab_changed error handler:')
            print(e)

    def widgetize_runs(self, sample_id):
        
        grid = QGridLayout()                           # init grid layout (that is inside scroll area)
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(0)
        
        # create column headers and add them to the grid layout
        headers = ['','Replicate', 'Status', 'Datetime', 'Notes', 'Analyzed']
        w_heads = []
        for header in headers:
            w = self.create_w(header, qss_name='run-col-header')
            w_heads.append(w)

        row = 0
        row = self.add_row_to_main(grid, w_heads, row)

        # Loop through all runs in sample's dataset
        for i, run in enumerate(self.data[g.S_RUNS]):
            if run[g.R_UID_SAMPLE] == sample_id:
                # For each run, create a row for each replicate and add it to the grid, leaving the first cell of each row blank
                start_row = row
                run_id = run[g.R_UID_SELF]
                self.layout[run_id] = {'sample_id':sample_id,
                                       'selected':[],
                                       'reps':[]}                     # initialize holing spot for run data 
                for j, rep in enumerate(run[g.R_REPLICATES]):
                    rep_name = l.r_rep_abbrev[g.L] + ' '+rep[g.R_UID_SELF].split('-')[-1]
                    rep_status = rep[g.R_STATUS]
                    rep_time = rep[g.R_TIMESTAMP_REP]
                    rep_notes = rep[g.R_NOTES]
                    rep_proc = ''
                    if rep[g.R_ANALYSIS]: rep_proc = g.ICON_CHECK
                    rep_strs = (rep_name,rep_status,rep_time,rep_notes,rep_proc)
                    icons = (False, False, False, False, True)

                    is_last = False
                    if j == len(run[g.R_REPLICATES])-1: is_last=True                # figure out if current rep is last of run

                    if j%2 == 0 and is_last: qss_name = 'run-rep-even-last'     # even rows that are last rep of run
                    elif j%2 != 0 and is_last: qss_name = 'run-rep-odd-last'    # odd rows that are last rep of run
                    elif j%2 == 0: qss_name = 'run-rep-even'                    # regular even rows
                    else: qss_name = 'run-rep-odd'                                  # regular odd rows
                    
                    rep_id = rep[g.R_UID_SELF]
                    ws_rep = []
                    for k,s in enumerate(rep_strs):
                        if k==len(rep_strs)-1:
                            qss_name = qss_name + '-right'
                        w = self.create_w(html_escape(s), qss_name, self.rep_clicked, run_id, rep_id, is_icon=icons[k])
                        ws_rep.append(w)   
                    row = self.add_row_to_main(grid, ws_rep, row, h_offset=1)
                    self.layout[run_id]['reps'].append(rep_id)
                
                # Vertically merge all the first cells for this run's replicates and add run information
                run_name = 'Run '+run[g.R_UID_SELF].split('-')[-1]
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
                
                self.add_row_to_main(grid, [w], start_row, v_merge=row-start_row)

        grid.setColumnStretch(len(headers)-1,1)

        # update self.layout to ensure that highlights maintain over update
        for run in self.layout_old:
            if run in self.layout:
                for rep in self.layout_old[run]['selected']:
                    if rep in self.layout[run]['reps']:
                        self.layout[run]['selected'].append(rep)
        
        w_in = QWidget()
        w_in.setLayout(grid)
        w_in.setObjectName('runs-container')
        
        w = QRunScrollArea(self)
        w.setWidget(w_in)

        return w

    def sa_resize(self):
        print('RESIZE DETECTED!')
 
    def do_nothing(self, w):
        """This is necessary so that each widget has a callback function if clicked.
        Pls don't delete even tho is looks oh so deleteable!"""
        return

    def create_w(self, s, qss_name, onclick_fn=do_nothing, run_id=False, rep_id=False, word_wrap=True, is_icon=False):
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
        if is_icon:
            w.setPixmap(QIcon(s).pixmap(QSize(20,20)))
        w.setTextFormat(Qt.TextFormat.RichText)
        w.setWordWrap(word_wrap)
        w.setObjectName(qss_name)
        w.mouseReleaseEvent = partial(onclick_fn, w)
        w.setProperty('ov-run', run_id)
        w.setProperty('ov-rep', rep_id)     
        w.setProperty('ov-qss-name', qss_name)          # store qss name for easy access later (to reset styles)
        w.setProperty('ov-selected-qss-name', 'selected-'+qss_name)
        return w

    def add_row_to_main(self, grid, ws, row, h_offset=0, v_merge=1, h_merge=1):
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
            grid.addWidget(w, row, i+h_offset, v_merge, h_merge)
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
        try:
            if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:        # regular right click
                if not self.rep_is_selected(run, rep):                                              # If the clicked rep is not selected
                    self.clear_selected()                                                           # Make it the only one selected
                    self.add_rep_to_selected(run, rep)
                    self.update_highlights()
                self.open_rightclick_menu(event)                                                    # Open right-click context menu

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
            self.update_highlights()                                                            # update styles to apply hightlighting
        except Exception as e:
            print('here in the rep_clicked error handler!')
            print(e)
        


    def run_clicked(self, w, event):
        keys = QApplication.keyboardModifiers()
        btn = event.button()
        run = w.property('ov-run')


        if btn == Qt.MouseButton.RightButton and keys == Qt.KeyboardModifier.NoModifier:    # regular right click
            if not self.all_reps_of_run_are_selected(run):
                self.clear_selected()
                self.add_run_to_selected(run)
                self.update_highlights()
            self.open_rightclick_menu(event)

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
        """ Returns Int, # of runs with any reps currently selected"""
        N = 0
        for run in self.layout.keys():
            if self.layout[run]['selected']:
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

    def get_scroll_area(self, i):
        """Returns the children of the QScrollArea widget in the tab i. If there is no
        QScrollArea widget found, or if it has no set widget ithin it, returns False."""
        for child in self.tabs.widget(i).children():
            if type(child) == type(QRunScrollArea(self)):
                return child
        return False
        
    
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
        
        tab_i = self.tabs.currentIndex()
        sa = self.get_scroll_area(tab_i)
        ws = False
        try: ws = sa.widget().children()    # get the children
        except: pass                        # if no widget set, ignore the error

        if ws:
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
        

    '''def select_all_lbl_clicked(self, event):        # this exists so that the "select all" label can be clicked
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
            self.cb_all.setChecked(False)'''

    def update_menu(self):
        print('-')
        runs = self.N_runs_selected()
        print('--')
        reps = self.N_reps_selected()
        print('---')
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
    #   1. open_rightclick_menu                 #
    #                                           #
    #############################################

    def open_rightclick_menu(self, event):
        reps = self.N_reps_selected()   # Get count of selected replicates
        runs = self.N_runs_selected()   # get count of all runs with at least one rep selected
        for action in self.rep_actions_one:
            if reps == 1: action.setEnabled(True)
            else: action.setEnabled(False)
        for action in self.run_actions_one:
            if runs == 1: action.setEnabled(True)
            else: action.setEnabled(False)
        if reps or runs:
            self.context_menu.exec(event.globalPosition().toPoint())

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
    #   5. delete_reps                          #
    #   6. confirm_delete                       #
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
                self.start_async_save(g.SAVE_TYPE_REP_MOD, [[(run_id, rep_id)], [rep]])

    def open_run_config_with_uid(self, mode):
        """Finds the first selected run (assumes there is only one run selected!)
        and opens up a new run configuration window with all of the parameters
        preset to match the currently selected run"""
        try:
            run_id = self.get_single_selected_run()
            if run_id:
                self.new_win_config_run(mode, run_id)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

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

    def view_data_selected_reps(self):
        reps = self.get_all_selected_reps()
        self.new_win_results_view(reps)

    def anayze_data_selected_reps(self):
        reps = self.get_all_selected_reps()

        # Check which reps actually have data
        all_data = get_data_from_file(self.path)
        for i, rep in reversed(list(enumerate(reps))):
            full_rep = get_rep(all_data, rep)
            if not full_rep[g.R_DATA]:
                reps.pop(i)
        if not reps:                        # If none of the selected reps have data, alert the user
            show_alert(self, "Alert", "None of the selected runs have data, please collect some data and try again.")
        else:                               # IF at least one has data, analyze that data!
            self.new_win_analysis(reps)

    def export_selected_reps_as_csv(self):
        reps = self.get_all_selected_reps()
        dest = get_path_from_user(self, 'folder')
        if dest:
            self.start_async_export(reps, dest)

    def delete_reps(self):
        reps = self.get_all_selected_reps()                                             # Get selected reps
        continue_action, calcs_to_archive = check_calc_conflict(self.data, reps)        # Confirm whether user wants to continue, given this impacts calcs
        if not continue_action:                                                         
            return
        if self.confirm_delete():                                                       # Confirm user wants to delete
            callback = partial(self.start_async_save, g.SAVE_TYPE_CALCS_ARCHIVE, [True, calcs_to_archive])  # Define callback fn to archive impacted calcs
            self.start_async_save(g.SAVE_TYPE_REP_DELETE, [reps], onSuccess=callback)   # Delete selected reps (and maybe their parent runs and connected methods) from file

   
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
    #   1. edit_session_name                       #
    #   2. new_win_config_run                   #
    #   3. new_win_view_run                     #
    #   4. new_win_method_by_id                 #
    #   5. new_win_method_by_path               #
    #   6. new_win_results_view                 #
    #   7. new_win_analysis                     #
    #   8. new_win_calculator                   #
    #
    #
    #
    #   9. new_win_one_of_type                  #
    #   10. new_win_one_with_value              #
    #   11. update_children                     #
    #                                           #
    #############################################

    def edit_session_name(self, oldname):
        try:
            title = 'Edit lab session name'
            text = 'Lab session name:'
            oldname = self.data[g.S_NAME]
            newname, ok = QInputDialog().getText(self, title, text, text=oldname)
            print(ok)
            print(newname)
            if ok and newname != oldname:
                self.start_async_save(g.SAVE_TYPE_EDIT_SESH_NAME, [newname])
        except Exception as e:
            print(e)
            
        


        
        #self.new_win_one_of_type(WindowSample(self, g.WIN_MODE_VIEW_ONLY))

    def new_win_config_run(self, mode, run_id=False, sample_id=False):
        self.new_win_one_of_type(WindowRunConfig(self, mode, run_id, sample_id))

    def new_win_view_run(self, tasks):
        self.new_win_one_of_type(WindowRunView(self, tasks))

    def new_win_method_by_id(self, mode, m_id, changable=True):
        self.new_win_one_with_value(WindowMethod(self, mode, method_id=m_id, mode_changable=changable), 'method_id', m_id)

    def new_win_method_by_path(self, mode, path, changable=True):
        self.new_win_one_with_value(WindowMethod(self, mode, path=path, mode_changable=changable), 'path', path)

    def new_win_results_view(self, tasks):
        self.new_win_one_with_value(WindowResultsView(self, tasks), 'tasks', tasks)

    def new_win_analysis(self, tasks):
        self.new_win_one_of_type(WindowAnalyze(self, tasks))
        
    def new_win_calculator(self, mode):
        tasks = None
        if mode == g.WIN_MODE_NEW:                  # if we want a new calculation
            tasks = self.get_all_selected_reps()    #   grab all selected reps and try
            if not tasks: tasks = None              #   to start the calc with them
        try:
            self.new_win_one_of_type(WindowCalculate(self, mode, suggestion=tasks))
        except Exception as e:
            print(e)
            
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
            if g.PROC_RUN_FROM == g.PROC_RUN_FROM_PYTHON:
                self.process.start('python', [g.PROC_SCRIPT_PYTHON, g.PROC_TYPE_EXPORT, self.path, destPath, str(reps)])
            else:
                self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_EXPORT, self.path, destPath, str(reps)])            

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
        print("hello, i'm an async read!")

        ##############
        #
        #   HERE! Sort async process stuff for linux
        #
        #
        #################

        if not self.process:
            self.process = QProcess()
            self.process.readyReadStandardOutput.connect(self.handle_read_stdout)
            self.process.readyReadStandardError.connect(self.handle_read_stderr)
            self.process.finished.connect(self.handle_finished_read)
            self.status.showMessage("Loading data...")
            self.progress_bar.setVisible(True)
            
            
            if g.PROC_RUN_FROM == g.PROC_RUN_FROM_PYTHON:
                self.process.start('python', [g.PROC_SCRIPT_PYTHON, g.PROC_TYPE_READ, self.path])
            else:
                self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_READ, self.path])

    def handle_read_stdout(self):
        print('load normal msg!')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        try:
            self.data = literal_eval(stdout)
            #print(self.data)
        except:
            print('ERROR on literal eval of stdout:')
            print(stdout)

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
            print('a')
            self.update_win()
            print('b')
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
        if self.process:        # if there is alreayd a process running
            return              # don't start another one! 
        
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_save_stdout)
        self.process.readyReadStandardError.connect(self.handle_save_stderr)
        self.process.finished.connect(partial(self.handle_finished_save, onSuccess, onError))
        self.status.showMessage("Saving...")
        self.progress_bar.setVisible(True)

        if g.PROC_RUN_FROM == g.PROC_RUN_FROM_PYTHON:
            self.process.start('python', [g.PROC_SCRIPT_PYTHON, g.PROC_TYPE_SAVE, self.path, saveType, str(params)])
        else:
            self.process.start(g.PROC_SCRIPT, [g.PROC_TYPE_SAVE, self.path, saveType, str(params)])

            

    def handle_save_stdout(self):
        print('normal msg:')
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        #print(stdout)
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
    #   Window resize event handler             #
    #                                           #
    #############################################

    def scroll_area_resized(self):
        if not self.tabs:
            return
        try:
            i = self.tabs.currentIndex()
            sa = self.get_scroll_area(i)
            if sa:
                w = False
                try: w = sa.widget()
                except: pass
                if w:
                    wid_sa = sa.width()
                    wid_win = self.width()
                    sa_border_wid = 1
                    wid = wid_sa - sa_border_wid                  #   match our width to the qscrollarea width (minus any border width)
                    sbar = sa.verticalScrollBar()
                    if sbar.isVisible():                # if the scrollbar is visible
                        wid = wid - sbar.width()    # adjust our width accordingly
                    w.setMinimumWidth(wid)
                    w.setMaximumWidth(wid)
        except Exception as e:
            print('window resize handler:')
            print(e)

    #############################################
    #                                           #
    #   Close window event handler              #
    #                                           #
    #############################################

    def closeEvent(self, event):
        if self.children:                       # if there are child windows open, confirm user wants all windows to close
            msg_box = QMessageBox()    
            msg_box.setWindowTitle("Are you sure?") 
            msg_box.setText('This will close this sample and all associated windows including active runs, run configurations, and analysis.\n\nAre you sure you want to close?\n')
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

            # customize button language text for multi-language support
            but_close = msg_box.button(QMessageBox.StandardButton.Ok)
            but_close.setText('Close')
            but_canc = msg_box.button(QMessageBox.StandardButton.Cancel)
            but_canc.setText('Cancel')

            resp = msg_box.exec()
        else:                                   # if the main window has no open child windows, don't show warning
            resp = QMessageBox.StandardButton.Ok
            
        if resp == QMessageBox.StandardButton.Ok:
            current_child = False
            while self.children:                # loop through children until children is empty
                if self.children[0] == current_child:   # if we arrive at a child twice (we failed to close it)
                    event.ignore()                      # stop the close
                    return                              # and stop trying to close children
                current_child = self.children[0]
                self.children[0].close()        # closing the 0th child window (closing pops it from list)
                

            self.parent.children.remove(self)   # remove reference to this window from parent for memory cleanup
            event.accept()
        else:
            event.ignore()
        

class TitleLbl(QLabel):
    def __init__(self, name):
        super(QLabel, self).__init__()
        self.setObjectName(encodeCustomName(g.S_NAME))
        self.setText(name)
                 
    def updateTitleLbl(self, new_name):
        self.setText(new_name)


class QRunScrollArea(QScrollArea):
    def __init__(self, parent):
        super(QScrollArea, self).__init__()
        self.parent = parent

    def resizeEvent(self, event):
        self.parent.scroll_area_resized()
        

        
        

    
