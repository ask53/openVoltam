
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
        self.saved = True
        self.updating_runs = False
        
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

    def get_sample_selector_layout(self):
        title = QLabel('Sample')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        '''s = QStackedLayout()
        w1 = QPushButton('Select sample')'''
        
        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels(('Run', 'Method', 'Note')) 
        tree.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        tree.setAlternatingRowColors(True)
        tree.itemSelectionChanged.connect(partial(self.update_run_list, tree))
        self.load_sample_runs(tree)
        v = QVBoxLayout()
        v.addWidget(title)
        v.addWidget(tree)
       
        return v
    
    def get_stdadd_selector_layout(self, i):
        t = QLabel('Standard addition '+str(i))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s = QStackedLayout()
        w1 = QPushButton('Select standard addition '+str(i))
        w1.clicked.connect(partial(s.setCurrentIndex, g.C_STACK_INDEX_RUNS))

        l2 = QListWidget()
        b2 = QPushButton('Accept')
        b2.clicked.connect(partial(s.setCurrentIndex, g.C_STACK_INDEX_REPS))
        v2 = QVBoxLayout()
        v2.addWidget(l2)
        v2.addWidget(b2)
        w2 = QWidget()
        w2.setLayout(v2)

        l3 = QListWidget()
        b3a = QPushButton('Graph')
        b3b = QPushButton('Change runs')
        b3b.clicked.connect(partial(s.setCurrentIndex,g.C_STACK_INDEX_RUNS))
        h3 = QHBoxLayout()
        h3.addWidget(b3a)
        h3.addWidget(b3b)
        v3 = QVBoxLayout()
        v3.addWidget(t)
        v3.addWidget(l3)
        v3.addLayout(h3)
        w3 = QWidget()
        w3.setLayout(v3)

        w4 = QLabel('Standard addition '+str(i))
        w4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        w5 = QLabel("No compatible standard additions")

        for w in (w1,w2,w3,w4,w5):
            s.addWidget(w)

        s.setCurrentIndex(g.C_STACK_INDEX_BLANK)

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
            all_items = [run_list.topLevelItem(x) for x in range(run_list.topLevelItemCount())]
            for i,item in reversed(list(enumerate(all_items))):
                run_list.takeTopLevelItem(i)
            
            # Add back in all runs with type == sample
            for run in self.parent.data[g.S_RUNS]:          
                if run[g.R_TYPE] == g.R_TYPE_SAMPLE:
                    method = get_method_from_file_data(self.parent.data, run[g.R_UID_METHOD])
                    name_lbl = run[g.R_UID_SELF] + ' (' + str(len(run[g.R_REPLICATES])) + ')'
                    method_lbl = method[g.M_NAME]
                    note_lbl = run[g.R_NOTES]
                    runitem = QTreeWidgetItem(run_list)
                    runitem.setText(0, name_lbl)
                    runitem.setText(1, method_lbl)
                    runitem.setText(2, note_lbl)
                    runitem.setData(0, Qt.ItemDataRole.UserRole, run)

                    '''for rep in run[g.R_REPLICATES]:
                        repitem = QTreeWidgetItem(runitem)
                        repitem.setText(0, rep[g.R_UID_SELF])
                        repitem.setText(2, rep[g.R_NOTES])'''

            self.updating_runs = False
            
                
        except Exception as e:
            print(e)

        
    def update_run_list(self, run_list):
        if self.updating_runs:
            return

        selected_items = run_list.selectedItems()
        selected_runs = [item for item in selected_items if g.R_RUN_UID_PREFIX
                         in item.data(0, Qt.ItemDataRole.UserRole)[g.R_UID_SELF]]



        try:
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
                            subitem.setSelected(True)
                        item.setExpanded(True)
                    if not item.isSelected() and (item.childCount() != 0):  # If item is no longer selected, hide all children!
                        item.takeChildren()
                    if item.isSelected() and item.childCount() != 0:         # If item is selected and already has children, check
                        selected_children = False                           #   whether they should be hidden
                        for i in range(0,item.childCount()):
                            if item.child(i).isSelected():
                                selected_children=True
                                break
                        if not selected_children:       # If all children have been deselected by user
                            item.takeChildren()         # Remove them all from the layout
                            item.setSelected(False)     # And deselect the run itself
                        

                self.updating_runs = False

                
            else:                           # If there are no runs selected, reload all runs!
                self.method = None
                self.load_sample_runs(run_list)

            items = run_list.selectedItems()
            print(len(items))
        except Exception as e:
            print('error is HERE!')
            print(e)


        
        

        
            




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
                                        
