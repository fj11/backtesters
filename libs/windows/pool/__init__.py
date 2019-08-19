# encoding: utf-8
import sys
from io import StringIO
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTextEdit, QPushButton, QToolButton, QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt

class PoolWidget():

    def __init__(self, parent, parent_widget, data=None, text='', file_path=None):
        self.parent = parent
        subWindow = QMdiSubWindow()
        self.sub_window = subWindow
        self.parent_widget = parent_widget
        loader = QUiLoader()
        pool = loader.load('stock_pool.ui', parentWidget=parent_widget)

        setattr(subWindow, "subWindowType", 3)
        setattr(subWindow, "btData", data)
        setattr(subWindow, "btFilePath", file_path)
        subWindow.setWindowTitle(u"股票池 - %s" % text)
        subWindow.setWidget(pool)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

