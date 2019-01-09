

import os
from PySide2.QtXml import QDomNode
from PySide2.QtWidgets import*
from PySide2.QtUiTools import QUiLoader
import matplotlib; matplotlib.use('Qt5Agg')
os.environ["QT_API"] = "pyside2"
from PySide2.QtWidgets import QFrame
from PySide2 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasQT
from matplotlib.figure import Figure
from matplotlib.style import use
from pylab import mpl
import matplotlib.pyplot as plt

#os.chdir("../ui")

class Pic():

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.label_text = {}
        self.xpos = 0
        self.subplot = False

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('key_press_event', self.on_press)

    def on_motion(self, evt):
        for texts in self.label_text.values():
            for text in texts:
                if text.get_visible():
                    text.set_visible(False)
        if evt.inaxes:
            # mycursor = wx.StockCursor(wx.CURSOR_CROSS)
            # self.canvas.SetCursor(mycursor)
            self.xpos = int(evt.xdata)
            annotations = self.label_text.get(self.xpos, [])
            for annotation in annotations:
                if not annotation.get_visible():             # is entered
                    annotation.set_visible(True)
            self.axes.figure.canvas.draw()

    def on_press(self, evt):
        key = evt.key.lower()
        if key not in ["d", "f"]:
            return
        if key == "f":
            self.xpos += 1
        elif key == "d":
            self.xpos -= 1
        if self.xpos <= 0:
            self.xpos = len(self.label_text.keys())
        elif self.xpos >= len(self.label_text.keys()):
            self.xpos = 0
        for texts in self.label_text.values():
            for text in texts:
                if text.get_visible():
                    text.set_visible(False)
        # mycursor = wx.StockCursor(wx.CURSOR_CROSS)
        # self.canvas.SetCursor(mycursor)
        annotations = self.label_text.get(self.xpos, [])
        for annotation in annotations:
            if not annotation.get_visible():             # is entered
                annotation.set_visible(True)
        self.axes.figure.canvas.draw()

class PicWidget(QWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, data_frame, parent=None, width=5, height=4, dpi=100):

        super(PicWidget, self).__init__(parent)

        self.label_text = {}
        self.data_frame = data_frame

        loader = QUiLoader()
        self.window = loader.load("pic_show.ui")
        l = QtWidgets.QVBoxLayout(self.window)



        sc = Pic(self.window, width=5, height=4, dpi=100)
        self.axes = sc.axes

        self.show_pic()
        print(type(self.window))

        print(type(sc))
        l.addWidget(sc)

        self.setParent(parent)

        self.window.setFocus()

        self.window.show()

    def show_pic(self):

        data_frame = self.data_frame
        cols = list(data_frame.columns)
        index = list(data_frame.index)
        index_name = data_frame.index.name
        for i in range(0, len(index)):
            self.label_text[i] = []
            for j in range(0, len(cols)):
                col_data = float(data_frame.iloc[i, j])
                self.label_text[i].append(self.axes.annotate("%s:%s\n%s:%s" %
                                                             (index_name, index[i], cols[j], col_data), (i, col_data),
                                                             bbox=dict(boxstyle="round", fc="w", ec="k"), visible=False,
                                                             size=0.3 * 36))
                # self.label_text[i, col_data] = self.axes.annotate("%s: %s" % (cols[j], col_data), (i, col_data), visible=False)
        self.axes = data_frame.plot(ax=self.axes, legend=True)
        # self.axes.legend(loc="best")
        # x_label = to_unicode(index_name)
        # x_label = index_name
        self.axes.set_xlabel(index_name)
        self.axes.grid(True)
        self.axes.tick_params(axis='x', labelsize=7)
        # plt.show()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        return

if __name__ == "__main__":
    A = Pic()
