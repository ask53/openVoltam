
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
    QInputDialog
)

class WindowCalculate(QMainWindow):
    def __init__(self, parent, mode, calc_id=None):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.calc_id = calc_id

        self.reset_globals()

        # Selector border widths and colors
        self.border_width_active = '5px'
        self.border_width_passive = '1px'
        self.border_color_good = 'green'
        self.border_color_todo = 'orange'
        self.border_color_error = 'red'

        # Status Bar and Progress Bar
        self.status = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMaximumWidth(g.SB_PROGRESS_BAR_WIDTH)  # Set a fixed width
        self.progress_bar.setVisible(False)     # Hide it initially
        self.status.addPermanentWidget(self.progress_bar)

        # Set the layout programatically
        self.set_layout()
        
    def reset_globals(self):
        self.method = None
        self.points = [[],[],[]]
        self.stdadd_selectors = []
        self.saved = True
        self.updating_runs = False

    def get_right_layout(self):
        self.calc_list = QListWidget()
        self.calc_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.calc_list.setAlternatingRowColors(True)
        self.calc_list.setSpacing(2)
        self.calc_list.itemSelectionChanged.connect(self.update_right_buttons)
        b_new = QPushButton()
        b_edit = QPushButton()
        b_dup = QPushButton()
        b_del = QPushButton()

        b_new.setIcon(QIcon(g.ICON_PLUS))
        b_edit.setIcon(QIcon(g.ICON_EDIT))
        b_dup.setIcon(QIcon(g.ICON_DUP))
        b_del.setIcon(QIcon(g.ICON_TRASH))

        b_new.clicked.connect(self.toggle)

        b_del.clicked.connect(self.delete)

        self.right_buttons_one_only = [b_edit]
        self.right_buttons_one_plus = [b_dup, b_del]
        
        h = QHBoxLayout()
        for b in (b_new, b_edit, b_dup, b_del):
            h.addWidget(b)
        
        v = QVBoxLayout()
        v.addWidget(self.calc_list)
        v.addLayout(h)
        #v.addStretch()

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
            txt = calc[g.R_UID_SELF] + ' ('+calc[g.C_TYPE] +')\n'
            txt = txt + runtxt + '\n'
            txt = txt + 'Result: '+str(round(calc[g.C_CONC_ORIGINAL],8))+' +/- STD_DEV mg/L'
            
            # Create the list element and attach it to the list
            calcitem = QListWidgetItem(self.calc_list)
            calcitem.setText(txt)
            calcitem.setData(Qt.ItemDataRole.UserRole, calc)

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
        # far left column
        type_lbl = QLabel("Calculation type")
        self.type = QComboBox()
        self.type.setPlaceholderText('Select')
        calc_types = ('Peak height / baseline', 'Peak height', 'Left slope', 'Right slope', 'Mean slope')
        for i, calc_type in enumerate(calc_types):
            self.type.addItem(calc_type, userData=g.C_TYPES[i])
        self.type.currentIndexChanged.connect(self.type_changed)
        notes_lbl = QLabel("Notes")
        self.notes = QTextEdit()

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
        v0.addWidget(notes_lbl)
        v0.addWidget(self.notes)
        v0.addStretch()
        v0.addLayout(self.results_stack)

        # center column
        self.graph = StdAddFitterPlot(self, 'Best-fit calculator') 

        
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
            
        '''but_add_point = QPushButton('+')
        h1.addWidget(but_add_point)'''

        v1 = QVBoxLayout()
        v1.addWidget(self.graph)
        v1.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addLayout(v0)
        h2.addWidget(QVLine())
        h2.addLayout(v1)

        but_save = QPushButton('save')
        but_save.clicked.connect(self.save)

        v2 = QVBoxLayout()
        v2.addLayout(h2)
        v2.addWidget(but_save)

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
        title = QLabel('Sample')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tree = self.get_run_tree_widget(with_method = True)
        tree.itemSelectionChanged.connect(partial(self.update_sample_runs, tree, 0))

        self.updating_runs = True
        self.load_sample_runs(tree)
        self.updating_runs = False

        b = QPushButton('Graph')
        b.clicked.connect(partial(self.graph_from_tree, tree))
        
        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(tree)
        v.addWidget(b)
        w = QWidget()
        w.setLayout(v)

        s = QStackedLayout()
        s.addWidget(w)
       
        return s
    
    def get_stdadd_selector_layout(self, i):
        title_str = 'Standard addition '+str(i)
        t1 = QLabel(title_str)
        t2 = QLabel(title_str)
        t3 = QLabel(title_str)
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t3.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        b2 = QPushButton('Graph')
        b2.clicked.connect(partial(self.graph_from_tree, tree))
        v2 = QVBoxLayout()
        v2.addWidget(t2)
        v2.addWidget(tree)
        v2.addWidget(b2)
        w2 = QWidget()
        w2.setLayout(v2)

        box3 = QTextEdit('There are no available standard additions with the selected method')
        box3.setEnabled(False)
        self.set_widget_border(box3, self.border_width_active, self.border_color_error)
        v3 = QVBoxLayout()
        v3.addWidget(t3)
        v3.addWidget(box3)
        v3.addStretch()
        w3 = QWidget()
        w3.setLayout(v3)
        
        for w in (w1,w2,w3):
            s.addWidget(w)

        self.stdadd_selectors.append({'tree': tree,
                                      'layout': s})

        s.setCurrentIndex(g.C_STACK_INDEX_BASE)

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

    def set_layout(self):
        self.reset_globals()
        l = self.get_full_layout()
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def toggle(self):
        """Toggles the display between right-pane only and adding a new calculation.
        If there is an unsaved calculation in the left pane, prompts the user about
        saving unsaved work before toggling"""
        ##################################################################################################
        #
        #   PROMPT USER ABOUT SAVING IF THERE IS UNSAVED WORK
        #
        ###########################################################################################################################################
        if self.mode == g.WIN_MODE_RIGHT: self.mode = g.WIN_MODE_NEW
        else: self.mode = g.WIN_MODE_RIGHT
        self.set_layout()

    def delete(self):

        items = self.calc_list.selectedItems()
        tasks = []
        for item in items:
            data = item.data(Qt.ItemDataRole.UserRole)
            tasks.append(data[g.R_UID_SELF])

        if self.mode==g.WIN_MODE_EDIT and self.calc_id in tasks:
            show_alert(self, "Alert!", "Cannot delete the calculation that is currently being edited ("+str(self.calc_id)+").\nPlease make a different selection and try again.")
            return
            
        if self.confirm_delete():
            self.progress_bar.setVisible(True)
            self.parent.start_async_save(g.SAVE_TYPE_CALC_DELETE, [tasks], onSuccess=self.delete_success, onError=self.async_error)

    def confirm_delete(self):
        title = 'Confirm delete'
        text = 'This will permanently delete all selected calculations.\n\nIf you are sure you want to delete, type DELETE below.'
        text, ok = QInputDialog.getText(self, title, text)
        if ok:
            if text == 'DELETE':
                return True
        return False

    def delete_success(self):
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
                self.show_reps_from_runs(run_list)
                
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
            if self.updating_runs: return               # to avoid recursion
            self.updating_runs = True                   # stops recursive calls during this fn
            tree = self.stdadd_selectors[i]['tree']
            selected_runs = self.get_selected_runs(tree)
            if selected_runs:
                               # if we're about to do some auto-updating, avoid recursion
                self.show_reps_from_runs(tree)
                

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
        self.saved = False
        self.results_stack.setCurrentIndex(0)
        self.points[i] = self.get_tasks_from_tree(tree, include_data=True)
        erase = False
        for i,point in enumerate(self.points):
            if not erase:           # find first point with no entries
                if not point:   
                    erase = True
            else:                   # erase data in all higher points
                self.points[i] = []

    def show_reps_from_runs(self, tree):
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
        

    def graph_from_tree(self, tree):
        tasks = self.get_tasks_from_tree(tree)
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
        self.saved = False
        self.results_stack.setCurrentIndex(0)
        calc_type = self.type.currentData()
        self.graph.update_type(calc_type)

    def get_and_show_results(self):
        r = self.graph.get_results()
        if not r[g.C_EQN]:
            txt = 'None'
        else:
            txt = '<b>Sample concentration</b>: '+str(round(float(r[g.C_CONC_ORIGINAL]), 9))+' mg/L<br><br>'
            txt = txt + 'R^2: '+str(round(float(r[g.C_R2]), 4))+'<br>'
            txt = txt + 'Standard error: '+str(round(float(r[g.C_STDERR]), 4))
        self.results.setText(txt)
        self.results_stack.setCurrentIndex(1)
        if not r[g.C_EQN]:
            return None
        else:
            return r

        
            




    def save(self):
        r = self.get_and_show_results()
        if r:                               # make sure there are some results
            ids = get_ids(self.parent.data, g.S_PROCESSED)
            calc_id = get_next_id(ids, g.C_UID_PREFIX)
            r[g.R_UID_SELF] = calc_id
            r[g.C_NOTE] = self.notes.toPlainText()

            self.progress_bar.setVisible(True)
            self.parent.start_async_save(g.SAVE_TYPE_CALC_NEW, [r], onSuccess=self.save_success, onError=self.async_error)           
        else:                               # if no results, show alert
            show_alert(self, "Alert!", "Please complete the analysis and try again.")

    def save_success(self):
        self.saved = True
        self.progress_bar.setVisible(False)
        self.status.showMessage("Complete", g.SB_DURATION)

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
                                        
