# encoding: utf-8
import sys
from io import StringIO
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTextEdit, QPushButton, QToolButton, QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt
import contextlib
import pandas as pd
import numpy as np
import talib
from src import functions

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class PoolWidget():

    def __init__(self, parent, parent_widget, data=None, text=''):
        self.parent = parent
        subWindow = QMdiSubWindow()
        self.sub_window = subWindow
        self.parent_widget = parent_widget
        loader = QUiLoader()
        pool = loader.load('stock_pool.ui', parentWidget=parent_widget)

        setattr(subWindow, "subWindowType", 3)
        setattr(subWindow, "btData", data)
        setattr(subWindow, "btFilePath", None)
        subWindow.setWindowTitle(u"股票池 - %s" % text)
        subWindow.setWidget(pool)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

