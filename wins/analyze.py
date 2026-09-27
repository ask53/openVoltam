"""
analyze.py

A window that displays as many graphs, one by one, for the user
to analyze.

Whenever possible, an autoanalysis is generated. However, the user
always has the option to modify as they see fit.

The following controls are provided:
    - Next: Brings user to next plot
    - Save: Saves all analysis conducted so far to file (only visible from last task)
    - Progress pane: clickable links to jump to any task
"""

from global_scripts.ov_functions import *
from global_scripts import ov_globals as g

from embeds.voltamOGram import VoltamogramPlot

from functools import partial
from time import sleep

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QStackedLayout,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
)

class WindowAnalyze(QMainWindow):
    def __init__(self, parent, tasks):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.status = self.statusBar()
        self.parent = parent
        self.tasks = tasks
        self.saved = False
        self.results = []
        self.force_close = False
        self.settings = None
        self.update_settings()
        
        # Load previous analysis
        for i, task in enumerate(self.tasks):               # for each task
            prev_a = get_analysis(self.parent.data, task)
            if prev_a:                                      # load previous analysis
                self.results.append(prev_a)                 #   if possible
            else:                                           # if not, load an empty dict
                self.results.append({})

        self.stack = QStackedLayout()
        self.voltamograms = []
        self.titles = []

        #Create pane in stack for each task
        for task in self.tasks:

            #title = QLabel('<b>'+task[0]+'  |  '+task[1]+'</b>')
            title = QLabel('')
            title.setObjectName('analysis-title-txt')
            vgram = VoltamogramPlot(self, self.settings)
            self.titles.append(title)
            self.voltamograms.append(vgram)

            h = QHBoxLayout()
            h.addStretch()
            h.addWidget(title)
            h.addStretch()
            w_top = QWidget()
            w_top.setLayout(h)
            w_top.setObjectName('analysis-title-bar')
            
            
            v = QVBoxLayout()
            v.addWidget(w_top)
            v.addWidget(vgram)
            v.addStretch()
            
            w = QWidget()
            w.setLayout(v)
            self.stack.addWidget(w)


        # Create button for each task in progress sidebar
        self.buts = []
        for i, task in enumerate(tasks):
            but = QPushButton()
            but.clicked.connect(partial(self.go_to_rep, i))
            self.buts.append(but)

        # Do rest of flat (not stacked) layout
        self.prog_lbl = QLabel('')
        v1 = QVBoxLayout()
        v1.addWidget(self.prog_lbl)
        for but in self.buts:
            v1.addWidget(but)
        v1.addStretch()

        self.helptext = QLabel('')
        h0 = QHBoxLayout()
        h0.addStretch()
        h0.addWidget(self.helptext)
        h0.addStretch()

        self.but_results = QPushButton('')
        self.but_results.clicked.connect(self.show_results)
        self.but_next = QPushButton()
        self.but_next.clicked.connect(self.next_click)

        h1 = QHBoxLayout()
        h1.addWidget(self.but_results)
        h1.addStretch()
        h1.addWidget(self.but_next)

        v2 = QVBoxLayout()
        v2.addLayout(self.stack)
        v2.addLayout(h0)
        v2.addLayout(h1)        

        h2 = QHBoxLayout()
        h2.addLayout(v1)
        h2.addWidget(QVLine())
        h2.addStretch()
        h2.addLayout(v2)

        # set form
        starting_index = self.stack.currentIndex()
        self.update_buttons(starting_index)
        self.refresh_progress(starting_index)
        self.set_graph(starting_index)
        
        # Set all text
        self.set_text(self.settings[g.SET_LANG])

        w = QWidget()
        w.setLayout(h2)
        self.setCentralWidget(w)
        applyStyles()

        

        

    
    def next_click(self):
        try:
            self.store_results()
            self.process_next()
        except Exception as e:
            print(e)

    def get_results(self):
        i = self.stack.currentIndex()
        r = self.voltamograms[i].get_analysis_results()
        return i, r

    def show_results(self):
        i, r = self.get_results()
        lang = self.settings[g.SET_LANG]
        #types_eng = ('Peak ht (from base)', 'Peak ht (from 0)', 'Deriv (L)', 'Derv (R)', 'Deriv (avg)', 'Area')
        msg = ''
        for i, t in enumerate(g.C_TYPES):
            val = str(round(get_analyzed_value(r, t), 4))
            msg = msg + get_text(l.ANA_C_TYPES[t], lang) + ' = ' + val + ' |  '
            if i == len(g.C_TYPES)-1:
                msg = msg[0:-3]                 # remove end separator from last value
        self.status.showMessage(msg)


    def vgram_updated(self):
        """A Hndler to be called by the embedded voltamogram"""
        self.hide_results()
            


    def hide_results(self):
        self.status.clearMessage()
        
    def store_results(self):
        i, r = self.get_results()
        self.results[i] = r
        
    def process_next(self):
        self.hide_results()
        if self.stack.currentIndex() == len(self.tasks)-1:  # if we're on last task already
            saved = self.save_and_close()                   #   try to save
        else:                                               # if we're not on the last task,
            i = self.stack.currentIndex()                   #   go to the next task
            self.go_to_rep(i+1)                                          

    def go_to_rep(self, i):
        try:
            self.set_graph(i)
        except Exception as e:
            print(e)
        self.stack.setCurrentIndex(i)
        self.update_buttons(i)
        self.refresh_progress(i)

    def set_graph(self, i):
        try:
            lines = self.voltamograms[i].get_line_count()
            if lines == 0:
                self.voltamograms[i].plot_reps([self.tasks[i]], subbackground=True, showsmoothed=True, showraw=True, predictpeak=True)
                if self.results[i]:
                    self.voltamograms[i].set_analysis(self.results[i])
        except Exception as e:
            print(e)
        

    def update_buttons(self, i):
        lang = self.settings[g.SET_LANG]
        if i == len(self.tasks)-1:  # if we are on the final task
            txt(self.but_next, l.ANA_BUT_SAVE, lang)
        else:                       # if we are on any other task
            txt(self.but_next, l.ANA_BUT_NEXT, lang)
        
    def refresh_progress(self, i):
        lang = self.settings[g.SET_LANG]
        for j,but in enumerate(self.buts):
            # set progress pane element color/border
            if j==i: but.setObjectName('task-selected') 
            elif self.results[j]: but.setObjectName('task-complete')
            else: but.setObjectName('task-pending')

            # Set progress pane element text
            run_id, rep_id = self.tasks[j]
            run_n, rep_n = get_run_num(run_id), get_rep_num(rep_id)
            run_s, rep_s = get_text(l.ANA_RUN_ABRV, lang)+run_n, get_text(l.ANA_REP_ABRV, lang)+rep_n
            s = run_s + ', ' + rep_s
            if self.results[j]: but.setText(s+'  |  '+ get_text(l.ANA_CPLT, lang))
            else: but.setText(s)       
        applyStyles()

    def keyPressEvent(self, event):
        if event.text() in ('z', '.'):
            i = self.stack.currentIndex()
            self.voltamograms[i].toggle_endpoint()
        
    def save_and_close(self):
        # 0. Check if this messes up any existing calculations
        continue_action, calcs_to_archive = check_calc_conflict(self.parent.data, self.tasks)
        if not continue_action:
            return
        
        # 1. slide analyzed data into parent data
        to_write = []
        for i, task in enumerate(self.tasks):       # for each rep analyzed
            rep = get_rep(self.parent.data, task)   # get the data pre-analysis
            rep[g.R_ANALYSIS] = self.results[i]     # slot in the analysis
            to_write.append(rep)   

        # 2. run async save
        lang = self.settings[g.SET_LANG]
        self.status.showMessage(get_text(l.SB_SAVE_STRT, lang))

        cb_suc = self.save_success          # callback on success of final async save
        cb_err = self.save_error            # callback on error of any async save

        cb_calc = partial(self.parent.start_async_save, g.SAVE_TYPE_CALCS_ARCHIVE, [True, calcs_to_archive], cb_suc, cb_err)     # Callback to archive calcs after analysis is saved
        self.parent.start_async_save(g.SAVE_TYPE_REP_MOD, [self.tasks, to_write], onSuccess=cb_calc, onError=cb_err)
            

    def save_success(self, event=False):
        lang = self.settings[g.SET_LANG]
        self.status.showMessage(get_text(l.SB_SAVE_GOOD, lang))
        self.saved = True
        self.close()

    def save_error(self, event=False):
        lang = self.settings[g.SET_LANG]
        self.status.showMessage(get_text(l.SB_SAVE_ERRR, lang), g.SB_DURATION)
        
            
    def set_text(self, lang):
        self.update_settings()
        
        self.setWindowTitle(self.parent.data[g.S_NAME]+' | '+get_text(l.ANA_HEAD, lang))
        for i, title in enumerate(self.titles):             # for each rep
            run, rep = self.tasks[i]
            run_n = get_run_num(run)
            rep_n = get_rep_num(rep)
            run_s = get_text(l.ANA_RUN_ABRV, lang)+run_n
            rep_s = get_text(l.ANA_REP_ABRV, lang)+rep_n
            txt(title, s='<b>'+run_s+'  |  '+rep_s+'</b>')  # Set title 
            self.voltamograms[i].set_text(lang)             # Set voltamogram text
            
        i = self.stack.currentIndex()
        self.update_buttons(i)                              # Updates text on next/save button
        self.refresh_progress(i)                            # Updates text on sidebar task buttons
        
        txt(self.prog_lbl, '<b>'+get_text(l.ANA_TITL, lang)+'</b>')
        txt(self.helptext, l.ANA_HELP, lang)
        txt(self.but_results, l.ANA_RLTS, lang)
        
    def update_settings(self):
        self.settings = self.parent.parent.settings












    def update_win(self):
        return
        # update window widgets here
    
    def event(self, event):                                 # General purpose event handler
        if event.type() == QEvent.Type.ActivationChange:    # Check if the event is changing the activation status of the window
            if self.isActiveWindow():                       #   Check whether the event *activated* the window
                main = self.parent
                welcome = main.parent
                if not fileOkRoutine(welcome, main, self):      # Run routine to check if file is okay
                    return True
        return QMainWindow.event(self, event)               # Forward all events to appropriate QMainWindow event handler
        
    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.set_enabled_children(False)
        self.setEnabled(True)
        event.accept()      
    
    def closeEvent(self, event):
        """Event handler for close event."""
        if self.force_close:
            self.accept_close(event)
        elif not self.saved:
            lang = self.settings[g.SET_LANG]
            confirm = saveMessageBox(lang)
            resp = confirm.exec()
            if resp == QMessageBox.StandardButton.Save:
                event.ignore()
                if len(self.tasks) == 1: self.store_results()   # store data for the current one if only one
                self.save_and_close()
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
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        if self in self.parent.children:
            self.parent.children.remove(self)
        closeEvent.accept()
        

