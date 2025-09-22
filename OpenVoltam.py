import GLOBALS as g
import lang as l
from tkinter.filedialog import asksaveasfile as askSaveAsFile
from re import sub
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QGroupBox,
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QMessageBox
)

class WindowHome(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # set the window parameters
        self.setWindowTitle(l.window_home[g.L])
        
        # define possible popup windows (not modals)
        self.w_edit_sample = WindowEditSample(False)
        self.w_new_config = WindowNewConfig()
        self.ws_view_config = []
        
        # define menu bar
        menu = self.menuBar()

        # add labels for menu bar
        action_new_sample = QAction(l.new_sample[g.L], self)
        action_open_sample = QAction(l.open_sample[g.L], self)
        action_edit_sample = QAction(l.edit_sample[g.L], self)
        action_new_config = QAction(l.new_config[g.L], self)
        action_open_config = QAction(l.open_config[g.L], self)

        # connect menu bar labels with slots 
        action_new_sample.triggered.connect(self.new_sample)
        action_open_sample.triggered.connect(self.open_sample)
        action_edit_sample.triggered.connect(self.edit_sample)
        action_new_config.triggered.connect(self.new_config)
        action_open_config.triggered.connect(self.open_config)

        # Add menu top labels then populate the menus with the above slotted labels
        file_menu = menu.addMenu(l.menu_sample[g.L])
        file_menu.addAction(action_new_sample)
        file_menu.addAction(action_open_sample)
        file_menu.addSeparator()
        file_menu.addAction(action_edit_sample)
        
        file_menu = menu.addMenu(l.menu_config[g.L])
        file_menu.addAction(action_new_config)
        file_menu.addAction(action_open_config)

        file_menu = menu.addMenu(l.menu_run[g.L])

        # create main widget and add 
        self.setCentralWidget(self.homeWidget())

    def homeWidget(self):
        # Create the text intro label
        lbl_about = QLabel(l.info_msg[g.L])
        lbl_about.setWordWrap(True)
        lbl_about.setOpenExternalLinks(True)

        # Create the graphic
        lbl_icon = QLabel()
        lbl_icon.setPixmap(QPixmap("icons/icon_v1.png"))

        # Create all buttons
        but_sample_new = QPushButton(l.new_sample[g.L])
        but_sample_open = QPushButton(l.open_sample[g.L])
        but_config_new = QPushButton(l.new_config[g.L])
        but_config_open = QPushButton(l.open_config[g.L])

        # Connect relevant button signals to functions ("slots")
        but_sample_new.clicked.connect(self.new_sample)
        but_sample_open.clicked.connect(self.open_sample)
        but_config_new.clicked.connect(self.new_config)
        but_config_open.clicked.connect(self.open_config)

        # layout screen into three horizontal layouts grouped together vertically
        layout_pane = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_sample = QHBoxLayout()
        layout_config = QHBoxLayout()
        
        # add icon and intro text message into 1st layout
        layout_top.addWidget(lbl_icon)
        layout_top.addWidget(lbl_about)

        # add sample buttons into 2nd layout, wrap them in groupbox that labels them both
        layout_sample.addWidget(but_sample_new)
        layout_sample.addWidget(but_sample_open)
        groupbox_sample = QGroupBox(l.menu_sample[g.L])
        groupbox_sample.setLayout(layout_sample)

        # add config buttons into 3nd layout, wrap them in groupbox that labels them both
        layout_config.addWidget(but_config_new)
        layout_config.addWidget(but_config_open)
        groupbox_config = QGroupBox(l.menu_config[g.L])
        groupbox_config.setLayout(layout_config)

        # add all three horizontal layouts to the vertical layout
        layout_pane.addLayout(layout_top)
        layout_pane.addWidget(groupbox_sample)
        layout_pane.addWidget(groupbox_config)

        w = QWidget()
        w.setLayout(layout_pane)

        return w

    def sampleWidget(self):
        but_back = QPushButton("Go back...")
        but_back.clicked.connect(self.go_back)

        # Create the text intro label
        lbl_about = QLabel(l.info_msg[g.L])
        lbl_about.setWordWrap(True)
        lbl_about.setOpenExternalLinks(True)

        # Create the graphic
        lbl_icon = QLabel()
        lbl_icon.setPixmap(QPixmap("icons/icon_v1.png"))

        # layout screen into three horizontal layouts grouped together vertically
        layout_pane = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_bot = QHBoxLayout()
        # add icon and intro text message into 1st layout
        layout_top.addWidget(lbl_icon)
        layout_top.addWidget(lbl_about)
        layout_bot.addWidget(but_back)
        # add all three horizontal layouts to the vertical layout
        layout_pane.addLayout(layout_top)
        layout_pane.addLayout(layout_bot)

        w = QWidget()
        w.setLayout(layout_pane)

        return w

    def new_sample(self):
        if (self.w_edit_sample.isHidden()):                 # check if winow is hidden. If so:
            self.w_edit_sample = WindowEditSample(False)    #   Create a new empty edit sample window
            self.w_edit_sample.show()                       #   and show it!
        else:                                               # if window is already showing
            self.w_edit_sample.activateWindow()             #   bring it to front of screen

    def open_sample(self):
        self.setCentralWidget(self.sampleWidget())
        self.showMaximized()
        print("opening a saved sample!")

    def edit_sample(self):
        self.w_edit_sample = WindowEditSample("path")
        self.w_edit_sample.show()

    def new_config(self):
        self.w_new_config.show()

    def open_config(self):
        self.ws_view_config.append(WindowViewConfig())
        self.ws_view_config[-1].show()

    def go_back(self):
        self.setCentralWidget(self.homeWidget())
        self.showNormal()

class WindowEditSample(QMainWindow):
    def __init__(self, path):       # if path, load sample deets, else load empty edit window for new sample
        super().__init__()
        self.path = False
        self.saved = False
        layouts = []
        
        self.w_name = QLineEdit()
        self.w_name.setMaxLength(63)
        self.w_name.setObjectName("edit-sample-name")            # add object name for specific styling

        w_lbl_date_collected = QLabel(l.s_edit_date_c[g.L])
        self.w_date_collected = QDateEdit()
        self.w_date_collected.setDisplayFormat(g.DATE_FORMAT)
        self.w_date_collected.setCalendarPopup(True)
        layouts.append(self.horizontalize([w_lbl_date_collected, self.w_date_collected]))

        w_lbl_loc = QLabel(l.s_edit_loc[g.L])
        self.w_loc = QLineEdit()
        self.w_loc.setMaxLength(63)
        layouts.append(self.horizontalize([w_lbl_loc, self.w_loc]))

        w_lbl_contact = QLabel(l.s_edit_contact[g.L])
        self.w_contact = QLineEdit()
        self.w_contact.setMaxLength(63)
        layouts.append(self.horizontalize([w_lbl_contact, self.w_contact]))

        w_lbl_sampler = QLabel(l.s_edit_sampler[g.L])
        self.w_sampler = QLineEdit()
        self.w_sampler.setMaxLength(63)
        layouts.append(self.horizontalize([w_lbl_sampler, self.w_sampler]))

        w_lbl_notes = QLabel(l.s_edit_notes[g.L])
        self.w_notes = QTextEdit()
        layouts.append(self.horizontalize([w_lbl_notes, self.w_notes]))

        but_save = QPushButton(l.s_edit_save[g.L])
        but_save.clicked.connect(self.startSave)
        but_cancel = QPushButton(l.s_edit_cancel[g.L])
        but_cancel.setObjectName(g.CANCEL_BUTTON)
        but_cancel.clicked.connect(self.close)
        layouts.append(self.horizontalize([but_save, but_cancel]))
        
        
        

        if path:
            self.path = path
            self.w_name.setPlaceholderText("hahahahahahahh")
        else:
            self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.new_sample[g.L])
            self.w_name.setPlaceholderText(l.s_edit_name[g.L])

            
        layout_pane = QVBoxLayout()
        layout_pane.addWidget(self.w_name)
        for layout in layouts:
            layout_pane.addLayout(layout)
        w = QWidget()
        w.setLayout(layout_pane)
        self.setCentralWidget(w)

    def horizontalize(self, widgetlist):
        layout = QHBoxLayout()
        for widget in widgetlist:
            layout.addWidget(widget)
        return layout

    def startSave(self):
        if self.validate():
            self.saveFile()

    def validate(self):
        if len(self.w_name.text()) < g.SAMPLE_NAME_MIN_LENGTH:
            dlg = QMessageBox(self)
            dlg.setWindowTitle(l.alert_header[g.L])
            dlg.setText(l.alert_s_edit_name[g.L])
            dlg.exec()
            return False
        else:
            return True
       
    def saveFile(self):
        filename = self.w_name.text()
        filename = sub('[^A-Za-z0-9" "]+', '', filename)
        filename = ' '.join(filename.split())
        filename = filename.replace(' ', '-')
        file = askSaveAsFile(
            filetypes=[(l.filetype_lbl[g.L], g.FILE_TYPES)],
            defaultextension=g.DEFAULT_EXT,
            confirmoverwrite=True,
            initialfile=filename)
        if file:
            self.saved = True
            print(file.name)
            #################3333 HERE ... ACTUALLY SAVING THE FILE! 




            #######################################################










            
            self.close()
        else:
            print('nop')
        
    def closeEvent(self, event):

        if not self.saved:
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Discard changes?")
            confirm.setText("Are you sure you want to close without saving this sample?")
            confirm.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            resp = confirm.exec()

            if resp == QMessageBox.StandardButton.Save:
                if self.validate():
                    self.saveFile()
                else:
                    event.ignore()
            elif resp == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
class WindowNewConfig(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.new_config_full[g.L])

class WindowViewConfig(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(l.window_home[g.L]+g.HEADER_DIVIDER+l.view_config_full[g.L])
        
        

g.L = g.ENG            #set language
app = QApplication([])
with open("styles.css", "r") as file:
    app.setStyleSheet(file.read())


window = WindowHome()
window.show()
app.exec()
