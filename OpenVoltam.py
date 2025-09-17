from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QDialog
)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenVoltam")

        menu = self.menuBar()

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
