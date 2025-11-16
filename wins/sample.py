"""
window_editSample.py

This file defines a class WindowEditSample which creates a window object
that can be used to create a new sample (if blank) or to edit an existing
sample file (if passed the path of the sample file).

The sample file may be saved to a file named by the user anywhere in the
local directory.

All files are in .json format. 
"""

import ov_globals as g
import ov_lang as l
from ov_functions import *

from tkinter.filedialog import asksaveasfilename as askSaveAsFileName
from functools import partial

from PyQt6.QtCore import QDateTime, QDate
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox
)

class WindowSample(QMainWindow):
    def __init__(self, path, parent, view_only=False, update_on_save=False, open_on_save=False):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.path = path                            # create an empty string for holding the filepath
        self.parent = parent                        # store the parent object in object-wide scope
        self.data = {}                              # create an empty dict to hold data read from a file
        self.saved = False                          # reset flag to indicate current data shown in pane hasn't been saved
        self.setObjectName("window-edit-sample")    # create a name for modifying styles from QSS
        layouts = []                                # create list to hold layouts
        self.view_only = view_only
        self.update_on_save = update_on_save
        self.open_on_save = open_on_save


        print(type(self.parent))
        print(parent)
        

        # The name field 
        self.w_name = QLineEdit()                                       # init line edit
        self.w_name.setMaxLength(63)                                    # set properties
        self.w_name.setObjectName(encodeCustomName(g.S_NAME))           # add object name for specific styling and data mgmt
        if self.view_only:
            but_edit = QPushButton('edit')
            but_edit.clicked.connect(parent.edit_sample)
        

        # the date collected field 
        w_lbl_date_collected = QLabel(l.s_edit_date_c[g.L])                                 # init label with text
        self.w_date_collected = QDateEdit()                                                 # init input
        self.w_date_collected.setDisplayFormat(g.DATE_DISPLAY_FORMAT)                       # set input properties
        self.w_date_collected.setCalendarPopup(True)                                
        self.w_date_collected.setObjectName(encodeCustomName(g.S_DATE_COLLECTED))           # add name to input for data mgmt
        layouts.append(horizontalize([w_lbl_date_collected, self.w_date_collected]))   # add horizontal layout of label and input
                                                                                            #   to list of horizontal layouts
        # the location collected field
        w_lbl_loc = QLabel(l.s_edit_loc[g.L])
        self.w_loc = QLineEdit()
        self.w_loc.setMaxLength(63)
        self.w_loc.setObjectName(encodeCustomName(g.S_LOC_COLLECTED))
        layouts.append(horizontalize([w_lbl_loc, self.w_loc]))

        # the contact info field
        w_lbl_contact = QLabel(l.s_edit_contact[g.L])
        self.w_contact = QLineEdit()
        self.w_contact.setMaxLength(63)
        self.w_contact.setObjectName(encodeCustomName(g.S_CONTACT))
        layouts.append(horizontalize([w_lbl_contact, self.w_contact]))

        # the collected by field
        w_lbl_sampler = QLabel(l.s_edit_sampler[g.L])
        self.w_sampler = QLineEdit()
        self.w_sampler.setMaxLength(63)
        self.w_sampler.setObjectName(encodeCustomName(g.S_COLLECTED_BY))
        layouts.append(horizontalize([w_lbl_sampler, self.w_sampler]))

        # the notes field
        w_lbl_notes = QLabel(l.s_edit_notes[g.L])
        self.w_notes = QTextEdit()
        self.w_notes.setObjectName(encodeCustomName(g.S_NOTES))
        layouts.append(horizontalize([w_lbl_notes, self.w_notes]))

        # the save (and save as) button(s)
        but_save = QPushButton(l.s_edit_save[g.L])                          # create 'save' button
        but_save_as = QPushButton(l.s_edit_save_as[g.L])                    # create 'save as' button
        but_save_as.clicked.connect(partial(self.startSave, 'save as'))
        layout_but = QHBoxLayout()
        layout_but.addWidget(but_save)                                      # add 'save' button to horiz button layout
        if self.path:                                                       # if we are modifying an existing file
            but_save.clicked.connect(partial(self.startSave, 'save'))       #   then the 'save' button does the regular save action
            layout_but.addWidget(but_save_as)                               #   also add the 'save as' button to the button layout
        else:
            but_save.clicked.connect(partial(self.startSave, 'save as'))    # if new sample, run 'save as' when 'save' is clicked

        # organize these widgets into a layout
        layout_pane = QVBoxLayout()
        if self.view_only:
            layout_pane.addLayout(horizontalize([self.w_name, but_edit]))
        else:
            layout_pane.addWidget(self.w_name)  # add the name first
        for layout in layouts:              # add all the rest of the label+input rows
            layout_pane.addLayout(layout)   
        if not self.view_only:
            layout_pane.addLayout(layout_but)     # add the save button on the bottom
        self.w = QWidget()
        self.w.setLayout(layout_pane)

        if self.view_only:
            self.w_name.setEnabled(False)
            self.w_date_collected.setEnabled(False)
            self.w_loc.setEnabled(False)
            self.w_contact.setEnabled(False)
            self.w_sampler.setEnabled(False)
            self.w_notes.setEnabled(False)
            
        # if a path was entered, gather the data from the specified file and display it
        if self.path:
            try:
                self.setTextFromFile()
            except Exception as e:
                print(e)
            if self.view_only:
                self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.view_sample[g.L])
            else:
                self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.edit_sample[g.L])
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.new_sample[g.L])
            self.w_name.setPlaceholderText(l.s_edit_name[g.L])


        self.setCentralWidget(self.w)

    def startSave(self, save_type):
        if self.validate():
            try:
                if save_type == 'save as':
                    self.saveFileAs()
                else:
                    self.saveFile()
            except Exception as e:
                print(e)

    def validate(self):
        """
        Validates the form. If there is an error, a dialog is displayed to
        user that describes the error and the function returns False.
        If no error, returns True
        """
        if len(self.w_name.text()) < g.SAMPLE_NAME_MIN_LENGTH:
            show_alert(self, l.alert_header[g.L], l.alert_s_edit_name[g.L])
            return False
        else:
            return True

    def setTextFromFile(self):
        self.data = get_data_from_file(self.path)
        w = self.w
        
        textedits = w.findChildren(QLineEdit) + w.findChildren(QTextEdit) # grab all line and text edit objects from form
        dateedits = w.findChildren(QDateEdit)                                  # grab all date edit objects from form


        # loop through all line edit elements, saving entered text
        for el in textedits:
            if isCustomName(el.objectName()):
                el.setText(self.data[decodeCustomName(el.objectName())])

        # loop through all date elements, saving date
        for el in dateedits:
            if isCustomName(el.objectName()):
                d = QDate.fromString(self.data[decodeCustomName(el.objectName())], g.DATE_STORAGE_FORMAT)
                el.setDate(d)    


    def saveFileAs(self):
        # get the actual filename and path from user

        self.path = askSaveAsFileName(                           # open a save file dialog which returns the file object
            filetypes=[(l.filetype_sample_lbl[g.L], g.SAMPLE_FILE_TYPES)],
            defaultextension=g.SAMPLE_EXT,
            confirmoverwrite=True,
            initialfile=guess_filename(self.w_name.text()))
        if not self.path or self.path == '':            # if the user didn't select a path
            return                                      # don't try to save, just return
        self.saveFile()                                 # save the file!

    def saveFile(self):
        lineedits = self.findChildren(QLineEdit)            # grab all line edit objects from form
        dateedits = self.findChildren(QDateEdit)            # grab all date edit objects from form
        textedits = self.findChildren(QTextEdit)            # grab all paragraph text edit objects from form
        newSample = True
        if self.data:
            newSample = False
                

        # loop through all line edit elements, saving entered text
        for el in lineedits:
            if isCustomName(el.objectName()):
                self.data.update({decodeCustomName(el.objectName()): el.text()})

        # loop through all date elements, saving date
        for el in dateedits:
            if isCustomName(el.objectName()):
                self.data.update({decodeCustomName(el.objectName()): el.date().toString(g.DATE_STORAGE_FORMAT)})

        # loop through all paragraph edit(textedit) elements, saving text
        for el in textedits:
            if isCustomName(el.objectName()):
                self.data.update({decodeCustomName(el.objectName()): el.toPlainText()})

        if newSample:
            # append current datetime
            self.data.update({g.S_DATE_ENTERED: QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)})
        
            # append empty arrays for future data
            for key in g.S_BLANK_ARRAYS:
                self.data.update({key:[]})


        # write dict to file
        write_data_to_file(self.path, self.data)
        self.saved = True                                   # set flag that file has been successfully saved
        self.close()                                        # close the new sample window

    def closeEvent(self, event):
        """
        This is the handler for all close envents, including those generated by the user
        (eg. the press of the X button) and those generated programatically (eg. a
        'self.close()' statement). The name of this function is dictated by PyQt6's
        specification for event handling.

        Algorithm:
        Checks the flag self.saved.
            If True, window is closed.
            If False, displays a dialog with three options: save, discard, and cancel.
                - if save is selected, the close action is blocked and the save
                    routine is called
                - if discard is selected, the window is closed
                - if cancel is selected, the close action is blocked
        """
        if self.view_only:      # If the pane is view only (no editing possible)
            event.accept()      # we don't need to ask about saving, so close window
        else:
        
            if not self.saved:                                      # if there is unsaved content:

                confirm = saveMessageBox(self)                      # init a dialog asking the user if they're sure
                resp = confirm.exec()                               # launch the dialog

                if resp == QMessageBox.StandardButton.Save:         # if the user selects "Save"
                    event.ignore()                                  #   block the close action
                    if self.path:                                   # if there is already a save path
                        self.startSave('save')                      #   run the 'save' function
                    else:                                           # otherwise,
                        self.startSave('save as')                   #   run the 'save as' function
                elif resp == QMessageBox.StandardButton.Discard:    # if the user selects "discard"
                    event.accept()                                  #   allow the close action to complete
                else:                                               # if the user selects "cancel" (or anything else)
                    event.ignore()                                  #   block the close action
            else:                                                   # if there is no unsaved content
                try:
                    if self.open_on_save:
                        self.parent.open_sample(self.path)              #   open the recently saved sample
                    if self.update_on_save:
                        self.parent.update_displayed_info()
                    event.accept()                                  #   then allow the close event to proceed
                except Exception as e:
                    print(e)
                                        


class saveMessageBox(QMessageBox):
    def __init__(self, parent):                       
        super().__init__()
        # set text for save message
        self.setWindowTitle(l.s_edit_discard[g.L]) 
        self.setText(l.e_edit_save_dialog[g.L])
        self.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

        # customize button language text for multi-language support
        but_save = self.button(QMessageBox.StandardButton.Save)
        but_save.setText(l.s_edit_save[g.L])
        but_disc = self.button(QMessageBox.StandardButton.Discard)
        but_disc.setText(l.s_edit_close_wo_save[g.L])
        but_canc = self.button(QMessageBox.StandardButton.Cancel)
        but_canc.setText(l.s_edit_cancel[g.L])
