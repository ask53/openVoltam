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

from PyQt6.QtCore import QDateTime, QDate, Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QDateEdit,
    QPlainTextEdit,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QProgressBar
)

class WindowSample(QMainWindow):
    def __init__(self, parent, mode=g.WIN_MODE_NEW):  
        super().__init__()                          # if path, load sample deets, else load empty edit window for new sample
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.parent = parent                        # store the parent object in object-wide scope
        self.mode = mode
        self.saved = True                           # set flag to indicate current data shown reflects what is already saved
        self.setObjectName("window-edit-sample")    # create a name for modifying styles from QSS
        layouts = []                                # create list to hold layouts
        #self.view_only = view_only
        self.close_on_save = False
        #self.new_sample = False
        #if not self.path:
        #    self.new_sample = True
        self.status = self.statusBar()
        self.progress_bar = QProgressBar()

        #####################
        #                   #
        #   status bar      #
        #                   #
        ##################### 
        self.progress_bar.setMaximumWidth(200)  # Set a fixed width
        self.progress_bar.setVisible(False)     # Hide it initially
        self.status.addPermanentWidget(self.progress_bar)

        #####################
        #                   #
        #   Set up widgets  #
        #                   #
        #####################
        
        # The name field 
        self.w_name = QLineEdit()                                       # init line edit
        self.w_name.setMaxLength(63)                                    # set properties
        self.w_name.setObjectName(encodeCustomName(g.S_NAME))           # add object name for specific styling and data mgmt
        self.w_name.textEdited.connect(self.update_edited_status)

        # the date collected field 
        w_lbl_date_collected = QLabel(l.s_edit_date_c[g.L])                                 # init label with text
        self.w_date_collected = QDateEdit()                                                 # init input
        self.w_date_collected.setDisplayFormat(g.DATE_DISPLAY_FORMAT)                       # set input properties
        self.w_date_collected.setCalendarPopup(True)                                
        self.w_date_collected.setObjectName(encodeCustomName(g.S_DATE_COLLECTED))           # add name to input for data mgmt
        self.w_date_collected.userDateChanged.connect(self.update_edited_status)
        layouts.append(horizontalize([w_lbl_date_collected, self.w_date_collected]))   # add horizontal layout of label and input
                                                                                            #   to list of horizontal layouts
        # the location collected field
        w_lbl_loc = QLabel(l.s_edit_loc[g.L])
        self.w_loc = QLineEdit()
        self.w_loc.setMaxLength(63)
        self.w_loc.setObjectName(encodeCustomName(g.S_LOC_COLLECTED))
        self.w_loc.textEdited.connect(self.update_edited_status)
        layouts.append(horizontalize([w_lbl_loc, self.w_loc]))

        # the contact info field
        w_lbl_contact = QLabel(l.s_edit_contact[g.L])
        self.w_contact = QLineEdit()
        self.w_contact.setMaxLength(63)
        self.w_contact.setObjectName(encodeCustomName(g.S_CONTACT))
        self.w_contact.textEdited.connect(self.update_edited_status)
        layouts.append(horizontalize([w_lbl_contact, self.w_contact]))

        # the collected by field
        w_lbl_sampler = QLabel(l.s_edit_sampler[g.L])
        self.w_sampler = QLineEdit()
        self.w_sampler.setMaxLength(63)
        self.w_sampler.setObjectName(encodeCustomName(g.S_COLLECTED_BY))
        self.w_sampler.textEdited.connect(self.update_edited_status)
        layouts.append(horizontalize([w_lbl_sampler, self.w_sampler]))

        # the notes field
        w_lbl_notes = QLabel(l.s_edit_notes[g.L])
        self.w_notes = QPlainTextEdit()
        self.w_notes.setObjectName(encodeCustomName(g.S_NOTES))
        self.w_notes.textChanged.connect(self.update_edited_status)
        layouts.append(horizontalize([w_lbl_notes, self.w_notes]))

        # the bottom button row (save, save as, and edit button(s) -- depend on state)
        self.but_new = QPushButton(l.s_edit_save[g.L])                      # create 'save' button for new samples
        self.but_existing_edit = QPushButton(l.s_edit_save[g.L])            # create 'save' button for existing samples 
        self.but_existing_view = QPushButton(l.s_edit_edit[g.L])            # create 'edit' button for existing samples

        self.but_new.clicked.connect(self.start_save_new)
        self.but_existing_edit.clicked.connect(self.start_save_existing)
        self.but_existing_view.clicked.connect(self.set_mode_edit)

        self.buts = [self.but_new, self.but_existing_edit, self.but_existing_view]  # list of all buttons
        self.read_only = [self.w_date_collected,                                    # on read_only, set these to read only = True
                          self.w_notes]
        self.not_enabled = [self.w_name,                                            # on read_only set these to enabled = False
                            self.w_loc,
                            self.w_contact,
                            self.w_sampler]
                    
        
        # organize these widgets into a layout
        layout_pane = QVBoxLayout()
        layout_pane.addWidget(self.w_name)  # add the name first
        for layout in layouts:              # add all the rest of the label+input rows
            layout_pane.addLayout(layout)
        
        self.w = QWidget()
        self.w.setLayout(layout_pane)
            
        # if a path was entered, gather the data from the specified file and display it
        if not self.mode == g.WIN_MODE_NEW:
            self.update_win()

        self.saved = True               #set this again as the process of setting text may mess with this flag, but no data has changed
        self.setCentralWidget(self.w)

        # Set the current mode (new sample, edit existing sample, or view existing sample)
        if self.mode == g.WIN_MODE_NEW:
            self.set_mode_new()
        elif self.mode == g.WIN_MODE_EDIT:
            self.set_mode_edit()
        else:
            self.set_mode_view()

    def update_win(self):
        data = self.parent.data
        w = self.w
        
        textedits = w.findChildren(QLineEdit)
        plaintextedits = w.findChildren(QPlainTextEdit) 
        dateedits = w.findChildren(QDateEdit)                                  

        # loop through all line edit elements, saving entered text
        for el in textedits:
            if isCustomName(el.objectName()):
                el.setText(data[decodeCustomName(el.objectName())])

        for el in plaintextedits:
            if isCustomName(el.objectName()):
                el.setPlainText(data[decodeCustomName(el.objectName())])

        # loop through all date elements, saving date
        for el in dateedits:
            if isCustomName(el.objectName()):
                d = QDate.fromString(data[decodeCustomName(el.objectName())], g.DATE_STORAGE_FORMAT)
                el.setDate(d)

    def set_mode_new(self):
        self.mode = g.WIN_MODE_NEW
        self.set_elements_editable(True)
        self.set_button_bar(self.but_new)
        self.setWindowTitle(l.new_sample[g.L])
        self.w_name.setPlaceholderText(l.s_edit_name[g.L])
        
    def set_mode_edit(self):
        self.mode = g.WIN_MODE_EDIT
        self.set_elements_editable(True)
        self.set_button_bar(self.but_existing_edit)
        self.setWindowTitle(l.edit_sample[g.L])
        
    def set_mode_view(self):
        self.mode = g.WIN_MODE_VIEW_ONLY
        self.set_elements_editable(False)
        self.set_button_bar(self.but_existing_view)
        self.setWindowTitle(l.view_sample[g.L])
        
    def set_button_bar(self, button):
        for but in self.buts:
            #self.centralWidget().layout().replaceWidget(but, button)
            but.setParent(None)
        self.centralWidget().layout().addWidget(button)

    def set_elements_editable(self, editable):
        for w in self.read_only:
            w.setReadOnly(not editable)
        for w in self.not_enabled:
            w.setEnabled(editable)

    def set_buttons_enabled(self, enabled):
        for but in self.buts:
            but.setEnabled(enabled)

    def start_save_new(self):
        self.set_buttons_enabled(False)
        if self.validate():
            self.path = askSaveAsFileName(                           # open a save file dialog which returns the file object
                filetypes=[(l.filetype_sample_lbl[g.L], g.SAMPLE_FILE_TYPES)],
                defaultextension=g.SAMPLE_EXT,
                confirmoverwrite=True,
                initialfile=guess_filename(self.w_name.text()))
            if not self.path or self.path == '':            # if the user didn't select a path
                return                                      # don't try to save, just return
            self.saveFile()
        else:
            self.set_buttons_enabled(True)
            
    def start_save_existing(self):
        self.set_buttons_enabled(False)
        if self.validate():
            self.saveFile()
        else:
            self.set_buttons_enabled(True)

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
    
    def saveFile(self):
        # Gather all of the data into a dictionary
        lineedits = self.findChildren(QLineEdit)            # grab all line edit objects from form
        dateedits = self.findChildren(QDateEdit)            # grab all date edit objects from form
        textedits = self.findChildren(QPlainTextEdit)            # grab all paragraph text edit objects from form
        newSample = True
        data = self.parent.data
            
        # loop through all line edit elements, saving entered text
        for el in lineedits:
            if isCustomName(el.objectName()):
                data.update({decodeCustomName(el.objectName()): el.text()})

        # loop through all date elements, saving date
        for el in dateedits:
            if isCustomName(el.objectName()):
                data.update({decodeCustomName(el.objectName()): el.date().toString(g.DATE_STORAGE_FORMAT)})

        # loop through all paragraph edit(textedit) elements, saving text
        for el in textedits:
            if isCustomName(el.objectName()):
                data.update({decodeCustomName(el.objectName()): el.toPlainText()})

        if self.mode == g.WIN_MODE_NEW:
            # append current datetime
            data.update({g.S_DATE_ENTERED: QDateTime.currentDateTime().toString(g.DATETIME_STORAGE_FORMAT)})
        
            # append empty arrays for future data
            for key in g.S_BLANK_ARRAYS:
                data.update({key:[]})

        # Do actual save!
        if self.mode == g.WIN_MODE_NEW:                         # iF new sample
            try:
                write_data_to_file(self.path, data)     # do a synchronous save
                self.saved = True
                self.parent.open_sample(self.path)      
                self.close()
            except:
                self.status.showMessage('ERROR: File did not save.', g.SB_DURATION)

        else:
            self.set_mode_view()
            self.status.showMessage('Saving...', g.SB_DURATION)
            try:
                self.parent.start_async_save(g.SAVE_TYPE_SAMPLE, [data], onSuccess=self.after_save_success, onError=self.after_save_error)
            except Exception as e:
                print(e)
                
    def after_save_success(self):
        self.saved = True
        self.status.showMessage('Saved!', g.SB_DURATION)
        self.set_buttons_enabled(True)
        if self.close_on_save:
            self.close()
        
    def after_save_error(self):
        self.status.showMessage('ERROR: File did not save.', g.SB_DURATION)
        self.set_mode_edit()
        self.set_buttons_enabled(True)
            
    
    def closeEvent(self, event):
        """
        This is the handler for all close envents, including those generated by the user
        (eg. the press of the X button) and those generated programatically (eg. a
        'self.close()' statement). The name of this function is dictated by PyQt6's
        specification for event handling.

        Algorithm:
        Checks the self.saved flag.
            If True, the window is closed (all progress has been saved)
            Otherwise (if there is data to save): prompts the user to select:
                - Save: The save routine is called. If it succeeds, window is closed.
                    If it errors, window is not closed.
                - Discard: The window is closed without saving
                - Other (Cancel or the x-button): The close action is blocked"""
        try:
            if self.saved:                      # If all modified content (if any) has been saved
                self.accept_close(event)        # we don't need to ask about saving, so accept the close action
            else:                                                   # if there is unsaved content:                                    
                confirm = saveMessageBox(self)                      #   init a dialog asking the user if they're sure
                resp = confirm.exec()                               #   launch the dialog
                if resp == QMessageBox.StandardButton.Save:         #   if the user selects "Save"
                    event.ignore()                                  #       block the close action
                    if self.mode == g.WIN_MODE_NEW:                 #       if this is a new sample
                        self.start_save_new()                       #           save it as a new sample
                    else:                                           #       otherwise,
                        self.close_on_save = True                   #           tell window to close after saving 
                        self.start_save_existing()                  #           and save it as an existing sample
                elif resp == QMessageBox.StandardButton.Discard:    #   if the user selects "discard"
                    self.accept_close(event)                        #       allow the close action to complete
                else:                                               #   if the user selects "cancel" (or anything else)
                    event.ignore()                                  #       block the close action
        except Exception as e:
            print(e)
                
    def accept_close(self, closeEvent):
        """Take in a close event. Removes the reference to itself in the parent's
        self.children list (so reference can be cleared from memory) and accepts
        the passed event."""
        self.parent.children.remove(self)
        closeEvent.accept()
        
    def update_edited_status(self):
        self.saved = False
                                    
