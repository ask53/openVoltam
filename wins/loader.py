# import necessary tools from PyQt6
from PyQt6.QtWidgets import QPushButton, QMainWindow

# Define class for Welcome window
class WindowLoader(QMainWindow):
    def __init__(self):
        super().__init__()
        but = QPushButton('hello, world!')
        self.setCentralWidget(but)



