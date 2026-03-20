
"""
calculate.py

A window that allows the user to use analyzed data, collected with
the potentiostat, to back-calculate the concentration of the
species of interest in the original sample.
"""
from external.globals import ov_globals as g
from external.globals.ov_functions import *

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
    QAbstractItemView
)

class WindowCalculate(QMainWindow):
    def __init__(self, parent, mode, calc_id=None):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent
        self.mode = mode
        self.calc_id = calc_id
        self.method = None
        self.points = [[],[],[]]
        self.stdadd_selectors = []
        self.saved = True
        self.updating_runs = False

        self.border_width_active = '5px'
        self.border_width_passive = '1px'
        self.border_color_good = 'green'
        self.border_color_todo = 'orange'
        self.border_color_error = 'red'
        
        self.status = self.statusBar()
        
        self.set_layout()
    
        # Setup widgets, layout, and (if necessary) mode here

    def get_right_layout(self):
        l = QListWidget()
        b_new = QPushButton()
        b_edit = QPushButton()
        b_dup = QPushButton()
        b_del = QPushButton()

        b_new.setIcon(QIcon(g.ICON_PLUS))
        b_edit.setIcon(QIcon(g.ICON_EDIT))
        b_dup.setIcon(QIcon(g.ICON_DUP))
        b_del.setIcon(QIcon(g.ICON_TRASH))

        b_new.clicked.connect(self.toggle)
        
        h = QHBoxLayout()
        for b in (b_new, b_edit, b_dup, b_del):
            h.addWidget(b)
        
        v = QVBoxLayout()
        v.addWidget(l)
        v.addLayout(h)
        #v.addStretch()
        return v   

    def get_left_layout(self):
        # far left column
        type_lbl = QLabel("Calculation type")
        self.type = QComboBox()
        calc_types = ('Peak height / baseline', 'Peak height', 'Left slope', 'Right slope', 'Mean slope')
        for i, calc_type in enumerate(calc_types):
            self.type.addItem(calc_type, userData=g.C_TYPES[i])

        notes_lbl = QLabel("Notes")
        self.notes = QTextEdit()

        s = QStackedLayout()
        w1 = QPushButton('Show results')
        w1.clicked.connect(partial(s.setCurrentIndex, 1))
        self.results = QTextEdit()
        self.results.setEnabled(False)
        s.addWidget(w1)
        s.addWidget(self.results)

        v0 = QVBoxLayout()
        v0.addWidget(type_lbl)
        v0.addWidget(self.type)
        v0.addWidget(notes_lbl)
        v0.addWidget(self.notes)
        v0.addStretch()
        v0.addLayout(s)

        # center column
        self.graph = QTextEdit() ################## PLACEHOLDER HERE FOR NOW TILL SOMEONE GETS AROUND TO MAKING THE GRAPH :P

        
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
            
        but_add_point = QPushButton('+')
        h1.addWidget(but_add_point)

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
        
        self.load_sample_runs(tree)

        b = QPushButton('Graph')
        b.clicked.connect(partial(self.graph_from_tree, tree))
        
        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(tree)
        v.addWidget(b)
       
        return v
    
    def get_stdadd_selector_layout(self, i):
        title_str = 'Standard addition '+str(i)
        t1 = QLabel(title_str)
        t2 = QLabel(title_str)
        t3 = QLabel(title_str)
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if i == 1: msg = "Please select at lesat one <b>sample</b> run  <-----"
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
        #tree.itemSelectionChanged.connect(partial(self.update_run_list, tree))
        b2 = QPushButton('Graph')
        v2 = QVBoxLayout()
        v2.addWidget(t2)
        v2.addWidget(tree)
        v2.addWidget(b2)
        w2 = QWidget()
        w2.setLayout(v2)

        box3 = QTextEdit('There are no available standard additions with the selected method')
        box3.setEnabled(False)
        self.set_widget_border(box3, self.border_width_passive, self.border_color_error)
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
        l = self.get_full_layout()
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def toggle(self):
        if self.mode == g.WIN_MODE_RIGHT: self.mode = g.WIN_MODE_NEW
        else: self.mode = g.WIN_MODE_RIGHT
        self.set_layout()


    def load_sample_runs(self, run_list):
        # Get "sample" runs
        try:
            # If any elements in run list, remove them all
            self.updating_runs = True
            self.remove_all(run_list)
                    
            # Add back in all runs with type == sample
            for run in self.parent.data[g.S_RUNS]:          
                if run[g.R_TYPE] == g.R_TYPE_SAMPLE:
                    method = get_method_from_file_data(self.parent.data, run[g.R_UID_METHOD])
                    self.add_run_to_tree(run_list, run, method=method)
    
            self.updating_runs = False  
                
        except Exception as e:
            print(e)

    def load_stdadd_runs(self, i):
        
        try:
            # If any elements in run list, remove them all
            tree = self.stdadd_selectors[i]['tree']
            self.updating_runs = True
            self.remove_all(tree)

            # Add back in all runs with type == stdadd and method matching self.method
            for run in self.parent.data[g.S_RUNS]:
                if run[g.R_TYPE] == g.R_TYPE_STDADD and run[g.R_UID_METHOD] == self.method:
                    self.add_run_to_tree(tree, run)
            self.updating_runs = False
        except Exception as e:
            print(e)
                    

            

            
        

        
    def update_sample_runs(self, run_list, selector_index):
        if self.updating_runs:
            return
        try:
            selected_runs = self.get_selected_runs(run_list)


            if selected_runs:
                # grab method of first selected run (in case multiple selected simultaneously
                self.method = selected_runs[0].data(0, Qt.ItemDataRole.UserRole)[g.R_UID_METHOD]

                # loop backwards thru runs. If run doesn't match selected method, take it from list
                all_items = [run_list.topLevelItem(x) for x in range(run_list.topLevelItemCount())]
                self.updating_runs = True
                for i,item in reversed(list(enumerate(all_items))):
                    if item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_METHOD] != self.method:
                        run_list.takeTopLevelItem(i)
                

                # for each selected run, show all reps and select them, for deselected runs, remove children
                all_items = [run_list.topLevelItem(x) for x in range(run_list.topLevelItemCount())]
                for item in all_items:
                    if item.isSelected() and item.childCount() == 0:        # If item is newly selected, show all children and select!
                        for rep in item.data(0, Qt.ItemDataRole.UserRole)[g.R_REPLICATES]:
                            subitem = QTreeWidgetItem(item)
                            subitem.setData(0, Qt.ItemDataRole.UserRole, rep)
                            subitem.setText(0, rep[g.R_UID_SELF])
                            subitem.setText(2, rep[g.R_NOTES])
                            if not rep[g.R_ANALYSIS]:
                                subitem.setDisabled(True)
                                for col in range(0, run_list.columnCount()):
                                    subitem.setToolTip(col, "Please analyze to proceed")
                            else: subitem.setSelected(True)
                            self.set_widget_border(run_list, self.border_width_passive, self.border_color_good)
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
                        

                self.updating_runs = False

            # Check if any runs are selected anymore.                 
            selected_runs = self.get_selected_runs(run_list)
            if not selected_runs:                   # if not
                self.method = None                  # reset method
                self.load_sample_runs(run_list)     # reset sample pane
                self.set_widget_border(run_list, self.border_width_active, self.border_color_todo)

            # Update next pane based on status of this pane
            
            self.points[selector_index] = self.get_tasks_from_tree(run_list)
            self.update_other_selectors(selector_index)
        except Exception as e:
            print('error is HERE!')
            print(e)

    def update_stdadd_runs(self, i):
        return

    def update_other_selectors(self, i):
        if not self.points[0]:
            for selector in self.stdadd_selectors:
                selector['layout'].setCurrentIndex(g.C_STACK_INDEX_BASE)
        else:
            
            # Get j, the index of the first selector w no selected points
            empty = False
            for j,point in enumerate(self.points):
                if point:                           
                    empty = True
                    break
            if empty:                   # if there is a selector w no selected points
                # show selector[j]
                self.stdadd_selectors[j]['layout'].setCurrentIndex(g.C_STACK_INDEX_SELECTOR)

                # hide all selectors[k] for k>j
                for k, selector in enumerate(self.stdadd_selectors):
                    if k>j: selector['layout'].setCurrentIndex(g.C_STACK_INDEX_BASE)

                # for all stdadds w index between 0 and j
                #   erase tree
                #   add all stdadd runs to tree that are either in points[j+1] or not in points at all.
                self.load_stdadd_runs(j)
                self.update_stdadd_runs(j)

                
                
        

    def get_all(self, tree):
        return

    def get_selected(self, tree):
        return tree.selectedItems()

    def get_selected_runs(self, tree):
        selected_items = self.get_selected(tree)
        selected_runs = [item for item in selected_items if g.R_RUN_UID_PREFIX
                         in item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]]
        return selected_runs


    def get_selected_reps(self, tree):
        selected_items = self.get_selected(tree)
        selected_reps = [item for item in selected_items if g.R_REPLICATE_UID_PREFIX
                         in item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]]
        return selected_reps

    def get_tasks_from_tree(self, tree):
        reps = self.get_selected_reps(tree)
        tasks = []
        for rep in reps:
            run_id = rep.parent().data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
            rep_id = rep.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]
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


        
        

        
            




    def save(self):
        ############ USE THIS TO CHECK STUFF UNTIL ACTUALLY IMPLEMENTING SAVE METHOD
        print(self.type.currentText())
        print(self.type.currentData())
        print()

            
        
    def update_win(self):
        """Designed to be called when parent's data has been reloaded.
        Updates this window with new data as needed"""
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
                                        
