"""
voltamOGram.py

Shows a voltamogram of passed runs. Gives user the option to
analyze for baselines and peak location/heigh or not.

"""

from external.globals import ov_globals as g
from external.globals import ov_lang as l
from external.globals.ov_functions import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

class VoltamogramPlot(Canvas):
    def __init__(self):
       
        size_mm = g.APP.primaryScreen().physicalSize()
        width_in = size_mm.width() * g.MM2IN
        height_in = size_mm.height() * g.MM2IN

        self.fig = plt.figure(figsize=(width_in/1.75, height_in))
        self.axes = self.fig.add_subplot(111)
            
        super().__init__(self.fig)
            

