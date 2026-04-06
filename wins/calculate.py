
"""
calculate.py

A window that allows the user to use analyzed data, collected with
the potentiostat, to back-calculate the concentration of the
species of interest in the original sample.
"""
from external.globals import ov_globals as g
from external.globals.ov_functions import *

from embeds.stdAddFitter import StdAddFitterPlot

from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QComboBox,
    QTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,    
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QAbstractItemView,
    QProgressBar,
    QInputDialog,
    QSplitter
)

class WindowCalculate(QMainWindow):
    def __init__(self, parent, mode, calc_id=None, suggestion=None):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.calc_id = calc_id
        self.suggestion = suggestion
        self.mode_prev = None

        self.reset_globals()

        # Status Bar and Progress Bar
        self.status = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMaximumWidth(g.SB_PROGRESS_BAR_WIDTH)  # Set a fixed width
        self.progress_bar.setVisible(False)     # Hide it initially
        self.status.addPermanentWidget(self.progress_bar)

        # Set the layout programatically
        self.adjust_suggestion()
        self.set_layout()
        
    def reset_globals(self):
        self.method = None
        self.points = [[],[],[]]
        self.stdadd_selectors = []
        self.saved = True
        self.updating_runs = False
        self.on_save_mode = None
        self.on_save_calc = None
        
        self.to_preset = False
        if self.mode in (g.WIN_MODE_EDIT, g.WIN_MODE_VIEW_ONLY) and self.calc_id:
            self.to_preset = True

        # Selector border widths and colors
        self.border_width_active = '5px'
        self.border_width_passive = '1px'
        self.border_color_good = 'green'
        self.border_color_todo = 'orange'
        self.border_color_error = 'red'
        if self.mode == g.WIN_MODE_VIEW_ONLY:
            self.border_color_good = 'grey'
            self.border_color_todo = 'grey'
            self.border_color_error = 'grey'

    def get_right_layout(self):
        title = QLabel("<b>Results</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.calc_list = QListWidget()
        self.calc_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.calc_list.setAlternatingRowColors(True)
        self.calc_list.setSpacing(2)
        self.calc_list.itemSelectionChanged.connect(self.update_right_buttons)
        self.calc_list.itemDoubleClicked.connect(self.view_calc)
        
        b_new = QPushButton()
        b_edit = QPushButton()
        b_dup = QPushButton()
        b_del = QPushButton()

        b_new.setIcon(QIcon(g.ICON_PLUS))
        b_edit.setIcon(QIcon(g.ICON_EDIT))
        b_dup.setIcon(QIcon(g.ICON_DUP))
        b_del.setIcon(QIcon(g.ICON_TRASH))

        b_new.clicked.connect(partial(self.go_to_mode, g.WIN_MODE_NEW))
        b_edit.clicked.connect(self.edit_from_right)
        b_dup.clicked.connect(self.duplicate)
        b_del.clicked.connect(self.delete)

        b_new.setToolTip('New')
        b_edit.setToolTip('Edit')
        b_dup.setToolTip('Duplicate')
        b_del.setToolTip('Delete')

        self.right_buttons_one_only = [b_edit]
        self.right_buttons_one_plus = [b_dup, b_del]

        lbl = QLabel("<i>double-click a <b>result</b> to view calculation details.</i>")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        h2 = QHBoxLayout()
        for b in (b_new, b_edit, b_dup, b_del):
            h2.addWidget(b)
        
        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(self.calc_list)
        v.addLayout(h2)
        v.addWidget(lbl)

        self.update_calc_list()
        self.update_right_buttons()
        return v

    def update_calc_list(self):
        self.calc_list.clear()
        for calc in self.parent.data[g.S_PROCESSED]:
            
            # get unique runs in calc
            runs = []
            for point in calc[g.C_POINTS]:
                for rep in point:
                    run_id = rep[g.C_RUN_ID]
                    if not run_id in runs:
                        runs.append(run_id)
                        
            # Set text for the list label
            runtxt = ''
            for run in runs:
                runtxt = runtxt + str(run) + ' | '
            runtxt = runtxt[0:-3]                   # remove the pipe from the last entry
            txt = calc[g.R_UID_SELF] + ' ('+calc[g.C_TYPE] +', '+calc[g.C_REG_TYPE]+')\n'
            if calc[g.C_ARCHIVED]: txt = '[ARCHIVED] '+txt
            txt = txt + runtxt + '\n'
            txt = txt + 'Result: '+str(round(calc[g.C_CONC_ORIGINAL],8))+' +/- STD_DEV mg/L'
            if calc[g.C_NOTE]:
                txt = txt + '\nNote: '+str(calc[g.C_NOTE])
            
            # Create the list element and attach it to the list
            calcitem = QListWidgetItem(self.calc_list)
            calcitem.setText(txt)
            calcitem.setData(Qt.ItemDataRole.UserRole, calc)

    #################################
    #                               #
    #   MODE CHANGING FUNCTIONS     #
    #                               #
    #   1. view_calc                #
    #   2. edit_from_right          #
    #   3. go_to_mode               #
    #   4. continue_action          #
    #                               #
    #################################

    def view_calc(self, item):
        calc_id = item.data(Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
        self.go_to_mode(g.WIN_MODE_VIEW_ONLY, calc_id)

    def edit_from_right(self):
        item = self.calc_list.currentItem()
        calc_id = item.data(Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
        calc = self.get_calc_from_id(calc_id)
        if calc[g.C_ARCHIVED]:
            show_alert(self, 'Alert!', 'Archived calculations cannot be edited. To modify this calculation, duplicate it then edit the resulting copy.')
            return
        self.go_to_mode(g.WIN_MODE_EDIT, calc_id)

    def go_to_mode(self, mode_new, calc_id=None):
        """General function for changing to a different window mode. Takes in a
        new mode and an option Id of a calculation (required to go to VIEW or EDIT
        modes but not for NEW or RIGHT modes. Checks to make sure no data will be
        lost if mode is changed (and promps user to save, discard, or cancel if work
        will be lost, then changes the mode."""

        if not self.continue_action(mode_new, calc_id):
            return
        
        # Change the mode    
        self.calc_id = calc_id
        self.mode_prev = self.mode
        self.mode = mode_new
        self.suggestion = None
        self.set_layout()

    def continue_action(self, mode_new, calc_id):
        """Takes in the new mode that the user wants to go to and the id of the calc that
        they want to go to, if applicable.

        ALGORITHM
        It checks whether there is any unsaved progress.
        If so, asks the user whether to save, discard or cancel. If the user selecs "Save",
        the next mode and calc are stored, a save is begun and False is returned (because
        the action will occur once the async save is complete). If the user selects "Discard",
        True is returned, to indicate that whatever mode change was selected should continue.
        If the user selected "Cancel" False is returned.
        If there is no unsaved progress, returns True so that the user-selected change can
        continue as requested."""
        
        if not self.saved:
            resp = saveMessageBox().exec()
            if resp == QMessageBox.StandardButton.Save:         # if the user selects save
                self.on_save_mode = mode_new                    # tell saver what to do
                self.on_save_calc = calc_id                     # after save
                self.save()                                     # and start the save!
                return False
            elif resp == QMessageBox.StandardButton.Discard:    # if the user selects discard
                return True                                     # fall through to changing mode
            else:                                               # if the user selects cancel
                return False                                    # do nothing!
        return True
        
        

    def update_right_buttons(self):
        n = len(self.calc_list.selectedItems())
        if n == 0:
            enable = []
            freeze = self.right_buttons_one_only + self.right_buttons_one_plus
        elif n == 1:
            enable = self.right_buttons_one_only + self.right_buttons_one_plus
            freeze = []
        else:
            enable = self.right_buttons_one_plus
            freeze = self.right_buttons_one_only
            
        for but in enable:
            but.setEnabled(True)
        for but in freeze:
            but.setEnabled(False)

    def get_left_layout(self):
        # header bar
        txt = 'New calculation'
        if self.mode in (g.WIN_MODE_EDIT, g.WIN_MODE_VIEW_ONLY):
            txt = self.calc_id
            calc = self.get_calc_from_id(self.calc_id)
            if calc[g.C_ARCHIVED]:
                txt = '[ARCHIVED] '+txt
        title = QLabel(txt)
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setObjectName('left-title')
            
        but_close = QPushButton()
        but_close.setIcon(QIcon(g.ICON_X))
        but_close.clicked.connect(partial(self.go_to_mode, g.WIN_MODE_RIGHT))
        
        h0 = QHBoxLayout()
        h0.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        h0.addStretch()
        h0.addWidget(title)
        h0.addStretch()
        h0.addWidget(but_close)
        
        # far left column
        type_lbl = QLabel("Calculation type")
        self.type = QComboBox()
        self.type.setPlaceholderText('Select')
        calc_types = ('Peak height / baseline', 'Peak height', 'Left slope', 'Right slope', 'Mean slope')
        for i, calc_type in enumerate(calc_types):
            self.type.addItem(calc_type, userData=g.C_TYPES[i])
        self.type.currentIndexChanged.connect(self.type_changed)

        reg_type_lbl = QLabel("Fit regression to")
        self.reg_type = QComboBox()
        reg_types = ('All points', 'Means')
        for i, reg_type in enumerate(reg_types):
            self.reg_type.addItem(reg_type, userData=g.C_REG_TYPES[i])
        self.reg_type.currentIndexChanged.connect(self.reg_type_changed)
        
        notes_lbl = QLabel("Notes")
        self.notes = QTextEdit()
        self.notes.textChanged.connect(self.something_has_been_updated)

        but_graph = QPushButton('Graph selected')
        but_graph.clicked.connect(self.graph_selected)

        self.results_stack = QStackedLayout()
        w1 = QPushButton('Show results')
        w1.clicked.connect(self.get_and_show_results)
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results_stack.addWidget(w1)
        self.results_stack.addWidget(self.results)

        v0 = QVBoxLayout()
        v0.addWidget(type_lbl)
        v0.addWidget(self.type)
        v0.addWidget(reg_type_lbl)
        v0.addWidget(self.reg_type)
        v0.addWidget(notes_lbl)
        v0.addWidget(self.notes)
        v0.addStretch()
        v0.addWidget(but_graph)
        v0.addLayout(self.results_stack)

        # center column        
        self.graph = StdAddFitterPlot(self)#, 'Best-fit calculator') 

        
        h1 = QHBoxLayout()                            # row of selectors
        try:
            l0 = self.get_sample_selector_layout()
        except Exception as e:
            print(e)
        h1.addLayout(l0)
        for i, point in enumerate(self.points):
            if i>0:
                l = self.get_stdadd_selector_layout(i)
                h1.addLayout(l)

        w2 = QWidget()
        w2.setLayout(h1)

        '''but_add_point = QPushButton('+')
        h1.addWidget(but_add_point)'''

        qs = QSplitter()
        qs.setChildrenCollapsible(False)
        qs.setOrientation(Qt.Orientation.Vertical)
        qs.addWidget(self.graph)
        qs.addWidget(w2)

        h2 = QHBoxLayout()
        h2.addLayout(v0)
        h2.addWidget(QVLine())
        h2.addWidget(qs)

        but_save = QPushButton('save')
        but_edit = QPushButton('edit')
        archived_txt = QLabel('Archived calculations cannot be edited. To modify this calculation, duplicate it then edit the resulting copy.')
        
        but_save.clicked.connect(self.save)
        but_edit.clicked.connect(partial(self.go_to_mode, g.WIN_MODE_EDIT, self.calc_id))

        v2 = QVBoxLayout()
        v2.addLayout(h0)
        v2.addWidget(QHLine())
        v2.addLayout(h2)

        if self.mode == g.WIN_MODE_VIEW_ONLY:
            calc = self.get_calc_from_id(self.calc_id)
            if calc[g.C_ARCHIVED]:
                v2.addWidget(archived_txt)
            else:
                v2.addWidget(but_edit)
        else:
            v2.addWidget(but_save)

        if self.mode == g.WIN_MODE_VIEW_ONLY:                       # if view only, make a bunch of elements view_only
            self.type.setEnabled(False)
            self.reg_type.setEnabled(False)
            self.notes.setEnabled(False)
            self.graph.set_view_only()

        self.update_reg_type_on_graph()     # make sure graph has correct starting regression type 
            
        return v2

    def get_run_tree_widget(self, with_method=False):
        tree = QTreeWidget()
        if with_method:
            tree.setColumnCount(2)
            tree.setHeaderLabels(('Run', 'Method', 'Note'))
        else:
            tree.setColumnCount(1)
            tree.setHeaderLabels(('Run','Note'))
        tree.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        tree.setAlternatingRowColors(True)
        self.set_widget_border(tree, self.border_width_active, self.border_color_todo)
        return tree

    def set_widget_border(self, w, width, color):
        """Takes in a widget, and a border width and color, as strings.
        width must contain units, eg. "5px" is okay but 5 or "5" is not.
        color can be any format accepted by QSS"""
        w_type = w.__class__.__name__   
        w.setStyleSheet(w_type+"{border: "+width+" solid "+color+";}")
        

    def get_sample_selector_layout(self):
        title_str = 'Sample'
        t1 = QLabel(title_str)
        t2 = QLabel(title_str)
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sample_tree = self.get_run_tree_widget(with_method = True)
        self.sample_tree.itemSelectionChanged.connect(partial(self.update_sample_runs, self.sample_tree, 0))

        self.updating_runs = True
        self.load_sample_runs(self.sample_tree)
        self.updating_runs = False

        v1 = QVBoxLayout()
        v1.addWidget(t1)
        v1.addWidget(self.sample_tree)
        w1 = QWidget()
        w1.setLayout(v1)

        self.sample_txt = QTextEdit()
        self.sample_txt.setEnabled(False)

        v2 = QVBoxLayout()
        v2.addWidget(t2)
        v2.addWidget(self.sample_txt)
        w2 = QWidget()
        w2.setLayout(v2)
    
        self.sample_stack = QStackedLayout()
        self.sample_stack.addWidget(QWidget()) # Placeholder widget          
        self.sample_stack.addWidget(w1)
        self.sample_stack.addWidget(w2)

        
        if self.mode == g.WIN_MODE_VIEW_ONLY:
            self.sample_stack.setCurrentIndex(g.C_STACK_VIEW_TEXT)
        else:
            self.sample_stack.setCurrentIndex(g.C_STACK_INDEX_SELECTOR)
       
        return self.sample_stack
    
    def get_stdadd_selector_layout(self, i):
        title_str = 'Standard addition '+str(i)
        t1 = QLabel(title_str)
        t2 = QLabel(title_str)
        t3 = QLabel(title_str)
        t4 = QLabel(title_str)
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if i == 1: msg = "Please select at least one <b>sample</b> run  <-----"
        else: msg = "Please select at least one run for <b>standard addition "+str(i-1)+'</b>   \n\n<-----'
        
        s = QStackedLayout()
        box1 = QTextEdit(msg)
        box1.setEnabled(False)
        self.set_widget_border(box1, self.border_width_passive, self.border_color_todo)
        v1 = QVBoxLayout()
        v1.addWidget(t1)
        v1.addWidget(box1)
        v1.addStretch()
        w1 = QWidget()
        w1.setLayout(v1)

        tree = self.get_run_tree_widget(with_method = False)
        tree.itemSelectionChanged.connect(partial(self.update_stdadd_runs, i-1))
        v2 = QVBoxLayout()
        v2.addWidget(t2)
        v2.addWidget(tree)
        w2 = QWidget()
        w2.setLayout(v2)

        txt3 = QTextEdit()
        txt3.setEnabled(False)
        v3 = QVBoxLayout()
        v3.addWidget(t3)
        v3.addWidget(txt3)
        w3 = QWidget()
        w3.setLayout(v3)

        box4 = QTextEdit('There are no available standard additions with the selected method')
        box4.setEnabled(False)
        self.set_widget_border(box4, self.border_width_active, self.border_color_error)
        v4 = QVBoxLayout()
        v4.addWidget(t4)
        v4.addWidget(box4)
        v4.addStretch()
        w4 = QWidget()
        w4.setLayout(v4)
        
        for w in (w1,w2,w3,w3):
            s.addWidget(w)

        self.stdadd_selectors.append({'tree': tree,
                                      'layout': s,
                                      'txt': txt3})

        s.setCurrentIndex(g.C_STACK_INDEX_BASE)
        if self.mode == g.WIN_MODE_VIEW_ONLY:
            print('view only!')
            s.setCurrentIndex(g.C_STACK_VIEW_TEXT)

        return s
        

    def get_full_layout(self):
        right = self.get_right_layout()
        if self.mode == g.WIN_MODE_RIGHT:
            lay = right
        else:
            left = self.get_left_layout()
            lay = QHBoxLayout()
            lay.addLayout(left)
            lay.addWidget(QVLine())
            lay.addLayout(right)
        return lay

    def adjust_suggestion(self):
        """Considers the suggested reps that were passed to the calculator. Follows this algorithm:
        1. If empty, returns
        2. If there is at least one sample rep, returns
        3. If there are standard addition reps, goes to first one and grabs first sample run
            from data, including all reps, appends to suggestion."""
        print('here we are adjusting the suggestion!')
        if not self.suggestion:
            return
        samples = []
        stdadds = []
        for suggestion in self.suggestion:
            run_id = suggestion[0]
            run = get_run_from_file_data(self.parent.data, run_id)
            if run[g.R_TYPE] == g.R_TYPE_SAMPLE: samples.append(run)
            elif run[g.R_TYPE] == g.R_TYPE_STDADD: stdadds.append(run)

        if samples:
            return

        if stdadds:
            replist = []
            for stdadd in stdadds:
                sample_found = False
                method = stdadd[g.R_UID_METHOD]
                for run in self.parent.data[g.S_RUNS]:
                    if run[g.R_UID_METHOD] == method:
                        replist = get_all_reps_from_run_id(self.parent.data, run[g.R_UID_SELF])
                        sample_found = True
                        break
                if sample_found: break
            for rep in replist:
                self.suggestion.append(rep)
            print(self.suggestion)
                
                        

    def set_layout(self):
        self.reset_globals()            # Reset the globals

        l = self.get_full_layout()      # Get the layout
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)        # Set it! 

        # Set the window title
        txt = 'Results'
        if self.mode == g.WIN_MODE_NEW: txt = 'New calculation'
        elif self.mode == g.WIN_MODE_EDIT: txt = 'Edit calculation'
        elif self.mode == g.WIN_MODE_VIEW_ONLY: txt = 'View calculation'
        self.setWindowTitle(self.parent.data[g.S_NAME]+' | '+txt)

        # Adjust window size and position now that its been reset
        if self.mode == g.WIN_MODE_RIGHT:   # if going to Right pane only, shrink and place window
            self.showNormal()               # un-maximize
            screen = g.APP.primaryScreen().availableGeometry()  # resize to smaller column
            self.resize(self.centralWidget().layout().sizeHint().width(), screen.height()-100)
            x = screen.width() - self.geometry().width() - 20       # get desired x position of upper left
            y = screen.height() - self.geometry().height() - 70     # get desired y position of upper left
            self.move(x,y)
        elif not self.mode_prev or self.mode_prev == g.WIN_MODE_RIGHT:
            self.showMaximized()

        # Fill in the actual values to the form
        try:
            self.preset_runs()
            self.set_values()
            self.set_selector_indices()
            self.to_preset = False      # Once we have finished presetting, we are no longer presetting
            self.suggestion = None      # Once we have finished suggesting, we are no longer suggesting
            self.saved = True           # Right when we have finished presetting and suggesting, we have nothing to save
            #self.updating_runs = False  # And we are no longer updating runs
        except Exception as e:
            print('here i am being an error!')
            print(e)

    def set_values(self):
        if not self.mode in (g.WIN_MODE_EDIT, g.WIN_MODE_VIEW_ONLY):
            return
        calc = self.get_calc_from_id(self.calc_id)                  # get calc data
        type_index = g.C_TYPES.index(calc[g.C_TYPE])
        reg_type_index = g.C_REG_TYPES.index(calc[g.C_REG_TYPE])
        txt = calc[g.C_NOTE]
        self.type.setCurrentIndex(type_index)
        self.reg_type.setCurrentIndex(reg_type_index)
        self.notes.setPlainText(txt)
        if self.mode == g.WIN_MODE_VIEW_ONLY:
            self.set_view_only_points(calc)
            if calc[g.C_ARCHIVED]:
                self.graph.update_archived(calc)
                
        

    def set_selector_indices(self):
        if self.mode == g.WIN_MODE_VIEW_ONLY:
            for i in range(0, len(self.points)):
                if i==0: stack = self.sample_stack
                else: stack = self.stdadd_selectors[i-1]['layout']
                stack.setCurrentIndex(g.C_STACK_VIEW_TEXT)

    def set_view_only_points(self, calc): 
        for i, pt in enumerate(calc[g.C_POINTS]):
            
            if i==0: txt = self.sample_txt
            else: txt = self.stdadd_selectors[i-1]['txt']
            lines = []
            runs = []
            for j,row in enumerate(pt):
                run_id = row[g.C_RUN_ID]
                rep_id = row[g.C_REP_ID]
                if run_id not in runs:
                    if lines:
                        lines[-1] = lines[-1][0:-2] + ')\n'
                    lines.append(run_id+' (')
                    runs.append(run_id)
                lines[-1] = lines[-1] + rep_id + ', '
            lines[-1] = lines[-1][0:-2] + ')\n'
            to_write = ''
            for line in lines:
                to_write = to_write + line
            txt.setPlainText(to_write)    
                    
    def duplicate(self):
        """Duplicates all selected calculations"""
        items = self.calc_list.selectedItems()
        data = []
        
        for item in items:
            datum = item.data(Qt.ItemDataRole.UserRole)
            data.append(datum)
            
        ids = get_ids(self.parent.data, g.S_PROCESSED)
        for datum in data:  
            note = datum[g.C_NOTE]                          # Add [COPY OF calc-id] to new calc's note
            lbl = '[COPY OF '+str(datum[g.R_UID_SELF])+']'
            if note: datum[g.C_NOTE] =  lbl+' '+note
            else: datum[g.C_NOTE] = lbl
            datum[g.C_ARCHIVED] = False                     # Whether or not original was archived, new one will not be, even if incomplete.
            calc_id = get_next_id(ids, g.C_UID_PREFIX)      # Get the next calc-id UID
            datum[g.R_UID_SELF] = calc_id
            ids.append(calc_id)                             # to get next UID for next looop

        self.progress_bar.setVisible(True)
        self.parent.start_async_save(g.SAVE_TYPE_CALC_NEW, [data], onSuccess=self.async_success, onError=self.async_error)

        
    def delete(self):
        """Deletes selected calcs"""
        items = self.calc_list.selectedItems()
        tasks = []
        for item in items:
            data = item.data(Qt.ItemDataRole.UserRole)
            tasks.append(data[g.R_UID_SELF])

        if self.mode==g.WIN_MODE_EDIT and self.calc_id in tasks:    # Do not delete if currently edited calc is selected
            show_alert(self, "Alert!", "Cannot delete the calculation that is currently being edited ("+str(self.calc_id)+").\nPlease make a different selection and try again.")
            return
            
        if self.confirm_delete():                                   # Confirm delete w user
            self.progress_bar.setVisible(True)
            self.parent.start_async_save(g.SAVE_TYPE_CALC_DELETE, [tasks], onSuccess=self.async_success, onError=self.async_error)

        
    def confirm_delete(self):
        title = 'Confirm delete'
        text = 'This will permanently delete all selected calculations.\n\nIf you are sure you want to delete, type DELETE below.'
        text, ok = QInputDialog.getText(self, title, text)
        if ok:
            if text == 'DELETE':
                return True
        return False

    def async_success(self):
        self.progress_bar.setVisible(False)
        self.status.showMessage("Complete", g.SB_DURATION)
        
        

    def load_sample_runs(self, run_list):
        # Get "sample" runs
        
        # If any elements in run list, remove them all
        self.remove_all(run_list)
                    
        # Add back in all runs with type == sample
        for run in self.parent.data[g.S_RUNS]:          
            if run[g.R_TYPE] == g.R_TYPE_SAMPLE:
                method = get_method_from_file_data(self.parent.data, run[g.R_UID_METHOD])
                self.add_run_to_tree(run_list, run, method=method)

    def preset_runs(self):
        if self.to_preset:      # preset from calc with id calc_id
            calc = self.get_calc_from_id(self.calc_id)                  # get calc data
            points = calc[g.C_POINTS]
            for i, point in enumerate(points):
                if i==0: tree = self.sample_tree
                else: tree = self.stdadd_selectors[i-1]['tree']

                run_ids = self.get_runs_from_point(point)                   # get sample run ids
                for run_id in run_ids:                                      # for each run id
                    for j in range(0, tree.topLevelItemCount()):            # loop thru all items in tree
                        item = tree.topLevelItem(j)
                        item_run_id = item.data(0,Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
                        if item_run_id == run_id:                           # if the item run_id matches the sample run_id
                            item.setSelected(True)                          # select it! 
                            break                                           # and break, because selecting it will modify the tree we're looping thru

        elif self.suggestion:                                               # if the user has selected some runs/reps to seed the calculation
            for i, point in enumerate(self.points):                         # loop thru all points
                if i==0: tree = self.sample_tree                            
                else: tree = self.stdadd_selectors[i-1]['tree']
                runs = []
                any_added = False
                for (run_id, rep_id) in self.suggestion:                    # loop thru all the suggested reps
                    if any_added and not i in (0, len(self.points)-1):      #   if points have already been added for this selector (all selectors but sample and last std_add)
                        break
                    if not run_id in runs:                                  #   if we haven't yet checked this run
                        runs.append(run_id)                                 #       append to runs to indicate we're checking it now
                        for j in range(0, tree.topLevelItemCount()):        #       loop thru all items in tree
                            item = tree.topLevelItem(j)                     
                            item_run_id = item.data(0,Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
                            if item_run_id == run_id:                       #       if the run on the tree matches the suggested run
                                any_added = True                            #       we've selected one!
                                item.setSelected(True)                      #       select it
                                break                                       #       and break because selecting it will modify the tree we're looping thru
                            
                        
    def get_calc_from_id(self, calc_id):
        for calc in self.parent.data[g.S_PROCESSED]:
            if calc[g.R_UID_SELF] == calc_id:
                return calc
        return None

    def get_runs_from_point(self, point):
        """Takes an a list, point, of dicts and returns a list of the unique run ids"""
        runs = []
        for rep in point:
            run_id = rep[g.C_RUN_ID]
            if not run_id in runs:
                runs.append(run_id)
        return runs
        
    def get_tasks_from_point(self, point):
        """Takes ins a list, point, of dicts and returns of list of tuples of the form:
        [(runID1, repID), (runID, repID), ... , (runID, repID)]"""
        tasks = []
        for rep in point:
            run_id = rep[g.C_RUN_ID]
            rep_id = rep[g.C_REP_ID]
            tasks.append((run_id, rep_id))
        return tasks

    def load_stdadd_runs(self, i):
        
        # If any elements in run list, remove them all
        tree = self.stdadd_selectors[i]['tree']
        self.remove_all(tree)        

        # Add back in all runs with type == stdadd and method matching self.method
        

        selected_runs = self.get_all_selected_runs()
                
        runs_added = 0                                          
        for run in self.parent.data[g.S_RUNS]:                  # Add run to this stdadd selector IF:   
            if run[g.R_TYPE] == g.R_TYPE_STDADD:                #   - It is a standard addition type run
                if run[g.R_UID_METHOD] == self.method:          #   - It's method matches the selected sample method
                    if not run[g.R_UID_SELF] in selected_runs:  #   - It's not selected in any other standard addition selector
                        self.add_run_to_tree(tree, run)
                        runs_added = runs_added + 1

        if runs_added == 0:
            self.stdadd_selectors[i]['layout'].setCurrentIndex(g.C_STACK_INDEX_ERROR)
            
    

        
    def update_sample_runs(self, run_list, selector_index):
        if self.updating_runs:
            return
        self.updating_runs = True
        try:
            selected_runs = self.get_selected_runs(run_list)
            
            if selected_runs:
                # grab method of first selected run (in case multiple selected simultaneously
                self.method = selected_runs[0].data(0, Qt.ItemDataRole.UserRole)[g.R_UID_METHOD]

                # loop backwards thru runs. If run doesn't match selected method, take it from list
                all_items = [run_list.topLevelItem(x) for x in range(run_list.topLevelItemCount())]
                for i,item in reversed(list(enumerate(all_items))):
                    if item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_METHOD] != self.method:
                        run_list.takeTopLevelItem(i)
                
                # for each selected run, show all reps and select them, for deselected runs, remove children
                self.show_reps_from_runs(run_list, 0)
                
            # Check if any runs are selected anymore.                 
            selected_runs = self.get_selected_runs(run_list)
            if not selected_runs:                   # if not
                self.method = None                  # reset method
                self.load_sample_runs(run_list)
                self.set_widget_border(run_list, self.border_width_active, self.border_color_todo)
            # Update next pane based on status of this pane
            self.update_points(selector_index, run_list)
            self.graph.update_points(self.points)
            self.update_selectors()
            self.updating_runs = False
        except Exception as e:
            print('error is HERE!')
            print(e)

    def update_stdadd_runs(self, i):
        try:
            print('current, self.updating_runs is: '+str(self.updating_runs))
            if self.updating_runs: return               # to avoid recursion
            self.updating_runs = True                   # stops recursive calls during this fn
            print('here we are in the single update!')
            print('self.suggestion is:')
            print(self.suggestion)
            print()
            tree = self.stdadd_selectors[i]['tree']
            selected_runs = self.get_selected_runs(tree)
            if selected_runs:
                               # if we're about to do some auto-updating, avoid recursion
                self.show_reps_from_runs(tree, i+1)
                

            # Check if any runs are selected anymore.                 
            selected_runs = self.get_selected_runs(tree)
            if not selected_runs:               # if not
                self.load_stdadd_runs(i)        # reset sample pane
                self.set_widget_border(tree, self.border_width_active, self.border_color_todo)

            self.update_points(i+1, tree)
            
            self.graph.update_points(self.points)
            self.update_selectors()

            
            # hide all selected stdadd runs from all other selectors 
            used_runs = self.get_all_selected_runs()
            
            for selector in self.stdadd_selectors:
                if selector['layout'].currentIndex() == g.C_STACK_INDEX_SELECTOR:               # If selector is showing
                    tree = selector['tree']
                    all_items = [tree.topLevelItem(x) for x in range(tree.topLevelItemCount())]
                    for item in all_items:                                                      # Loop thru all runs in selector (hidden and not)
                        if not item.isSelected():                                               # If run is selected, leave it alone
                            run_id = item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]       
                            if run_id in used_runs:                                             # If run is selected elsewhere
                                item.setHidden(True)                                            #   hide it
                            if item.isHidden():                                                 # If run is hidden here
                                if not run_id in used_runs:                                     #   check if it can be redisplayed. If not used elsewhere,
                                    item.setHidden(False)                                       #   unhide it!
                    
            self.updating_runs = False              # ok, good job!

        except Exception as e:
            print('im really the ERROR:')
            print(e)
        
    def update_points(self, i, tree):
        self.something_has_been_updated()
        self.results_stack.setCurrentIndex(0)
        self.points[i] = self.get_tasks_from_tree(tree, include_data=True)
        erase = False
        for i,point in enumerate(self.points):
            if not erase:           # find first point with no entries
                if not point:   
                    erase = True
            else:                   # erase data in all higher points
                self.points[i] = []

    def show_reps_from_runs(self, tree, point_index):
        all_items = [tree.topLevelItem(x) for x in range(tree.topLevelItemCount())]
        for item in all_items:
            if item.isSelected() and item.childCount() == 0:        # If item is newly selected, show all children and select!
                for rep in item.data(0, Qt.ItemDataRole.UserRole)[g.R_REPLICATES]:
                    subitem = QTreeWidgetItem(item)
                    subitem.setData(0, Qt.ItemDataRole.UserRole, rep)
                    subitem.setText(0, rep[g.R_UID_SELF])
                    subitem.setText(2, rep[g.R_NOTES])
                    if not rep[g.R_ANALYSIS]:
                        subitem.setDisabled(True)
                        for col in range(0, tree.columnCount()):
                            subitem.setToolTip(col, "Please analyze to proceed")
                    else: subitem.setSelected(True)
                    self.set_widget_border(tree, self.border_width_active, self.border_color_good)
                item.setExpanded(True)
            elif not item.isSelected() and (item.childCount() != 0):  # If item is no longer selected, hide all children!
                item.takeChildren()
            elif item.isSelected() and item.childCount() != 0:         # If item is selected and already has children, check
                selected_children = False                           #   whether they should be hidden
                for i in range(0,item.childCount()):
                    if item.child(i).isSelected():
                        selected_children=True
                        break
                if not selected_children:       # If all children have been deselected by user
                    item.takeChildren()         # Remove them all from the layout
                    item.setSelected(False)     # And deselect the run itself
                    
        # if we're supposed to be preselecting certain runs (either preset or suggestion)
        preset_flag = False
        if self.to_preset:
            calc = self.get_calc_from_id(self.calc_id)                                      # get data for calc that we're presetting
            tasks = self.get_tasks_from_point(calc[g.C_POINTS][point_index])                # get list of tasks of format [(runID, repID),...]
            preset_flag = True
        elif self.suggestion:
            tasks = self.suggestion
            preset_flag = True

        if preset_flag:
            for item in tree.selectedItems():                                               #   that *should* be the only ones selected
                if not item.childCount():                                                   # loop thru all child items on tree
                    run_id = item.parent().data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]  #   get run and rep IDs of element
                    rep_id = item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
                    if not (run_id, rep_id) in tasks:                                       #   if the selected rep shouldn't be selected
                        item.setSelected(False)                                             #       deselect it!
            

                    

    def update_selectors(self):
        self.updating_runs = True
        if not self.points[0]:
            for i, selector in enumerate(self.stdadd_selectors):
                selector['layout'].setCurrentIndex(g.C_STACK_INDEX_BASE)
                self.points[i+1] = []
        else:
            # Get i, the index of the first selector w no selected points
            empty = False
            for i,point in enumerate(self.points):
                if not point:                           
                    empty = True
                    break
            if empty:                   # if there is a selector w no selected points
                # show selector[i]
                i = i-1                 # adjust index to index from 0.
                # wipe points for all selectors with index >i
                for j in range(i+1,len(self.points)):
                    self.points[j] = []
                    self.set_widget_border(self.stdadd_selectors[j-1]['tree'], self.border_width_active, self.border_color_todo)

                # show the ith selector
                self.stdadd_selectors[i]['layout'].setCurrentIndex(g.C_STACK_INDEX_SELECTOR)
                # hide all selectors[j] for j>i
                for j, selector in enumerate(self.stdadd_selectors):
                    if j>i: selector['layout'].setCurrentIndex(g.C_STACK_INDEX_BASE)
                # for all stdadds w index between 0 and j
                #   erase tree
                #   add all stdadd runs to tree that are either in points[j+1] or not in points at all.
                self.load_stdadd_runs(i)
                self.update_stdadd_runs(i)
        self.updating_runs = False

    def get_selected(self, tree):
        return tree.selectedItems()

    def get_selected_runs(self, tree):
        selected_items = self.get_selected(tree)
        selected_runs = [item for item in selected_items if g.R_RUN_UID_PREFIX
                         in item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]]
        return selected_runs

    def get_all_selected_runs(self):
        selected_runs = []
        for selector in self.points:
            for point in selector:
                selected_runs.append(point[0])
        return list(set(selected_runs))


    def get_selected_reps(self, tree):
        selected_items = self.get_selected(tree)
        selected_reps = [item for item in selected_items if g.R_REPLICATE_UID_PREFIX
                         in item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]]
        return selected_reps

    def get_tasks_from_tree(self, tree, include_data=False):
        reps = self.get_selected_reps(tree)
        tasks = []
        for rep in reps:
            run_data = rep.parent().data(0, Qt.ItemDataRole.UserRole)
            rep_data = rep.data(0, Qt.ItemDataRole.UserRole)
            run_id = run_data[g.R_UID_SELF]
            rep_id = rep_data[g.R_UID_SELF]
            if include_data:
                tasks.append((run_id, rep_id, run_data))
            else:
                tasks.append((run_id, rep_id))
        return tasks


    def graph_selected(self):
        tasks = self.get_tasks_from_tree(self.sample_tree)
        for selector in self.stdadd_selectors:
            tasks = tasks + self.get_tasks_from_tree(selector['tree'])
        if tasks:
            self.parent.new_win_results_view(tasks)

    def remove_all(self, tree):
        all_items = [tree.topLevelItem(x) for x in range(tree.topLevelItemCount())]
        for i,item in reversed(list(enumerate(all_items))):
            tree.takeTopLevelItem(i)

    def add_run_to_tree(self, tree, run, method=False):
        analyzed = 0
        for rep in run[g.R_REPLICATES]:
            if rep[g.R_ANALYSIS]:
                analyzed = analyzed+1
        name_lbl = run[g.R_UID_SELF] + ' (' + str(analyzed) + '/'+str(len(run[g.R_REPLICATES]))+')'
        note_lbl = run[g.R_NOTES]
        runitem = QTreeWidgetItem(tree)
        runitem.setText(0, name_lbl)
        if method:
            method_lbl = method[g.M_NAME]
            runitem.setText(1, method_lbl)
            runitem.setText(2, note_lbl)
        else:
            runitem.setText(1, note_lbl)
        runitem.setData(0, Qt.ItemDataRole.UserRole, run)
        if analyzed == 0:
            runitem.setDisabled(True)
            for col in range(0, tree.columnCount()):
                runitem.setToolTip(col, "Please analyze to proceed")

    def type_changed(self):
        self.something_has_been_updated()
        self.results_stack.setCurrentIndex(0)
        calc_type = self.type.currentData()
        self.graph.update_type(calc_type)

    def reg_type_changed(self):
        self.something_has_been_updated()
        self.results_stack.setCurrentIndex(0)
        self.update_reg_type_on_graph()

    def update_reg_type_on_graph(self):
        reg_type = self.reg_type.currentData()
        self.graph.update_reg_type(reg_type)
        
        

    def something_has_been_updated(self):
        self.saved = False

    def get_and_show_results(self):
        r = self.graph.get_results()
        if not r[g.C_EQN]:
            txt = 'None'
        else:
            txt = '<b>Sample concentration</b>: '+str(round(float(r[g.C_CONC_ORIGINAL]), 9))+' mg/L<br><br>'
            txt = txt + 'Model: y = '+str(r[g.C_SLOPE])+' * x + '+str(r[g.C_INT])+'<br><br>'
            txt = txt + 'R^2: '+str(round(float(r[g.C_R2]), 4))+'<br>'
            txt = txt + 'Standard error: '+str(round(float(r[g.C_STDERR]), 4))
        self.results.setText(txt)
        self.results_stack.setCurrentIndex(1)
        if not r[g.C_EQN]:
            return None
        else:
            return r

        
            




    def save(self):
        if self.saved:
            self.status.showMessage("Saved.", g.SB_DURATION)
            return
        r = self.get_and_show_results()
        if r:                               # make sure there are some results
            if self.calc_id:
                r[g.R_UID_SELF] = self.calc_id
            else:
                ids = get_ids(self.parent.data, g.S_PROCESSED)
                self.calc_id = get_next_id(ids, g.C_UID_PREFIX)
                r[g.R_UID_SELF] = self.calc_id
                
            r[g.C_NOTE] = self.notes.toPlainText()

            self.progress_bar.setVisible(True)
            if not self.on_save_mode:
                self.on_save_mode = g.WIN_MODE_EDIT
                self.on_save_calc = self.calc_id
            print("this is what we're gonna save!")
            print(r)
            print()
            
            if self.mode == g.WIN_MODE_NEW:
                self.parent.start_async_save(g.SAVE_TYPE_CALC_NEW, [[r]], onSuccess=self.save_success, onError=self.async_error)   #r gets double bracketed, because it goes to a fn that accepts a list of calcs        
            elif self.mode == g.WIN_MODE_EDIT and self.calc_id:
                self.parent.start_async_save(g.SAVE_TYPE_CALC_EDIT, [self.calc_id, r], onSuccess=self.save_success, onError=self.async_error)
                
                
        else:                               # if no results, show alert
            self.on_save_mode = None
            self.on_save_calc = None
            show_alert(self, "Alert!", "Please complete the analysis and try again.")

    def save_success(self):
        self.saved = True
        self.progress_bar.setVisible(False)
        self.status.showMessage("Saved.", g.SB_DURATION)
        if self.on_save_mode:
            if self.on_save_mode == g.WIN_MODE_CLOSED:
                self.close()
            else:
                self.go_to_mode(self.on_save_mode, self.on_save_calc)

    def async_error(self):
        self.progress_bar.setVisible(False)
        self.status.showMessage("ERROR, operation did not complete", g.SB_DURATION_ERROR)
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
        self.update_calc_list()
        return

    def showEvent(self, event):
        self.parent.setEnabled(False)
        self.parent.set_enabled_children(False)
        self.setEnabled(True)
        event.accept() 
            
    
    def closeEvent(self, event):
        """
        Event handler for close event."""
        # add close/save logic here
        try:
            if not self.continue_action(g.WIN_MODE_CLOSED, None):
                event.ignore()
            else:
                self.accept_close(event)
        except Exception as e:
            print(e)
                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.setEnabled(True)
        self.parent.set_enabled_children(True)
        self.parent.children.remove(self)
        closeEvent.accept()
                                        
