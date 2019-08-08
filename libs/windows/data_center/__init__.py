# encoding: utf-8

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTabWidget, QAction, QPushButton, QTextEdit, QProgressBar
from PySide2.QtCore import Qt
from .stock import Stock
from .query import Query
from .signals import Signals

class DataCenterWidget():

    def __init__(self, parent, parent_widget):
        self.parent = parent
        self.parent_widget = parent_widget
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        data_center = loader.load('data_update.ui', parentWidget=parent_widget)

        self.update_button = data_center.findChild(QPushButton, "update_button")
        self.log_output = data_center.findChild(QTextEdit, "log_output")
        self.progress_bar = data_center.findChild(QProgressBar, "progressBar")

        #
        self.update_button.clicked.connect(lambda :self.onUpdateButton())

        self.signals = Signals(self.log_output, self.progress_bar)
        self.stock = Stock(self)
        subWindow.destroyed.connect(self.stop_update)

        subWindow.setWidget(data_center)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

    def onUpdateButton(self):
        self.progress_bar.reset()
        self.log_output.clear()
        self.update_button.setEnabled(False)

        self.stock.set_enable(True)
        self.stock.finished.connect(self.updated)
        self.stock.start()

    def updated(self):
        try:
            self.update_button.setEnabled(True)
        except:
            return

    def stop_update(self):
        self.stock.set_enable(False)
        if self.stock.local_sql: self.stock.local_sql.close()
        # self.stock.remote_sql.close()


