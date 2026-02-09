# import custom stuff
from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

# import other python functions (be as specific as possible to keep filesize down)
from os.path import dirname
from os.path import join as joindir     #   many seconds depending on caches
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

# set the base directory. this lets us find media regardless of where the program is run from
g.BASEDIR = dirname(__file__) # by setting location to joindir(basedir, [relative path from base directory])

g.APP = QApplication([])                                                        # create a PyQt app
splash = QSplashScreen(QPixmap(joindir(g.BASEDIR,'external/icons/splash.png')))   # create splash screen
splash.show()                                                                   # show splash screen
g.APP.processEvents()

# import slower things
from wins.welcome import WindowWelcome  # this imports entire app including dependencies like matplotlib. can take 

import sys
import time

#time.sleep(2)


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


g.APP.setWindowIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))      # set the display icon for the app

with open(joindir(g.BASEDIR,"external/styles/styles.css"), "r") as file:    # open the stylesheet
    g.STYLES = file.read()
applyStyles()                       # and set it as the app's stylesheet
window = WindowWelcome()            # create a new welcome window object
window.show()                       # show the welcome window (when the app is run)
splash.finish(window)
sys.exit(g.APP.exec())                        # run the app!



