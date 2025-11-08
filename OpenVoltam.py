# import custom stuff
import ov_globals as g
import ov_lang as l
from ov_functions import *
from wins.home import WindowHome

# import other python functions (be as specific as possible to keep filesize down)
from os.path import dirname
from os.path import join as joindir
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
    
# set the base directory. this lets us find media regardless of where the program is run from
g.BASEDIR = dirname(__file__) # by setting location to joindir(basedir, [relative path from base directory])

# Give this app a unique windows ID (windows only) so icon displays on taskbar
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'cda.potentiostat.openvoltam.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

# Set the display language
g.L = g.ENG

#
g.APP = QApplication([])                                                      # create a PyQt app
g.APP.setWindowIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))      # set the display icon for the app
with open(joindir(g.BASEDIR,"external/styles/styles.css"), "r") as file:    # open the stylesheet
    g.STYLES = file.read()
applyStyles()                       # and set it as the app's stylesheet
window = WindowHome()               # create a new home window object
window.show()                       # show the home window (when the app is run)
g.APP.exec()                        # run the app!



