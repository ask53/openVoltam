# import custom stuff
import ov_globals as g
import ov_lang as l
from ov_functions import *
from PyQt6.QtCore import QProcess
print('loaded globals!')



def err():

    print('stderr:')
    data = process.readAllStandardError()
    stderr = bytes(data).decode("utf8")
    print(stderr)

def out():
    print('stdout')
    data = process.readAllStandardOutput()
    stdout = bytes(data).decode("utf8")
    print(stdout)

process = QProcess()
process.readyReadStandardError.connect(err)
process.readyReadStandardOutput.connect(out)
process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
process.start('python', ['processes/launchLoader.py'])
    



############# If "loaded globals!" appears much before the "loaded welcome..."
# message, create a placeholder window that indicates to user that
# OpenVoltam! is loading.
################################################################

# import other python functions (be as specific as possible to keep filesize down)
from os.path import dirname
from os.path import join as joindir

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from wins.welcome import WindowWelcome
print('loaded welcome window =/')
    
# set the base directory. this lets us find media regardless of where the program is run from
g.BASEDIR = dirname(__file__) # by setting location to joindir(basedir, [relative path from base directory])

# Give this app a unique windows ID (windows only) so icon displays on taskbar
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'cda.potentiostat.openvoltam.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass
try:
    print('sleeping...')
    import time
    time.sleep(3)
    print('awake!')
except Exception as e:
    print(e)

process.write('stop'.encode('utf8'))

# Set the display language
g.L = g.ENG

#
g.APP = QApplication([])                                                      # create a PyQt app
g.APP.setWindowIcon(QIcon(joindir(g.BASEDIR,'external/icons/icon.png')))      # set the display icon for the app



with open(joindir(g.BASEDIR,"external/styles/styles.css"), "r") as file:    # open the stylesheet
    g.STYLES = file.read()
applyStyles()                       # and set it as the app's stylesheet
window = WindowWelcome()            # create a new welcome window object
window.show()                       # show the welcome window (when the app is run)
g.APP.exec()                        # run the app!



