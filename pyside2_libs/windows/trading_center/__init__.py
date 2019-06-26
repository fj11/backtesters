# encoding: utf-8

import os, pickle, re

import pandas as pd
import numpy as np

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QTreeWidgetItem, \
    QMdiSubWindow, QTableView, \
    QTableWidget, QAction, QComboBox, QLineEdit, \
    QTreeWidget, QSpinBox, QPushButton,\
    QMenu, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, \
    QCalendarWidget, QWidget, QAbstractButton, QAbstractItemView, QCheckBox, QTextEdit, QTabWidget
from PySide2.QtCore import Qt
from PySide2 import QtGui

from src import sql, pandas_mode, setting
from . import manual_tab, trade_tab, signal_tab

class TradeCenterWidget():

    def __init__(self, parent, parent_widget):
        self.parent = parent
        self.config = setting.SETTINGS
        loader = QUiLoader()
        backtest_management = loader.load('backtest_management.ui', parentWidget=parent_widget)

        tabs = backtest_management.findChild(QTabWidget, "tabWidget")

        tabs.currentChanged.connect(
            lambda event: self.onLoadTabs(event))

        manual_tab.ManualSignal(backtest_management, parent)
        trade_tab.BackTest(backtest_management, parent)
        signal_tab.SemiAutoSignal(backtest_management, parent)







        parent.mdi_area.addSubWindow(backtest_management)
        backtest_management.show()

    def onLoadTabs(self, index):
        print(index
              )
        return