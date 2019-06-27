# encoding: utf-8

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow
from src import setting
from . import manual_tab, trade_tab, signal_tab

class TradeCenterWidget():

    def __init__(self, parent, parent_widget, config={}):
        self.parent = parent
        config = setting.SETTINGS if not config else config
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        backtest_management = loader.load('backtest_management.ui', parentWidget=parent_widget)
        setattr(subWindow, "subWindowType", 1)
        setattr(subWindow, "btData", config)
        setattr(subWindow, "btFilePath", None)
        manual_tab.ManualSignal(backtest_management, parent, config)
        trade_tab.BackTest(backtest_management, parent, config)
        signal_tab.SemiAutoSignal(backtest_management, parent, config)
        subWindow.setWidget(backtest_management)
        parent.mdi_area.addSubWindow(subWindow)

        subWindow.show()
