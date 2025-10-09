"""
window_viewSample.py

This file defines a class WindowViewSample which creates a window object
that can be used to view a sample's information.

"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from window_editSample import horizontalize

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

class WindowViewSample(QMainWindow):
    def __init__(self, data):                       
        super().__init__()
        self.data = data                            # add data to self scope
        self.setWindowTitle(custText(l.s_view_info)+" | "+data[g.S_NAME])
        layouts = []                                # create list to hold layouts

        # The name field 
        w_name_lbl = QLabel(custText(l.s_edit_name))
        w_name = QLabel(data[g.S_NAME])
        layouts.append(horizontalize([w_name_lbl, w_name]))
        
        # the date collected field 
        w_lbl_date_collected = QLabel(custText(l.s_edit_date_c))
        date_col = QDate.fromString(data[g.S_DATE_COLLECTED], g.DATE_STORAGE_FORMAT)
        w_date_collected = QLabel(date_col.toString(g.DATE_DISPLAY_FORMAT))                         
        layouts.append(horizontalize([w_lbl_date_collected, w_date_collected]))   # add horizontal layout of label and input
                                                                                            #   to list of horizontal layouts
        # the location collected field
        w_lbl_loc = QLabel(custText(l.s_edit_loc))
        w_loc = QLabel(data[g.S_LOC_COLLECTED])
        layouts.append(horizontalize([w_lbl_loc, w_loc]))

        # the contact info field
        w_lbl_contact = QLabel(custText(l.s_edit_contact))
        w_contact = QLabel(data[g.S_CONTACT])
        layouts.append(horizontalize([w_lbl_contact, w_contact]))

        # the collected by field
        w_lbl_sampler = QLabel(custText(l.s_edit_sampler))
        w_sampler = QLabel(data[g.S_COLLECTED_BY])
        layouts.append(horizontalize([w_lbl_sampler, w_sampler]))

        # the notes field
        w_lbl_notes = QLabel(custText(l.s_edit_notes))
        w_notes = QTextEdit(data[g.S_NOTES])
        w_notes.setReadOnly(True)
        layouts.append(horizontalize([w_lbl_notes, w_notes]))
        
        # organize these widgets into a layout
        layout_pane = QVBoxLayout()
        for layout in layouts:              # add all the rest of the label+input rows
            layout_pane.addLayout(layout)   
        w = QWidget()
        w.setLayout(layout_pane)

        # make the labels and text selectable by user (useful for copy/paste)
        w = makeLabelsSelectable(w)

        self.setCentralWidget(w)


