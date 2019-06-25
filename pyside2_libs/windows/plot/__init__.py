from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QTreeWidgetItem, \
    QMdiSubWindow, QTableView, \
    QTableWidget, QAction, QComboBox, QLineEdit, \
    QTreeWidget, QSpinBox, QPushButton,\
    QMenu, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, \
    QCalendarWidget, QWidget, QAbstractButton, QAbstractItemView, QCheckBox, QTextEdit
from PySide2.QtCore import Qt
from PySide2 import QtGui

# Make sure that we are using QT5
# matplotlib.use('Qt5Agg')
# os.environ["QT_API"] = "PySide2"
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Plot():

    def __init__(self, data_frame, parent_widget, mdi_area):
        if data_frame.empty:
            return
        self.subplot = False
        self.label_text = {}
        loader = QUiLoader()
        subwindow = loader.load("plot.ui", parentWidget=parent_widget)
        subwindow.setWindowTitle("图形展示")

        pwidget = subwindow.findChild(QWidget)

        canvas = FigureCanvas(Figure())
        canvas.figure.add_subplot(111)
        canvas.axes = canvas.figure.add_subplot(111)

        canvas.mpl_connect('motion_notify_event', lambda event: self.onPlotMotion(event, canvas))
        canvas.mpl_connect('key_press_event', self.onPlotPress)

        cols = list(data_frame.columns)
        index = list(data_frame.index)
        index_name = data_frame.index.name
        for i in range(0, len(index)):
            self.label_text[i] = []
            for j in range(0, len(cols)):
                col_data = float(data_frame.iloc[i, j])
                self.label_text[i].append(canvas.axes.annotate("%s:%s\n%s:%s" %
                                                             (index_name, index[i], cols[j], col_data), (i, col_data),
                                                             bbox=dict(boxstyle="round", fc="w", ec="k"), visible=False,
                                                             size=0.3 * 36))
                # self.label_text[i, col_data] = self.axes.annotate("%s: %s" % (cols[j], col_data), (i, col_data), visible=False)
        axes = data_frame.plot(ax=canvas.axes, legend=True, subplots=self.subplot)
        # self.axes.legend(loc="best")
        # x_label = to_unicode(index_name)
        # x_label = index_name
        axes.set_xlabel(index_name)
        axes.grid(True)
        axes.tick_params(axis='x', labelsize=7)
        toolbar = NavigationToolbar2QT(canvas, pwidget)
        toolbar.update()
        l = QtWidgets.QVBoxLayout(pwidget)
        l.addWidget(toolbar)
        l.addWidget(canvas)
        subwindow.setAttribute(Qt.WA_DeleteOnClose)

        mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def onPlotMotion(self, evt, canvas):
        for texts in self.label_text.values():
            for text in texts:
                if text.get_visible():
                    text.set_visible(False)
        if evt.inaxes:
            mycursor = QtGui.QCursor()
            canvas.setCursor(mycursor)
            #self.canvas.setCursor(mycursor)
            xpos = int(evt.xdata)
            annotations = self.label_text.get(xpos, [])
            for annotation in annotations:
                if not annotation.get_visible():             # is entered
                    annotation.set_visible(True)
            canvas.axes.figure.canvas.draw()

    def onPlotPress(self, evt):
        return