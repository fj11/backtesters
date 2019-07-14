# encoding: utf-8

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTabWidget, QAction
from src import setting
from . import manual_tab, trade_tab, signal_tab

class TradeCenterWidget():

    def __init__(self, parent, parent_widget, config={}):
        self.parent = parent
        config = setting.SETTINGS if not config else config
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        backtest_management = loader.load('backtest_management.ui', parentWidget=parent_widget)
        action_delete_order = backtest_management.findChild(QAction, "delete_order")

        delete_backtest_tree_item = backtest_management.findChild(QAction, "action_delete")
        add_option_underlying = backtest_management.findChild(QAction, "action_add_option_underlying")
        add_option_group = backtest_management.findChild(QAction, "action_add_option_group")
        add_option_contract = backtest_management.findChild(QAction, "action_add_option_contract")
        no_support = backtest_management.findChild(QAction, "action_no_support")

        tab_widget = backtest_management.findChild(QTabWidget)
        setattr(subWindow, "subWindowType", 1)
        setattr(subWindow, "btData", config)
        setattr(subWindow, "btFilePath", None)
        manual_tab.ManualSignal(tab_widget.widget(0), parent, config, action_delete_order)
        signal_tab.SemiAutoSignal(tab_widget.widget(1), parent, config, delete_backtest_tree_item, add_option_underlying,
                                  add_option_group, add_option_contract, no_support)
        trade_tab.BackTest(tab_widget.widget(2), parent, config)
        subWindow.setWidget(backtest_management)
        parent.mdi_area.addSubWindow(subWindow)

        subWindow.show()
