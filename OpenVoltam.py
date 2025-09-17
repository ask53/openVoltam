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
    QFrame
)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenVoltam | Welcome")
        self.setMinimumWidth(360)
        
        layout0 = QVBoxLayout()
        layout1 = QHBoxLayout()

        lbl_about = QLabel("Welcome to <a href='https://github.com/ask53/openVoltam'>OpenVoltam</a>!<br>v0.0 | 2025<br><br>An open source project by Caminos de Agua and IO Rodeo")
        lbl_about.setWordWrap(True)
        lbl_about.setOpenExternalLinks(True)

        lbl_icon = QLabel()
        lbl_icon.setPixmap(QPixmap("icons/folder.png"))
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        
        layout1.addWidget(lbl_icon)
        layout1.addWidget(lbl_about)
        
        layout0.addLayout(layout1)
        layout0.addWidget(QPushButton("New sample"))
        layout0.addWidget(QPushButton("Open sample"))
        layout0.addWidget(QPushButton("New run configuration"))
        layout0.addWidget(QPushButton("Open run configuration"))

        widget = QWidget()
        widget.setLayout(layout0)
        self.setCentralWidget(widget)

        '''menu = self.menuBar()

        but_action_new_sample = QAction("New sample", self)
        but_action_new_sample.triggered.connect(self.open_window_new_sample)

        but_action_open_sample = QAction("Open sample", self)
        but_action_open_sample.triggered.connect(self.open_window_open_sample)

        but_action_about = QAction("About", self)
        but_action_about.triggered.connect(self.open_window_about)

        but_action_new_config = QAction("New run configuration", self)
        but_action_new_config.triggered.connect(self.open_window_new_config)

        but_action_open_config = QAction("Open run configuration", self)
        but_action_open_config.triggered.connect(self.open_window_open_sample)

        file_menu = menu.addMenu("&File")
        file_menu.addAction(but_action_new_sample)
        file_menu.addAction(but_action_open_sample)
        file_menu.addSeparator()
        file_menu.addAction(but_action_about)
        
        file_menu = menu.addMenu("&Run configurations")
        file_menu.addAction(but_action_new_config)
        file_menu.addAction(but_action_open_config)
        '''

    def open_window_new_sample(self):
        print("opening window to add a new sample")

    def open_window_open_sample(self):
        print("opening window to open an existing sample")

    def open_window_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("About")
        dlg.exec()

    def open_window_new_config(self):
        print("open window to add a new run configuration")

    def open_window_open_config(self):
        print("open window to view existing configuration")


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
