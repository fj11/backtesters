
import re
import os
import sys
import wmi
import copy
import uuid
import time
import pickle

import pandas as pd
import numpy as np

from PySide2.QtXml import QDomNode

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QApplication, QMdiArea, QTreeWidgetItem, \
    QMessageBox, QMdiSubWindow, QTableView, QToolBox, QFrame, QListView, \
    QTableWidget, QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
    QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox, QPushButton, QFileDialog,\
    QMenu, QInputDialog, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, \
    QToolBar, QCalendarWidget, QWidget, QAbstractButton, QAbstractItemView, QSlider
from PySide2.QtCore import QFile, QObject, Qt
from PySide2 import QtGui
os.environ["QT_API"] = "pyqt5"

# from PyQt5.uic import loadUi as QUiLoader
# from PyQt5 import QtCore, QtWidgets
# from PyQt5.QtWidgets import QApplication, QMdiArea, QTreeWidgetItem, \
#     QMessageBox, QMdiSubWindow, QTableView, QToolBox, QFrame, QListView, \
#     QTableWidget, QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
#     QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox, QPushButton, QFileDialog,\
#     QMenu, QInputDialog, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, QToolBar, QCalendarWidget, QWidget
# from PyQt5.QtCore import QFile, QObject, Qt
# from PyQt5 import QtGui
#
# os.environ["QT_API"] = "pyside2"

from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure


import talib
from talib import abstract

from src import sql, pandas_mode, setting, tradeCenter

font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14)
os.chdir("ui")

ROOT = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0])))

def get_disk_id():
    import wmi
    M = wmi.WMI()
    return M.Win32_DiskDrive()[0].SerialNumber.strip()

def get_mac_address():
    import uuid
    return uuid.UUID(int = uuid.getnode()).hex[-12:]

def get_uuid():
    return str(uuid.uuid5(uuid.NAMESPACE_OID, str(get_disk_id()))).replace("-", "")

class BT(QObject):

    def __init__(self, ui_file, parent=None):
        super(BT, self).__init__(parent)

        self.tc = None
        self.orders = {}
        self.positions = {}
        self.cashs = {}
        self.label_text = {}
        self.option_filter_dict = {}
        self.subplot = False
        self.filePath = None
        self.config = setting.SETTINGS

        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        self.window.setWindowTitle("回测者")
        #self.window.setWindowIcon("")
        ui_file.close()
        self.window.show()
        self.guid = get_uuid()

        self.loadWidget()
        self.loadShowToolBox()
        self.connectSignal()

    def loadUI(self, file_name, parentWidget=None):
        loader = QUiLoader()
        return loader.load(file_name, parentWidget=parentWidget)

    def loadWidget(self):
        self.mdi_area = self.window.findChild(QMdiArea, "display_mdiArea")
        self.show_contract = self.window.findChild(QToolBox, "show_contract")
        self.option_list = self.window.findChild(QTableView, "option_table_view")
        self.future_list = self.window.findChild(QTableView, "future_table_view")
        self.backtest_tree = self.window.findChild(QTreeWidget, "backtest_tree")
        self.action_function = self.window.findChild(QAction, "actionfunction")
        self.action_signal = self.window.findChild(QAction, "action_signal")
        self.action_msignal = self.window.findChild(QAction, "action_manul_signal")
        self.action_about = self.window.findChild(QAction, "actionabout")
        self.action_account = self.window.findChild(QAction, "actionacounts")
        self.action_backtest = self.window.findChild(QAction, "actionstart_backtest")
        self.action_open_file = self.window.findChild(QAction, "actionopen")
        self.action_save_file = self.window.findChild(QAction, "actionsave")
        self.action_save_as_flie = self.window.findChild(QAction, "actionsave_as")
        self.action_new_file = self.window.findChild(QAction, "actionnew")
        self.add_option_underlying = self.window.findChild(QAction, "action_add_option_underlying")
        self.add_option_group = self.window.findChild(QAction, "action_add_option_group")
        self.add_option_contract = self.window.findChild(QAction, "action_add_option_contract")
        self.delete_backtest_tree_item = self.window.findChild(QAction, "action_delete")
        self.filter = self.window.findChild(QAction, "action_filter")

        self.backtest_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.backtest_tree.topLevelItem(0).setExpanded(True)

    def loadShowToolBox(self):
        for i in range(self.show_contract.count()):
            text = self.show_contract.itemText(i)
            if text == "期权":
                listName = "option_table_view"
            elif text == "期货":
                listName = "future_table_view"
                self.show_contract.setItemEnabled(i, False)
            elif text == "股票":
                listName = "stock_table_view"
                self.show_contract.setItemEnabled(i, False)
            elif text == "基金":
                listName = "fund_table_view"
                self.show_contract.setItemEnabled(i, False)

    def loadTreeView(self):

        for i in range(self.share_tree_view.topLevelItemCount()):
            item = self.share_tree_view.topLevelItem(i)
            if item:
                self._set_tree_items(item)

    def connectSignal(self):

        self.option_list.itemDoubleClicked.connect(self.onOptionListDoubleClicked)
        self.future_list.itemDoubleClicked.connect(self.onFutureListDoubleClicked)
        self.action_function.triggered.connect(self.onActionFunction)
        self.action_signal.triggered.connect(self.onActionSignal)
        self.action_msignal.triggered.connect(self.onActionMSignal)
        self.action_about.triggered.connect(self.about)
        self.action_account.triggered.connect(self.onAccounts)
        self.action_backtest.triggered.connect(self.onBacktest)
        self.action_new_file.triggered.connect(self.onNewFile)
        self.action_open_file.triggered.connect(self.onOpenFile)
        self.action_save_file.triggered.connect(self.onSaveAs)
        self.action_save_as_flie.triggered.connect(self.onSaveAs)
        self.backtest_tree.itemDoubleClicked.connect(self.onBackTestTreeDoubleClicked)
        self.add_option_underlying.triggered.connect(self.onAddOptionUnderlying)
        self.add_option_group.triggered.connect(self.onAddOptionGroup)
        self.add_option_contract.triggered.connect(self.onAddOptionContract)
        self.delete_backtest_tree_item.triggered.connect(self.onDeleteBackTestTreeItem)
        #self.filter.triggered.connect(self.onFilter)
        self.mdi_area.subWindowActivated.connect(self.onSubWindoActivated)

        self.window.findChild(QAction, "display_action").triggered.connect(self.onDisplay)
        self.window.findChild(QAction, "action_roll").triggered.connect(self.onRoll)
        self.window.findChild(QAction, "action_delete_column").triggered.connect(self.onDeleteColumn)

        self._connectBackTestOptionSignal()

    def _connectBackTestOptionSignal(self):

        self.backtest_tree.customContextMenuRequested.connect(self.onBackTestTreeRightClicked)

    def onDeleteColumn(self):
        current_window = self.mdi_area.currentSubWindow()
        table_view = current_window.findChild(QTableView)
        selectedColumns = [selection.column() for selection in table_view.selectionModel().selectedColumns()]
        if not selectedColumns:
            self.messageBox("请选择需要删除的列")
            return
        data = getattr(current_window, "btData")
        columns = list(data.columns)
        for i in selectedColumns:
            column_name = columns[i]
            data.drop(column_name, axis=1, inplace=True)
        self.__display_table(data, current_window)

    def onRoll(self):
        current_window = self.mdi_area.currentSubWindow()
        table_view = current_window.findChild(QTableView)
        selectedColumns = [selection.column() for selection in table_view.selectionModel().selectedColumns()]
        if not selectedColumns:
            self.messageBox("请选择需要滚动的列")
            return
        if len(selectedColumns) > 1:
            self.messageBox("不支持多列数据滚动")
            return
        data = getattr(current_window, "btData")
        hidden_columns = getattr(current_window, "hidden_columns")
        column_index = len(data.index)
        columns = list(data.columns)
        column_name = columns[selectedColumns[0]]
        column = data.iloc[:, selectedColumns]
        roll_widget = self.loadUI("roll.ui", parentWidget=self.window)
        volume = roll_widget.findChild(QSpinBox)
        table = roll_widget.findChild(QTableView)
        slider = roll_widget.findChild(QSlider)
        button_box = roll_widget.findChild(QDialogButtonBox)

        volume.setRange(column_index * -1, column_index)
        mode = pandas_mode.PandasModel(column)
        table.setModel(mode)
        slider.setMinimum(column_index * -1)
        slider.setMaximum(column_index)

        volume.valueChanged.connect(lambda event: self.onRollVolumeValueChanged(event, column, table))
        slider.valueChanged.connect(lambda event: self.onRollSliderValueChanged(event, volume))

        button_box.accepted.connect(lambda: self.onRollAccept(volume, selectedColumns[0], column_name, data, table_view, current_window))
        #button_box.rejected.connect(self.onRollReject)

        roll_widget.show()

        return

    def onRollVolumeValueChanged(self, value, data, table):

        data = data.shift(value)
        mode = pandas_mode.PandasModel(data)
        table.setModel(mode)

    def onRollSliderValueChanged(self, value, volume):
        volume.setValue(value)

    def onRollAccept(self, volume, column_number, column_name, data, table_view, current_window):
        number = volume.value()
        new_column_name = "%s, %s" % (column_name, number)
        data.insert(column_number + 1, new_column_name, data[column_name].shift(number))
        self.__display_table(data, current_window)

    def onSubWindoActivated(self, subWindow):
        if hasattr(subWindow, "btData") and hasattr(subWindow, "btFilePath"):
            self.action_save_file.setEnabled(True)
            self.action_save_as_flie.setEnabled(True)
        else:
            self.action_save_file.setEnabled(False)
            self.action_save_as_flie.setEnabled(False)

    def onBackTestTreeDoubleClicked(self, item, column):

        loader = QUiLoader()
        subWindow = QMdiSubWindow()
        text = item.text(column)
        whats_this = item.whatsThis(column)
        if whats_this == "option":
            bt_type = "backtest_option"
            title = "期权设置"
            load_file = "backtest_option.ui"
            current_node = self.config["options"]
            setattr(subWindow, "btCurrentNode", self.config["options"])
        elif whats_this == "option_underlying":
            title = "标的 %s 的设置" % text
            load_file = "backtest_option_underlying.ui"
            bt_type = "backtest_option_underlying"
            current_node = [i for i in self.config["options"]["underlyings"] if i["name"] == text][0]
            setattr(subWindow, "btCurrentNode", current_node)
        elif whats_this == "option_group":
            title = "期权组 %s 的设置" % text
            load_file = "backtest_option_group.ui"
            bt_type = "backtest_option_group"
            parent_item = item.parent()
            parent_item_text = parent_item.text(0)
            underlying_node = [i for i in self.config["options"]["underlyings"] if i["name"] == parent_item_text][0]
            current_node = [i for i in underlying_node["groups"] if i["name"] == text][0]
            setattr(subWindow, "btCurrentNode", current_node)
        elif whats_this == "option_contract":
            title = "期权合约 %s 的设置" % text
            load_file = "backtest_option_contract.ui"
            bt_type = "backtest_option_contract"
            parent_item = item.parent()
            parent_item_text = parent_item.text(0)
            parent_item_whats_this = parent_item.whatsThis(column)
            if parent_item_whats_this == "option_group":
                grand_parent_item = parent_item.parent()
                grand_parent_item_text = grand_parent_item.text(0)
                underlying_node = [i for i in self.config["options"]["underlyings"] if i["name"] == grand_parent_item_text][0]
                group_node = [i for i in underlying_node["groups"] if i["name"] == parent_item_text][0]
                current_node = [i for i in group_node["contracts"] if i["name"] == text][0]
                setattr(subWindow, "btCurrentNode", current_node)
            elif parent_item_whats_this == "option_underlying":
                underlying_node = [i for i in self.config["options"]["underlyings"] if i["name"] == parent_item_text][0]
                current_node = [i for i in underlying_node["contracts"] if i["name"] == text][0]
                setattr(subWindow, "btCurrentNode", current_node)
        elif whats_this == "strategy":
            title = "策略基本设置"
            load_file = "strategy.ui"
            bt_type = "backtest_strategy"
        else:
            return
        if self._active_backtest_widget(bt_type, title):
            return
        setattr(subWindow, "btType", bt_type)
        setattr(subWindow, "btData", self.config)
        setattr(subWindow, "btFilePath", None)
        setattr(subWindow, "btType", 0)
        sub_window_widget = loader.load(load_file, parentWidget=self.window)
        sub_window_widget.setWindowTitle(title)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWidget(sub_window_widget)
        self.mdi_area.addSubWindow(subWindow)

        #连接各组件信号和展示数据
        if whats_this == "option":
            ratio = sub_window_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(current_node["ratio"]["value"])
            ratio.valueChanged.connect(self.onRatioChanged)
        elif whats_this == "option_underlying":
            ratio = sub_window_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(current_node["ratio"]["value"])
            sub_window_widget.findChild(QSpinBox, "ratio").valueChanged.connect(self.onRatioChanged)

            underlying_list = sub_window_widget.findChild(QComboBox, "underlying_list")
            underlying_list.addItems(current_node["id"]["list"])
            underlying_list.currentIndexChanged.connect(self.onUnderlyingListChanged)
            # underlying_list.setCurrentIndex(0)

            signal_list = sub_window_widget.findChild(QComboBox, "signal_list")
            #signal_list.setCurrentIndex(current_node["signal"]["value"])
            ids = current_node["id"]["list"]
            if ids == []:
                self.messageBox("没有数据")
                return
            _sub_window = self.__getSubWindowByAttribute("btId", ids[0])
            if _sub_window is None:
                self.messageBox("没有找到标的")
                return
            columns = _sub_window.btData.columns
            signal_column = [i for i in columns if i.startswith("signal")]
            current_node["signal"]["list"] = signal_column
            signal_list.addItems(signal_column)
            signal_list.currentIndexChanged.connect(self.onSignalChanged)

            side = sub_window_widget.findChild(QComboBox, "side")
            side.setCurrentIndex(current_node["option_side"]["value"])
            side.currentIndexChanged.connect(self.onOptionSideChanged)

            volume = sub_window_widget.findChild(QSpinBox, "volume")
            volume.setValue(current_node["volume"]["value"])
            volume.valueChanged.connect(self.onVolumeChanged)

        elif whats_this == "option_group":

            ratio = sub_window_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(current_node["ratio"]["value"])
            sub_window_widget.findChild(QSpinBox, "ratio").valueChanged.connect(self.onRatioChanged)

        elif whats_this == "option_contract":
            contract_type = sub_window_widget.findChild(QComboBox, "contract_type")
            contract_type.setCurrentIndex(current_node["option_type"]["value"])
            contract_type.currentIndexChanged.connect(self.onOptionContractTypeChanged)

            option_side = sub_window_widget.findChild(QComboBox, "option_side")
            option_side.setCurrentIndex(current_node["option_side"]["value"])
            option_side.currentIndexChanged.connect(self.onOptionSideChanged)

            close_strategy = sub_window_widget.findChild(QComboBox, "close_strategy")
            close_strategy.setCurrentIndex(current_node["close_method"]["value"])
            close_strategy.currentIndexChanged.connect(self.onCloseMethodChanged)

            change_feq = sub_window_widget.findChild(QComboBox, "change_feq")
            change_feq.setCurrentIndex(current_node["change_feq"]["value"])
            change_feq.currentIndexChanged.connect(self.onChangeFeqChanged)

            move_condition = sub_window_widget.findChild(QComboBox, "move_condition")
            move_condition.setCurrentIndex(current_node["change_condition"]["value"])
            move_condition.currentIndexChanged.connect(self.onChangeConditionChanged)

            interval = sub_window_widget.findChild(QComboBox, "interval")
            interval.setCurrentIndex(current_node["month_interval"]["value"])
            interval.currentIndexChanged.connect(self.onMonthIntervalChanged)

            strike_interval = sub_window_widget.findChild(QComboBox, "strike_interval")
            strike_interval.setCurrentIndex(current_node["strike_interval"]["value"])
            strike_interval.currentIndexChanged.connect(self.onStrikeIntervalChanged)

            smart_match = sub_window_widget.findChild(QComboBox, "smart_match")
            smart_match.setCurrentIndex(current_node["smart_selection"]["value"])
            smart_match.currentIndexChanged.connect(self.onSmartSelectionChanged)

            volume = sub_window_widget.findChild(QSpinBox, "volume")
            volume.setValue(current_node["volume"]["value"])
            volume.valueChanged.connect(self.onVolumeChanged)

            deposit_ratio = sub_window_widget.findChild(QDoubleSpinBox, "deposit_ratio")
            deposit_ratio.setValue(current_node["deposit_coefficient"]["value"])
            deposit_ratio.valueChanged.connect(self.onDepositCoefficient)

            delta = sub_window_widget.findChild(QDoubleSpinBox, "delta")
            delta.setValue(current_node["delta"]["value"])
            delta.valueChanged.connect(self.onDeltaChanged)

            gamma = sub_window_widget.findChild(QDoubleSpinBox, "gamma")
            gamma.setValue(current_node["gamma"]["value"])
            gamma.valueChanged.connect(self.onGammaChanged)

            theta = sub_window_widget.findChild(QDoubleSpinBox, "theta")
            theta.setValue(current_node["theta"]["value"])
            theta.valueChanged.connect(self.onThetaChanged)

            vega = sub_window_widget.findChild(QDoubleSpinBox, "vega")
            vega.setValue(current_node["vega"]["value"])
            vega.valueChanged.connect(self.onVegaChanged)

            rho = sub_window_widget.findChild(QDoubleSpinBox, "rho")
            rho.setValue(current_node["rho"]["value"])
            rho.valueChanged.connect(self.onRhoChanged)

            ivix = sub_window_widget.findChild(QDoubleSpinBox, "ivix")
            ivix.setValue(current_node["ivix"]["value"])
            ivix.valueChanged.connect(self.onIvixChanged)

        elif whats_this == "strategy":
            account_folder = os.path.normpath(os.path.join(ROOT, "accounts"))
            account_files = [os.path.splitext(i)[0] for i in os.listdir(account_folder) if
                             os.path.splitext(i)[-1] == ".bt"]
            account_list = sub_window_widget.findChild(QComboBox, "account")
            account_list.addItems(account_files)
            account_list.currentTextChanged.connect(self.onBackTestRunAccountChanged)

            table_view = sub_window_widget.findChild(QTableWidget)
            self.initBacktestAccountTable(table_view, account_files[0])

        subWindow.show()


    def _active_backtest_widget(self, bt_type, text):

        for i in self.mdi_area.subWindowList():
            if i.btType==bt_type and i.windowTitle() == text:
                self.mdi_area.setActiveSubWindow(i)
                return True

    def onCornerButtonRightClicked(self):
        print(1111)

    def onBackTestTreeRightClicked(self):
        menu = QMenu(self.backtest_tree)
        if self.backtest_tree.currentItem().whatsThis(0) == "option":
            #
            menu.addAction(self.add_option_underlying)
        else:
            whats_this = self.backtest_tree.currentItem().whatsThis(0)
            if whats_this == "option_underlying":
                menu.addAction(self.add_option_group)
                # menu.addAction(self.add_option_contract)
                menu.addAction(self.delete_backtest_tree_item)
            elif whats_this == "option_group":
                menu.addAction(self.add_option_contract)
                menu.addAction(self.delete_backtest_tree_item)
            elif whats_this == "option_contract":
                menu.addAction(self.delete_backtest_tree_item)
            else:
                no_support = self.window.findChild(QAction, "action_no_support")
                menu.addAction(no_support)
        menu.popup(QtGui.QCursor.pos())

    def onOptionContractTypeChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["option_type"]["value"] = index

    def onOptionSideChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["option_side"]["value"] = index

    def onCloseMethodChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["close_method"]["value"] = index

    def onChangeFeqChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["change_feq"]["value"] = index

    def onChangeConditionChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["change_condition"]["value"] = index

    def onMonthIntervalChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["month_interval"]["value"] = index

    def onStrikeIntervalChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["strike_interval"]["value"] = index

    def onSmartSelectionChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["smart_selection"]["value"] = index

    def onDepositCoefficient(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["deposit_coefficient"]["value"] = value

    def onDeltaChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["delta"]["value"] = value

    def onGammaChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["gamma"]["value"] = value

    def onThetaChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["theta"]["value"] = value

    def onVegaChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["vega"]["value"] = value

    def onRhoChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["rho"]["value"] = value

    def onIvixChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["ivix"]["value"] = value

    def onRatioChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["ratio"]["value"] = value

    def onUnderlyingListChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["id"]["value"] = index
        text = current_node["id"]["list"][index]
        signal_list = self.mdi_area.currentSubWindow().findChild(QComboBox, "signal_list")
        signal_list.clear()
        sub_window = self.__getSubWindowByAttribute("btId", text)
        data = sub_window.btData
        signal_list.addItems([i for i in data.columns if i.startswith("signal")])

    def onOptionSideChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["option_side"]["value"] = index

    def onVolumeChanged(self, value):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["volume"]["value"] = value

    def onSignalChanged(self, index):
        current_node = getattr(self.mdi_area.currentSubWindow(), "btCurrentNode")
        current_node["signal"]["value"] = index

    def onDisplay(self):

        widget = self.loadUI("grid_display.ui", parentWidget=self.window)
        widget.setWindowTitle("显示设置")

        button_box = widget.findChild(QDialogButtonBox, "buttonBox")

        hide_button = widget.findChild(QPushButton, "hide")
        show_button = widget.findChild(QPushButton, "show")

        show_list = widget.findChild(QListWidget, "show_list")
        hide_list = widget.findChild(QListWidget, "hide_list")

        sub_window = self.mdi_area.currentSubWindow()
        data = getattr(sub_window, "btData")
        columns = list(data.columns)
        hidden_columns = getattr(sub_window, "hidden_columns")
        show_columns = [i for i in columns if i not in hidden_columns]

        hide_list.addItems(hidden_columns)
        show_list.addItems(show_columns)

        hide_button.clicked.connect(lambda: self.onHideButtonClicked(show_list, hide_list))
        show_button.clicked.connect(lambda: self.onShowButtonClicked(show_list, hide_list))

        button_box.accepted.connect(lambda: self.onGridDisplayAccept(show_list, hide_list, sub_window))
        button_box.rejected.connect(self.onGridDisplayReject)

        widget.show()

    def onGridDisplayAccept(self, show_list, hide_list, sub_window):

        items_text = [hide_list.item(i).text() for i in range(hide_list.count())]

        setattr(sub_window, "hidden_columns", items_text)
        data = getattr(sub_window, "btData")

        self.__display_table(data, sub_window)

        return

    def onGridDisplayReject(self):
        return

    def onHideButtonClicked(self, show_list, hide_list):
        selected_items = show_list.selectedItems()
        selected_items_text = [i.text() for i in selected_items]
        for i in selected_items:
            index = show_list.indexFromItem(i).row()
            show_list.takeItem(index)

        hide_list.addItems(selected_items_text)
        return

    def onShowButtonClicked(self, show_list, hide_list):
        selected_items = hide_list.selectedItems()
        selected_items_text = [i.text() for i in selected_items]
        for i in selected_items:
            index = hide_list.indexFromItem(i).row()
            hide_list.takeItem(index)

        show_list.addItems(selected_items_text)
        return

    def onFilter(self):
        subWindow = self.loadUI("table_filter.ui")

        table_subwindows = [i for i in self.mdi_area.subWindowList() if hasattr(i, "btData") and getattr(i, "btData") is not None]
        table_ids = [getattr(i, "btId") for i in table_subwindows]

        table_list = subWindow.findChild(QComboBox, "table_list")
        table_list.addItems(table_ids)
        table_list.currentIndexChanged.connect(lambda event: self.onFilterTableChanged(event, subWindow, table_subwindows))

        display_list = subWindow.findChild(QListWidget)
        display_list.itemSelectionChanged.connect(lambda: self.onDisplayListItemSelectionChanged(subWindow, table_subwindows))

        columns = subWindow.findChild(QListWidget, "display_list")

        filter_tree = subWindow.findChild(QTreeWidget)

        add_filter = subWindow.findChild(QPushButton, "add_filter")
        delete_filter = subWindow.findChild(QPushButton, "delete_filter")

        filter_tree = subWindow.findChild(QTreeWidget)
        add_filter.clicked.connect(lambda : self.onAddFilter(subWindow, table_subwindows))
        delete_filter.clicked.connect(lambda : self.onDeleteFilter(filter_tree))

        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi_area.addSubWindow(subWindow)
        subWindow.show()
        return

    def onFilterTreeCellEntered(self, filter_tree, table):
        # count = filter_tree.topLevelItemCount()
        # data = getattr(table, "btData")
        # for i in range(count):
        #     item = filter_tree.topLevelItem(i)
        #     column_item = filter_tree.itemWidget(item, 0)
        #
        #     condition_item = filter_tree.itemWidget(item, 1)
        #     value_item = filter_tree.itemWidget(item, 2)
        #
        #     column = column_item.currentText()
        #     condition = condition_item.currentText()
        #     value = value_item.text()
        #
        #     if condition == "大于":
        #         data = data[column > value]
        #     elif condition == "大于且等于":
        #         data = data[column >= value]
        #     elif condition == "小于":
        #         data = data[column < value]
        #     elif condition == "小于且等于":
        #         data = data[column <= value]
        #     elif condition == "等于":
        #         data = data[column == value]
        #         print(data)
        #     elif condition == "包含于":
        #         data = data[column.str.contains(value)]
        #     # elif condition == "不包含于":
        #     #     data = data[column.str.contains(value)]
        #     self.__display_table(data, table)

        return

    def onAddFilter(self, subWindow, table_subwindows):
        filter_tree = subWindow.findChild(QTreeWidget)
        table_list = subWindow.findChild(QComboBox, "table_list")
        index = table_list.currentIndex()
        table = table_subwindows[index]

        data = getattr(table, "btData")
        columns = list(data.columns)

        value_list = QComboBox()
        value_list.addItems(columns)

        condition_list = QComboBox()
        condition_list.addItems(["大于", "大于且等于", "小于", "小于且等于", "等于", "包含于"])

        line_edit = QLineEdit()
        line_edit.textChanged.connect(lambda : self.onFilterTreeCellEntered(filter_tree, table))

        filterItem = QTreeWidgetItem()
        filter_tree.addTopLevelItem(filterItem)

        filter_tree.setItemWidget(filterItem, 0, value_list)
        filter_tree.setItemWidget(filterItem, 1, condition_list)
        filter_tree.setItemWidget(filterItem, 2, line_edit)
        return

    def onDeleteFilter(self, filter_tree):
        current_item = filter_tree.currentItem()
        current_index = filter_tree.indexOfTopLevelItem(current_item)
        filter_tree.takeTopLevelItem(current_index)
        return

    def onFilterTableChanged(self, index, subwindow, tables):
        table = tables[index]
        filter_tree = subwindow.findChild(QTreeWidget)
        filter_tree.clear()

        display_list = subwindow.findChild(QListWidget)
        data = getattr(table, "btData")
        columns = list(data.columns)
        hidden_columns = getattr(table, "hidden_columns")
        if hasattr(table, "btFilter"):
            filter = getattr(table, "btFilter")
        else:
            filter = None
        display_list.clear()

        display_list.addItems(columns)

        for i in range(len(columns)):
            text = columns[i]
            if text not in hidden_columns:
                item = display_list.item(i)
                display_list.setItemSelected(item, True)
        #display_list.itemSelectionChanged.connect(lambda: self.onDisplayListItemSelectionChanged(subwindow, table))

    def onFilterTreeAdded(self):
        return

    def onDisplayListItemSelectionChanged(self, subWindow, tables):

        table_list = subWindow.findChild(QComboBox, "table_list")
        index = table_list.currentIndex()
        table = tables[index]

        display_list = subWindow.findChild(QListWidget)

        items = [display_list.item(i).text() for i in range(display_list.count())]
        display_items = [i.text() for i in display_list.selectedItems()]

        hidden_columns = list(set(items).difference(set(display_items)))
        setattr(table, "hidden_columns", hidden_columns)
        data = getattr(table, "btData")

        self.__display_table(data, table)
        return

    def onDeleteBackTestTreeItem(self):
        current_item = self.backtest_tree.currentItem()
        parent_item = current_item.parent()
        grand_parent_item = parent_item.parent()
        whats_this = current_item.whatsThis(0)
        parent_whats_this = parent_item.whatsThis(0)
        parent_item_text = parent_item.text(0)
        current_item_text = current_item.text(0)

        index = parent_item.indexOfChild(current_item)
        if whats_this == "option_group":
            for underlying in self.config["options"]["underlyings"]:
                if underlying.get("name") == parent_item_text:
                    groups = underlying.get("groups")
                    for group in groups:
                        if group.get("name") == current_item_text:
                            groups.remove(group)
        elif whats_this == "option_contract":
            #两种情况需要处理
            if parent_whats_this == "option_underlying":
                for underlying in self.config["options"]["underlyings"]:
                    if underlying.get("name") == parent_item_text:
                        contracts = underlying.get("contracts")
                        for contract in contracts:
                            if contract.get("name") == current_item_text:
                                contracts.remove(contract)
            elif parent_whats_this == "option_group":
                for underlying in self.config["options"]["underlyings"]:
                    if underlying.get("name") == grand_parent_item.text(0):
                        groups = underlying.get("groups")
                        for group in groups:
                            if group.get("name") == parent_item_text:
                                contracts = group.get("contracts")
                                for contract in contracts:
                                    if contract.get("name") == current_item_text:
                                        contracts.remove(contract)
        elif whats_this == "option_underlying":
            underlyings = self.config["options"]["underlyings"]
            for underlying in underlyings:
                if underlying.get("name") == current_item_text:
                    underlyings.remove(underlying)
        parent_item.takeChild(index)
        return

    def onAddOptionGroup(self):
        text, ok = QInputDialog.getText(self.window, "请输入期权组名称", "名称", QLineEdit.Normal)
        current_item = self.backtest_tree.currentItem()
        # parent_item = current_item.parent()
        current_item_text = current_item.text(0)
        # parent_item_text = parent_item.text(0)
        if ok and text:
            node = QTreeWidgetItem(current_item)
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_group")
            node.setIcon(0, QtGui.QIcon("../icon/group.png"))
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            group_dict = {
                "name": text,
                "enable": 1,
                "contracts": [],
                "signal": {
                    "type": "list",
                    "value": 0,
                    "list": []
                },
                "ratio": {
                    "type": "float",
                    "value": 0,
                },
            }
            for underlying in self.config["options"]["underlyings"]:
                if underlying.get("name") == current_item_text:
                    underlying["groups"].append(group_dict)

    def onAddOptionContract(self):
        text, ok = QInputDialog.getText(self.window, "请输入期权合约名称", "名称", QLineEdit.Normal)
        current_item = self.backtest_tree.currentItem()
        current_item_whats_this = current_item.whatsThis(0)
        current_item_text = current_item.text(0)
        parent_item = current_item.parent()
        parent_whats_this = parent_item.whatsThis(0)
        parent_item_text = parent_item.text(0)
        if ok and text:
            node = QTreeWidgetItem(current_item)
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_contract")
            node.setIcon(0, QtGui.QIcon("../icon/contract.png"))
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            filter_dict = {
                "name": text,
                "enable": 1,
                "open_status": False,
                "ids":[],
                "option_type": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_TYPE,
                },
                "option_side": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_SIDE,
                },
                "close_method": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CLOSE_METHOD,
                },
                "change_feq": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CHANGE_FEQ,
                },
                "change_condition": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CHANGE_CONDITION,
                },
                "month_interval": {
                    "type": "list",
                    "value": 0,
                    "list": [setting.OPTION_INTERVAL[i] for i in range(len(setting.OPTION_INTERVAL)) if i != 2],
                },
                "strike_interval": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_STRIKE_INTERVAL,
                },
                "smart_selection": {
                    "type": "list",
                    "value": 1,
                    "list": setting.OPTION_SMART_SELECTION,
                },
                "type": "option",
                "volume": {
                    "type": "int",
                    "value": 0
                },
                "deposit_coefficient": {
                    "type": "int",
                    "value": 1,
                },
                "delta": {
                    "type": "int",
                    "value": 0,
                },
                "gamma": {
                    "type": "int",
                    "value": 0,
                },
                "theta": {
                    "type": "int",
                    "value": 0,
                },
                "vega": {
                    "type": "int",
                    "value": 0,
                },
                "rho": {
                    "type": "int",
                    "value": 0,
                },
                "ivix": {
                    "type": "float",
                    "value": 0
                }
            }
            for underlying in self.config["options"]["underlyings"]:
                underlying_name = underlying.get("name")
                if current_item_whats_this == "option_group":
                    if underlying_name == parent_item_text:
                        groups = underlying.get("groups")
                        for group in groups:
                            if group.get("name") ==  current_item_text:
                                group["contracts"].append(filter_dict)
                elif current_item_whats_this == "option_underlying":
                    if underlying_name == current_item_text:
                        underlying.get("contracts").append(filter_dict)

    def onAddOptionUnderlying(self):

        text, ok = QInputDialog.getText(self.window, "请输入期权标的名称","名称", QLineEdit.Normal)
        if ok and text:
            node = QTreeWidgetItem(self.backtest_tree.currentItem())
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_underlying")
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            group_dict = {
                "name": text,
                "enable": 0,
                "ratio": {
                    "type": "int",
                    "value": 0,
                },
                "id": {
                    "type": "list",
                    "value": 0,
                    "list": [i.btId for i in self.mdi_area.subWindowList() if i.btType in ["option_underlying", "excel", "csv"]]
                },
                "signal": {
                    "type": "list",
                    "value": 0,
                    "list": []
                },
                "option_side": {
                    "type": "list",
                    "value": 0,
                    "list": [u"买入"]
                },
                "volume": {
                    "type": "int",
                    "value": 0,
                },
                "groups": [],
                "contracts":[],
            }
            self.config["options"]["underlyings"].append(group_dict)

    def onNewFile(self):
        return

    def onOpenFile(self):
        fileName = QFileDialog.getOpenFileName(self.window, "Open BackTest File", "../", "BackTest Files (*.csv *.xls *.xlsx *.bt)")[0]
        file_name, extension = os.path.splitext(fileName)
        if extension == ".csv":
            data = pd.read_csv(fileName)
            self._show_table_sub_window(file_name, data, type="csv", id=file_name)
        elif extension == ".xls" or  extension == ".xlsx":
            data = pd.read_excel(fileName)
            self._show_table_sub_window(file_name, data, type="excel", id=file_name)
        elif extension == "bt":
            data = pickle.load(fileName)

    def onSave(self, type, data, file_path):

        if type == 1:
            writer = pd.ExcelWriter('%s' % file_path)
            data.to_excel(writer, 'BackTest')
            writer.save()
        elif type == 0:
            with open("%s "% file_path, "wb") as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def onSaveAs(self):
        currentSubWindow = self.mdi_area.currentSubWindow()
        data = getattr(currentSubWindow, "btData")
        type = getattr(currentSubWindow, "btType")
        fileName = getattr(currentSubWindow, "btFilePath")
        if fileName is None:
            if type == 0:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../",
                                                   "BackTest Files (*.bt)")[0]
                setattr(currentSubWindow, "btFilePath", fileName)
            elif type == 1:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../",
                                                       "BackTest Files (*.xlsx)")[0]
                setattr(currentSubWindow, "btFilePath", fileName)
        self.onSave(type, data, fileName)
        return

    def about(self):
        QMessageBox.about(self.window, "About Backtester",
                          """<b>Platform Details</b>
                            <p>Copyright &copy; 2018.
                            <p>简易，灵活，全方位回测是我们的目标，
                            将量化及期权平民化，非编程化是我们的宗旨!
                            只要您能想到的，回测者就能帮您实现，
                            不需要您具备编程技巧，不需要您到处搜寻数据，
                            只要动动鼠标，打破一切高门槛的垄断！

                            免责条款：本软件数据来源于公开信息，
                            回测结果仅供投资者分析参考，软件作者
                            不对使用此软件而造成的损失承担任何责任。""")

    def onBacktest(self):
        self._show_backtest_sub_window("开始回测", None, id=0)

    def onBacktestRun(self):
        start_date = self.backtest.findChild(QDateEdit, "start_date").date()
        end_date = self.backtest.findChild(QDateEdit, "end_date").date()
        current_date = start_date
        process_bar = self.backtest.findChild(QProgressBar)
        if start_date >= end_date:
            self.messageBox("开始时间必须小于结束时间")
            return
        days = start_date.daysTo(end_date)
        process_bar.reset()
        process_bar. setRange(0, days)
        count = 1
        while end_date > current_date:
            current_date = current_date.addDays(1)
            current_date_str = current_date.toString("yyyy-MM-dd 00:00:00")
            self.__handleManualOrder(current_date_str)

            process_bar.setValue(count)
            option = self.config["options"]
            if option["enable"] == 1 or option["enable"] == 0:
                underlyings = option["underlyings"]
                for underlying in underlyings:
                    id = underlying["id"]["list"][underlying["id"]["value"]]
                    sub_window = self.__getSubWindowByAttribute("btId", id)
                    data = sub_window.btData
                    row = data[data.date == current_date_str]
                    row = row.T.squeeze()
                    if row.empty:
                        continue
                    if underlying["signal"]["list"] == []:
                        self.messageBox("标的%s没有绑定的信号" % id)
                        return
                    underlying_signal_column = underlying["signal"]["list"][underlying["signal"]["value"]]
                    underlying_signal = int(row[underlying_signal_column])
                    self.__handleOptionUnderlyingTick(id, row, underlying_signal, underlying)
                    groups = underlying["groups"]
                    if groups:
                        table = "option/contract"
                        contract_dataframe = sql.read(table, where="underlying_order_book_id='%s'" % id)
                        for group in groups:
                            group_contract = group["contracts"]
                            for contract in group_contract:
                                self.__handleOptionContractTick(id, row, underlying_signal, contract_dataframe, contract)
            self.updateMarket()
            self.updatePosition(current_date_str)
            self.updateCash(current_date_str)
            self.updatePerformance()
            count += 1
        self.afterRun()
        return

    def afterRun(self):
        result_tree = self.backtest.findChild(QTreeWidget)
        result_tree.clear()

        for text in ["资产", "仓位", "订单"]:
            item = QTreeWidgetItem(result_tree)
            item.setText(0, text)

        position_dataframe = pd.DataFrame()
        positions = self.positions.keys()
        position_item = result_tree.topLevelItem(1)
        for id in positions:
            id_item = QTreeWidgetItem(position_item)
            id_item.setText(0, id)
            for date in self.positions[id].keys():
                date_item = QTreeWidgetItem(id_item)
                date_item.setText(0, date)
                date_item.setWhatsThis(0, "position")
                if position_dataframe.empty:
                    position_dataframe = pd.DataFrame(self.positions[id][date])
                else:
                    position_dataframe = position_dataframe.append(pd.DataFrame(self.positions[id][date]), ignore_index=True, sort=True)

        order_item = result_tree.topLevelItem(2)
        orders = self.orders.keys()
        for order_id in orders:
            id_item = QTreeWidgetItem(order_item)
            id_item.setText(0, order_id)
            for order_date in self.orders[order_id].keys():
                date_item = QTreeWidgetItem(id_item)
                date_item.setText(0, order_date)
                date_item.setWhatsThis(0, "order")

        self.tc.performance.max_drawdown = round(self._get_max_drawdown(self.cashs["nav"]), 2)
        self.backtest.findChild(QLineEdit, "init_capital").setText(str(self.tc.performance.init_capital))
        self.backtest.findChild(QLineEdit, "profit_ratio").setText(str(self.tc.performance.profit_ratio))
        self.backtest.findChild(QLineEdit, "win_count").setText(str(self.tc.performance.win_count))
        self.backtest.findChild(QLineEdit, "lose_count").setText(str(self.tc.performance.lose_count))
        self.backtest.findChild(QLineEdit, "win_ratio").setText(str(self.tc.performance.win_ratio))
        self.backtest.findChild(QLineEdit, "average_win").setText(str(self.tc.performance.average_win))
        self.backtest.findChild(QLineEdit, "average_loss").setText(str(self.tc.performance.average_loss))
        self.backtest.findChild(QLineEdit, "max_draw_down").setText(str(self.tc.performance.max_drawdown))
        self.backtest.findChild(QLineEdit, "win_loss").setText(str(self.tc.performance.win_loss))
        self.backtest.findChild(QLineEdit, "final_capital").setText(str(self.tc.performance.final_capital))
        # self.backtest.findChild(QLineEdit, "performance_indicator").setText(str(performance_indicator))

    def onResultTreeDoubleClicked(self, item, column):
        text = item.text(column)
        whats_this = item.whatsThis(column)
        if text == "资产":
            data = pd.DataFrame(self.cashs)
            self._show_table_sub_window("资产详情", data)
        if whats_this == "position":
            id = item.parent().text(column)
            data = self.positions[id][text]
            data = pd.DataFrame(data)
            self._show_table_sub_window("%s 的仓位详情" % id, data, hidden_columns=["account_id", "short_name"])
        elif whats_this == "order":
            id = item.parent().text(column)
            data = self.orders[id][text][0]
            loader = QUiLoader()
            order_status = loader.load('order_status.ui', parentWidget=self.window)
            order_status.setWindowTitle("订单状态")
            sec_id = order_status.findChild(QLineEdit, "sec_id")
            sec_id.setText(data[0].sec_id)

            order_type = order_status.findChild(QLineEdit, "order_type")
            order_type.setText(str(data[0].order_type))

            position_effect = order_status.findChild(QLineEdit, "position_effect")
            position_effect.setText(str(data[0].position_effect))

            side = order_status.findChild(QLineEdit, "side")
            side.setText(str(data[0].side))

            sending_time = order_status.findChild(QDateEdit, "sending_time")
            sending_time.setDate(QtCore.QDate.fromString(data[0].sending_time, "yyyy-MM-dd"))

            transact_time = order_status.findChild(QDateEdit, "transact_time")
            transact_time.setDate(QtCore.QDate.fromString(data[1].transact_time, "yyyy-MM-dd"))

            price = order_status.findChild(QDoubleSpinBox, "price")
            price.setValue(data[0].price)

            res_price = order_status.findChild(QDoubleSpinBox, "res_price")
            res_price.setValue(data[1].price)

            amount = order_status.findChild(QDoubleSpinBox, "amount")
            amount.setValue(data[1].amount)

            res_volume = order_status.findChild(QSpinBox, "res_volume")
            res_volume.setValue(data[1].volume)

            volume = order_status.findChild(QSpinBox, "volume")
            volume.setValue(data[0].volume)

            subWindow = QMdiSubWindow()
            subWindow.setAttribute(Qt.WA_DeleteOnClose)
            subWindow.setWidget(order_status)
            self.mdi_area.addSubWindow(subWindow)

            order_status.show()

    def display_result(self):
        loader = QUiLoader()
        self.result = loader.load('backtest_result.ui', parentWidget=self.window)
        self.result.setWindowTitle("回测结果")
        self.result.findChild()
        self.result.show()

    def buy_option_underlying(self, id, volume, tick):
        order = setting.Order()
        order.sec_id = id
        order.order_type = "stock"
        order.price = tick.close
        order.volume = volume
        order.position_effect = setting.PositionEffect_Open
        order.side = setting.OrderSide_Bid
        order.sending_time = tick.date
        self.__save_order(order, self.tc.onOptionUnderlyingOrder(order))

    def sell_option_underlying(self, id, volume, tick):
        order = setting.Order()
        order.sec_id = id
        order.order_type = "stock"
        order.price = tick.close
        order.volume = volume
        order.position_effect = setting.PositionEffect_Close
        order.side = setting.OrderSide_Ask
        order.sending_time = tick.date
        self.__save_order(order, self.tc.onOptionUnderlyingOrder(order))

    def __save_order(self, order, response):
        if order.sec_id in self.orders:
            order_id = self.orders[order.sec_id]
            if order.sending_time in order_id:
                order_id[order.sending_time].append((order, response))
            else:
                order_id[order.sending_time] = [(order, response)]
        else:
            self.orders[order.sec_id] = {
                order.sending_time: [(order, response)]
            }

    def buy_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting):
        close_method = option_contract_setting["close_method"]["value"]
        volume = option_contract_setting["volume"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.change_feq = option_contract_tick.change_feq
        order.var_price = option_underlying_tick.open if change_condition == 1 else option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * 1
        order.position_effect = setting.PositionEffect_Open
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Bid
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        order.deposit_coefficient = deposit_coefficient
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            option_contract_setting["ids"] = [order.sec_id]
        self.__save_order(order, response)

    def short_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting):
        close_method = option_contract_setting["close_method"]["value"]
        volume = option_contract_setting["volume"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.change_feq = option_contract_tick.change_feq
        order.var_price = option_underlying_tick.open if change_condition == 1 else option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * -1
        order.position_effect = setting.PositionEffect_Open
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Ask
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        order.deposit_coefficient = deposit_coefficient
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            if "ids" in option_contract_setting:
                option_contract_setting["ids"] = [order.sec_id]
        self.__save_order(order, response)

    def sell_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting):
        close_method = option_contract_setting["close_method"]["value"]
        volume = option_contract_setting["volume"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.var_price = option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * -1
        order.position_effect = setting.PositionEffect_Close
        order.expiration_date = option_contract_tick.maturity_date
        order.close_method = close_method
        order.side = setting.OrderSide_Ask
        order.sending_time = option_underlying_tick.date
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            if "ids" in option_contract_setting:
                option_contract_setting["ids"].remove(order.sec_id)
        self.__save_order(order, response)

    def cover_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting):
        close_method = option_contract_setting["close_method"]["value"]
        volume = option_contract_setting["volume"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.var_price = option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * 1
        order.position_effect = setting.PositionEffect_Close
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Bid
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            option_contract_setting["ids"].remove(order.sec_id)
        self.__save_order(order, response)

    def short(self, volume, tick):
        pass

    def cover(self, volume, tick):
        pass

    def updateMarket(self):
        self.tc.cash.fpnl = 0
        self.tc.cash.nav = self.tc.cash.available

    def updateCash(self, date):
        self.tc.cash.date = date
        for i in self.tc.cash.__dict__.keys():
            if i.startswith("_"):
                continue
            key = self.cashs.get(i, None)
            if key:self.cashs[i].append(self.tc.cash.__dict__[i])
            else:self.cashs[i] = [self.tc.cash.__dict__[i]]

    def updatePosition(self, date):
        for id in self.tc.optionUnderlyingPosition.copy():
            position = self.tc.optionUnderlyingPosition[id]
            table = "option/underlyings/%s" % id
            tick = sql.read(table, select="close", where="date='%s'" % date)
            if tick.empty:
                continue
            close = tick.at[0, "close"]
            self._updateOptionUnderlyingPosition(id, close, date, position)
            if position.volume == 0:
                self.tc.optionUnderlyingPosition.pop(id)
        for id in self.tc.optionContractPosition.copy():
            position = self.tc.optionContractPosition[id]
            table = "option/contracts/%s" % id
            tick = sql.read(table, select="close", where="date='%s'" % date)
            if tick.empty:
                continue
            close = tick.at[0, "close"]
            self._updateOptionContractPosition(id, close, date, position)
            if position.volume == 0:
                self.tc.optionContractPosition.pop(id)

    def _updateOptionContractPosition(self, id, close, date, position):
        position.fpnl = (close * position.volume) - (position.cum_cost)
        position.price = close
        position.date = date
        position.available_today = position.volume
        position.available = position.volume
        position.cum_cost = position.cost + position.deposit_cost + position.commission + position.slide_cost
        self.tc.cash.fpnl += position.fpnl
        self.tc.cash.nav += (position.price * position.volume)

        positions = self.positions.get(id, {})
        _position = positions.get(position.init_time, {})
        for i in position.__dict__.keys():
            key = _position.get(i, None)
            if key:
                _position[i].append(position.__dict__[i])
            else:
                _position[i] = [position.__dict__[i]]
        if position.init_time not in positions:
            if id not in self.positions:
                self.positions[id] = {position.init_time: _position}
            else:
                self.positions[id][position.init_time] = _position

    def _updateOptionUnderlyingPosition(self, id, close, date, position):

        position.fpnl = (close * position.volume) - (position.cum_cost)
        position.price = close
        position.date = date
        position.available_today = position.volume
        position.available = position.volume
        self.tc.cash.fpnl += position.fpnl
        self.tc.cash.nav += (position.price * position.volume)

        positions = self.positions.get(id, {})
        _position = positions.get(position.init_time, {})
        for i in position.__dict__.keys():
            key = _position.get(i, None)
            if key:
                _position[i].append(position.__dict__[i])
            else:
                _position[i] = [position.__dict__[i]]
        if position.init_time not in positions:
            if id not in self.positions:
                self.positions[id] = {position.init_time: _position}
            else:
                self.positions[id][position.init_time] = _position

    def updatePerformance(self):
        self.tc.performance.init_capital = round(self.tc.cash._nav, 2)
        self.tc.performance.final_capital = round(self.tc.cash.nav, 2)
        self.tc.performance.profit_ratio = round((self.tc.performance.final_capital - self.tc.performance.init_capital) / self.tc.performance.init_capital, 2) * 100
        win_count = self.tc.performance.win_count
        lose_count = self.tc.performance.lose_count
        if win_count > 0 or lose_count > 0:
            self.tc.performance.win_ratio = round(win_count / (win_count + lose_count), 2) * 100
            if win_count > 0:
                self.tc.performance.average_win = round(self.tc.performance.total_win / win_count, 2)
            if lose_count > 0:
                self.tc.performance.average_lose = round(self.tc.performance.total_loss / lose_count, 2)
                if self.tc.performance.average_loss:
                    self.tc.performance.win_loss = round(self.tc.performance.average_win / self.tc.performance.average_loss, 2)
        # performance_indicator = profit_ration / self.tc.performance.max_draw_down
        # performance_level = self.get_performance_level(performance_indicator)

    def select_option(self, underlying_tick, option_info, **params):
        options = pd.DataFrame()
        current_date = underlying_tick.date
        info_frame = self.select_option_by_info(underlying_tick, option_info, **params)
        if info_frame.empty:
            return options
        if len(info_frame.index) > 1:
            risk_frame = self.select_option_by_risk(underlying_tick, info_frame, **params)
        else:
            risk_frame = info_frame

        d = risk_frame
        sec_ids = list(d.order_book_id)
        for i in range(len(sec_ids)):
            sec_id = sec_ids[i]
            table = "option/contracts/%s" % sec_id
            data = sql.read(table, where="date='%s'" % current_date)
            data["order_book_id"] = sec_id
            if options.empty:
                options = data
            else:
                options.append(data, ignore_index=True)
        options = options.merge(d, on="order_book_id", how="inner")
        return options

    def select_option_by_info(self, underlying_tick, option_dataframe, **params):

        current_date = underlying_tick.date
        smart_selection = params["smart_selection"].get("value")
        change_condition = params["change_condition"].get("value")
        option_type = params["option_type"].get("value")
        month_interval = params["month_interval"].get("value")
        strike_interval = params["strike_interval"].get("value")
        if change_condition == 0:
            close_price = underlying_tick.close
        else:
            close_price = underlying_tick.open
        strike_interval_string = setting.OPTION_STRIKE_INTERVAL[strike_interval]
        strike_match = re.search(r"\d", strike_interval_string)
        if strike_match:
            strike_symbol_match = re.search(u"高", strike_interval_string)
            if strike_symbol_match:
                strike_interval = int(strike_match.group(0)) * 1
            else:
                strike_interval = int(strike_match.group(0)) * -1
        else:
            strike_interval = 0
        option_dataframe = option_dataframe[option_dataframe.listed_date <= current_date]
        option_dataframe = option_dataframe[option_dataframe.maturity_date > current_date]
        if option_type == 0:
            option_dataframe = option_dataframe[option_dataframe.option_type == "C"]
        elif option_type == 1:
            option_dataframe = option_dataframe[option_dataframe.option_type == "P"]
        if month_interval is not None:
            option_dataframe = option_dataframe.sort_values("maturity_date", axis=0)
            exp_date, group = list(option_dataframe.groupby("maturity_date"))[month_interval]
            option_dataframe = option_dataframe[option_dataframe.maturity_date == exp_date]
        if option_dataframe.empty:
            return pd.DataFrame()
        if strike_interval_string != "":
            option_dataframe = self.__filter_by_interval(option_dataframe, strike_interval, close_price, smart_selection)
        return option_dataframe

    def __filter_by_interval(self, data_frame, strike_interval, close_price, smart_selection):
        d = data_frame
        if strike_interval > 0:
            d = d[d.strike_price > close_price]
            if d.empty and smart_selection:
                return self.__filter_by_interval(data_frame, -1, close_price, smart_selection)
            d = d.sort_values("strike_price", axis=0)
            d.index = [i+1 for i in range(len(d.index))]
            if strike_interval > max(d.index) and smart_selection:
                strike_interval = max(d.index)
            d = d[d.index == abs(strike_interval)]
        elif strike_interval < 0:
            strike_interval = abs(strike_interval)
            d = d[d.strike_price < close_price]
            if d.empty and smart_selection:
                return self.__filter_by_interval(data_frame, 1, close_price, smart_selection)
            d = d.sort_values("strike_price", ascending=False, axis=0)
            d.index = [i+1 for i in range(len(d.index))]
            if strike_interval > max(d.index) and smart_selection:
                strike_interval = max(d.index)
            d = d[d.index == strike_interval]
        else:
            d["close_price_filter"] = np.abs(d.strike_price - float(close_price))
            d = d.sort_values(by="close_price_filter")
            d.index = [i for i in range(len(d.index))]
            d = d[d.index == 0]
        return d

    def select_option_by_risk(self, underlying_tick, option_dataframe, **params):

        optID = None
        current_date = underlying_tick.tradeDate
        delta = params["delta"].get("value")
        gamma = params["gamma"].get("value")
        rho = params["rho"].get("value")
        theta = params["theta"].get("value")
        vega = params["vega"].get("value")
        ivix = params["ivix"].get("value")
        table_name = "/option_risk"
        if not sql.is_table(table_name):
            return pd.DataFrame()
        option_risk_frame = sql.read(table_name)
        option_risk_frame = option_risk_frame[option_risk_frame.tradeDate==current_date]
        if not option_dataframe.empty:
            option_risk_frame = option_risk_frame.loc[:, ["Delta", "Gamma", "Rho", "Theta", "Vega", "optID", "ivix"]]
            option_risk_frame = pd.merge(option_risk_frame, option_dataframe, "optID")
        else:
            option_risk_frame["secID"] = option_risk_frame.ticker + ".XSHG"
        if delta:
            option_risk_frame["delta_filter"] = np.abs(option_risk_frame.Delta - float(delta))
            option_risk_frame = option_risk_frame.sort_values(by="delta_filter")
            optID = list(option_risk_frame.optID)[0]
        if gamma:
            option_risk_frame["gamma_filter"] = np.abs(option_risk_frame.Gamma - float(gamma))
            option_risk_frame = option_risk_frame.sort_values(by="gamma_filter")
            optID = list(option_risk_frame.optID)[0]
        if rho:
            option_risk_frame["rho_filter"] = np.abs(option_risk_frame.Rho - float(rho))
            option_risk_frame = option_risk_frame.sort_values(by="rho_filter")
            optID = list(option_risk_frame.optID)[0]
        if theta:
            option_risk_frame["theta_filter"] = np.abs(option_risk_frame.Theta - float(theta))
            option_risk_frame = option_risk_frame.sort_values(by="theta_filter")
            optID = list(option_risk_frame.optID)[0]
        if vega:
            option_risk_frame["vega_filter"] = np.abs(option_risk_frame.Vega - float(vega))
            option_risk_frame = option_risk_frame.sort_values(by="vega_filter")
            optID = list(option_risk_frame.optID)[0]
        if ivix:
            option_risk_frame["ivix_filter"] = np.abs(option_risk_frame.ivix - float(ivix))
            option_risk_frame = option_risk_frame.sort_values(by="ivix_filter")
            optID = list(option_risk_frame.optID)[0]
        if optID:
            option_risk_frame = option_risk_frame[option_risk_frame.optID == optID]
            return option_risk_frame
        else:
            return option_dataframe

    def __getSubWindowByAttribute(self, key, value):
        for i in self.mdi_area.subWindowList():
            if hasattr(i, key) and getattr(i, key) == value:
                return i
        return None

    def __handleManualOrder(self, date):
        order_tree = self.manual_create_order.findChild(QTreeWidget)
        count = order_tree. topLevelItemCount()
        for index in range(count):
            item = order_tree.topLevelItem(index)
            send_date_text = item.text(0)
            if send_date_text != date:
                continue
            underlying_id_text = item.text(1)
            contract_id_text = item.text(2)
            position_effect_text = item.text(3)
            side_text = item.text(4)
            order_type_text = item.text(5)
            volume = int(item.text(6))

            if order_type_text == "期权标的":
                table = "option/underlyings/%s" % underlying_id_text
                tick = sql.read(table, where="date='%s'" % date)
                tick = tick.T.squeeze()
                if position_effect_text == "开仓" and side_text == "买入":
                    self.buy_option_underlying(underlying_id_text, volume, tick)
                if position_effect_text == "平仓" and side_text == "卖出":
                    self.sell_option_underlying(underlying_id_text, volume, tick)
            elif order_type_text == "期权合约":
                contracts_table = "option/contract"
                contract_table = "option/contracts/%s" % contract_id_text
                underlying_table = "option/underlyings/%s" % underlying_id_text

                contract_tick = sql.read(contract_table, where="date='%s'" % date)
                contract_tick = contract_tick.T.squeeze()

                contracts_tick = sql.read(contracts_table, where="order_book_id='%s'" % contract_id_text)
                contracts_tick = contracts_tick.T.squeeze()

                underlying_tick = sql.read(underlying_table, where="date='%s'" % date)
                underlying_tick = underlying_tick.T.squeeze()

                contract_tick = contract_tick.append(contracts_tick)
                contract_tick.change_feq = ""
                contract_setting = {
                        "close_method":{
                            "value": 0
                        },
                        "volume": {
                            "value":volume
                        },
                        "deposit_coefficient":{
                            "value": 0
                        },
                        "change_condition":{
                            "value": 0
                        }
                        }

                if position_effect_text == "开仓" and side_text == "买入":
                    self.buy_option_contract(underlying_tick, contract_tick, contract_setting)
                if position_effect_text == "平仓" and side_text == "卖出":
                    self.sell_option_contract(underlying_tick, contract_tick, contract_setting)

    def __handleOptionUnderlyingTick(self, id, row, signal, underlying_config):
        volume = underlying_config["volume"]["value"]
        if signal == 1:
            #买入
            self.buy_option_underlying(id, volume, row)
        elif signal == -1:
            #卖出
            self.sell_option_underlying(id, volume, row)

    def __handleOptionContractTick(self, id, tick, signal, option_dataframe, option_contract_setting,
                                   option_group_setting={},
                                   option_underlying_setting={},
                                   option_setting={}):
        # open_type = option_contract_setting["open_type"]["value"]
        # close_type = option_contract_setting["close_type"]["value"]
        option_type = option_contract_setting["option_type"]["value"]
        close_method = option_contract_setting["close_method"]["value"]
        option_side = option_contract_setting["option_side"]["value"]
        option_volume = option_contract_setting["volume"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        change_feq = option_contract_setting["change_feq"]["value"]
        if signal == 1:
            var_price_type = change_condition
            options = self.select_option(tick, option_dataframe, **option_contract_setting)
            for j in options.index:
                option = options.loc[j]
                if not change_feq:
                    change_feq = None
                option_volume = int(option_volume)
                # if open_type == 0:
                #     option_volume = int(option_volume)
                # elif open_type == 1:
                #     if option_side == 0:
                #         option_volume = int((float(option_volume)/(option.closePrice*10000)))
                #     elif option_side == 1:
                #         _option_volume = 0
                #         if option_type == 0:
                #             while self.tc.call_option_cash_deposit(option.strikePrice, tick.closePrice,
                #     option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                #                 _option_volume += 1
                #         elif option_type == 1:
                #             while self.tc.put_option_cash_deposit(option.strikePrice, tick.closePrice,
                #     option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                #                 _option_volume += 1
                #         option_volume = _option_volume - 1
                # elif open_type == 2:
                #     option_ratio = float(option_underlying_setting["ratio"]["value"])/100
                #     option_ratio = option_ratio * (float(option_group_setting["ratio"]["value"])/100)
                #     option_ratio = option_ratio * (float(option_volume)/100)
                #     if option_side == 0:
                #         option_volume = int((option_ratio*self.tc.cash.available/(option.closePrice*10000)))
                #     elif option_side == 1:
                #         _option_volume = 0
                #         option_volume = option_ratio*self.tc.cash.available
                #         if option_type == 0:
                #             while self.tc.call_option_cash_deposit(option.strikePrice, tick.closePrice,
                #     option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                #                 _option_volume += 1
                #         elif option_type == 1:
                #             while self.tc.put_option_cash_deposit(option.strikePrice,
                #     tick.closePrice, option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                #                 _option_volume += 1
                #         option_volume = _option_volume - 1
                option.change_feq = change_feq
                option_contract_setting["volume"]["value"] = option_volume
                if option_side == 0:
                    self.buy_option_contract(tick, option, option_contract_setting)
                elif option_side == 1:
                    self.short_option_contract(tick, option, option_contract_setting)
        elif signal == -1:
            for id in option_contract_setting["ids"]:
                tick_table = "option/contracts/%s" % id
                contract_table = "option/contract"
                contract_dataframe = sql.read(contract_table, where="order_book_id='%s'" % id)
                option_tick = sql.read(tick_table, where="date='%s'" % tick.date)
                option_tick["order_book_id"] = id
                option = contract_dataframe.merge(option_tick, on="order_book_id", how="inner")
                option = option.T.squeeze()
                if option_side == 0:
                    self.sell_option_contract(tick, option, option_contract_setting)
                elif option_side == 1:
                    self.cover_option_contract(tick, option, option_contract_setting)
        elif signal == 0:
            for id in option_contract_setting["ids"]:
                contract_dataframe = option_dataframe[option_dataframe["order_book_id"] == id]
                contract_dataframe = contract_dataframe.T.squeeze()
                if tick.date[:10] == contract_dataframe.maturity_date:

                    tick_table = "option/contracts/%s" % id
                    option_tick = sql.read(tick_table, where="date='%s'" % tick.date)
                    option_tick = option_tick.T.squeeze()
                    option = contract_dataframe.append(option_tick)
                    if close_method == 0:
                        # 按照交易信号平仓，需要换仓
                        if option_side == 0:
                            self.sell_option_contract(tick, option, option_contract_setting)
                        elif option_side == 1:
                            self.cover_option_contract(tick, option, option_contract_setting)
                        options = self.select_option(tick, option_dataframe, **option_contract_setting)
                        for j in options.index:
                            option = options.loc[j]
                            if not change_feq:
                                change_feq = None
                            option.change_feq = change_feq
                            if option_side == 0:
                                self.buy_option_contract(tick, option, option_contract_setting)
                            elif option_side == 1:
                                self.short_option_contract(tick, option, option_contract_setting)
                            #TODO

                    elif close_method == 1:
                        #按到期日平仓，需要检查当前日期是否是到期日
                        #平仓
                        if option_side == 0:
                            self.sell_option_contract(tick, option, option_contract_setting)
                        elif option_side == 1:
                            self.cover_option_contract(tick, option, option_contract_setting)

    def onAccounts(self):
        loader = QUiLoader()
        self.account_management = loader.load('account_management.ui', parentWidget=self.window)
        self.account_management.setWindowTitle("账户")

        self.account_list = self.account_management.findChild(QListWidget)
        self.add_account_button = self.account_management.findChild(QPushButton, "add_account")
        self.delete_account_button = self.account_management.findChild(QPushButton, "delete_account")

        self.add_account_button.clicked.connect(self.onNewAccount)
        self.delete_account_button.clicked.connect(self.onDeleteAccount)
        self.account_list.itemClicked.connect(self.onAccountListClicked)
        account_folder = os.path.normpath(os.path.join(ROOT, "accounts"))
        files = [f for f in os.listdir(account_folder) if os.path.isfile(os.path.normpath(os.path.join(account_folder, f))) and f.endswith("bt")]
        for f in files:
            name, extension = os.path.splitext(f)
            self.account_list.addItem(name)
        self.account_management.show()

    def onAccountListClicked(self, item):
        name = item.text()
        account_folder = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % name))
        with open(account_folder, 'rb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            data = pickle.load(f)

        self.account_name = self.account_management.findChild(QLineEdit, "name")
        self.assert_value = self.account_management.findChild(QDoubleSpinBox, "investment")
        self.commission_rate = self.account_management.findChild(QDoubleSpinBox, "commission_rate")
        self.option_commission_rate = self.account_management.findChild(QDoubleSpinBox, "option_commission_rate")
        self.slide_point = self.account_management.findChild(QDoubleSpinBox, "slide_point")
        self.stop_profit = self.account_management.findChild(QDoubleSpinBox, "stop_profit")
        self.stop_loss = self.account_management.findChild(QDoubleSpinBox, "stop_loss")

        self.assert_value.setValue(data.get("investment"))
        self.commission_rate.setValue(data.get("commission_rate"))
        self.option_commission_rate.setValue(data.get("option_commission_rate"))
        self.slide_point.setValue(data.get("slide_point"))
        self.stop_profit.setValue(data.get("stop_profit"))
        self.stop_loss.setValue(data.get("stop_loss"))
        return

    def onNewAccount(self):

        loader = QUiLoader()
        self.create_account = loader.load('create_account.ui', parentWidget=self.account_management)
        self.create_account.setWindowTitle("账户设置")

        self.account_name = self.create_account.findChild(QLineEdit, "name")

        self.assert_value = self.create_account.findChild(QSpinBox, "assert_value")
        self.assert_value.setValue(setting.ACCOUNT["investment"]["value"])

        self.commission_rate = self.create_account.findChild(QDoubleSpinBox, "commission_rate")
        self.commission_rate.setValue(setting.ACCOUNT["commission_rate"]["value"])

        self.option_commission_rate = self.create_account.findChild(QDoubleSpinBox, "option_commission_rate")
        self.option_commission_rate.setValue(setting.ACCOUNT["option_commission_rate"]["value"])

        self.profit_ratio = self.create_account.findChild(QDoubleSpinBox, "profit_ratio")
        self.profit_ratio.setValue(setting.ACCOUNT["profit_ratio"]["value"])

        self.slide_point = self.create_account.findChild(QSpinBox, "slide_point")
        self.slide_point.setValue(setting.ACCOUNT["slide_point"]["value"])

        self.stop_profit = self.create_account.findChild(QSpinBox, "stop_profit")
        self.stop_profit.setValue(setting.ACCOUNT["stop_profit"]["value"])

        self.stop_loss = self.create_account.findChild(QSpinBox, "stop_loss")
        self.stop_loss.setValue(setting.ACCOUNT["stop_loss"]["value"])

        button_box = self.create_account.findChild(QDialogButtonBox)
        button_box.setEnabled(False)

        button_box.accepted.connect(self.onCreateAccountAccept)
        button_box.rejected.connect(self.onCreateAccountReject)
        self.button_box = button_box
        self.account_name.textEdited.connect(self.onEditAccountName)

        self.create_account.show()

    def onDeleteAccount(self):
        current_item = self.account_list.currentItem()
        if current_item:
            name = current_item.text()
            account_folder = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % name))
            if os.path.isfile(account_folder):
                os.remove(account_folder)
                if not os.path.isfile(account_folder):
                    self.account_list.takeItem(self.account_list.row(current_item))

    def onEditAccountName(self):
        if self.account_name.text().strip():
            self.button_box.setEnabled(True)
        else:
            self.button_box.setEnabled(False)

    def onCreateAccountAccept(self):
        name = self.account_name.text()
        info = {
            "name": name,
            "investment": self.assert_value.value(),
            "commission_rate": self.commission_rate.value(),
            "option_commission_rate":self.option_commission_rate.value(),
            "profit_ratio": self.profit_ratio.value(),
            "slide_point":self.slide_point.value(),
            "stop_profit":self.stop_profit.value(),
            "stop_loss":self.stop_loss.value(),
            "currency": "RMB"
        }
        self.account_list.addItem(name)
        account_folder = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % name))
        with open(account_folder, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(info, f, pickle.HIGHEST_PROTOCOL)
        return

    def onCreateAccountReject(self):
        return

    def onActionSignal(self):
        current_window = self.mdi_area.currentSubWindow()
        if current_window is None:
            self.messageBox("请先打开数据")
            return
        self.data = getattr(current_window, "btData")
        hidden_columns = getattr(current_window, "hidden_columns")
        loader = QUiLoader()
        self.signal = loader.load('signal_dialog.ui', parentWidget=self.window)
        self.signal.setWindowTitle("函数信号")

        self.button_box = self.signal.findChild(QDialogButtonBox, "buttonBox")

        self.open_signal_box = self.signal.findChild(QComboBox, "openbox")
        self.open_signal_list1 = self.signal.findChild(QListWidget, "open_list1")
        self.open_signal_list2 = self.signal.findChild(QListWidget, "open_list2")

        self.close_signal_box = self.signal.findChild(QComboBox, "closebox")
        self.close_signal_list1 = self.signal.findChild(QListWidget, "close_list1")
        self.close_signal_list2 = self.signal.findChild(QListWidget, "close_list2")

        self.button_box.accepted.connect(self.onSignalAccept)
        self.button_box.rejected.connect(self.onSignalReject)

        self.list_items = [i for i in list(self.data.columns) if i not in hidden_columns]
        for item in self.list_items:
            self.open_signal_list1.addItem(item)
            self.close_signal_list1.addItem(item)
            self.open_signal_list2.addItem(item)
            self.close_signal_list2.addItem(item)

        self.signal.show()

    def onActionMSignal(self):

        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        manual_create_order = loader.load('msignal_dialog.ui', parentWidget=self.window)
        self.manual_create_order = manual_create_order
        manual_create_order.setWindowTitle("手动下单")

        order_type = manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = manual_create_order.findChild(QComboBox, "contract_id")
        add_order = manual_create_order.findChild(QPushButton, "add_order")

        self.manual_create_order.findChild(QAction, "delete_order").triggered.connect(self.onDeleteOrder)

        calendar = manual_create_order.findChild(QCalendarWidget)
        order_tree = manual_create_order.findChild(QTreeWidget)

        order_tree.itemClicked.connect(self.onOrderTreeClicked)
        order_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        order_tree.customContextMenuRequested.connect(self.onOrderTreeRightClicked)

        order_type.currentTextChanged.connect(self.onManualSignalOrderTypeChanged)
        order_type.setCurrentIndex(1)

        underlying_id.currentTextChanged.connect(self.onManualSignalUnderlyingIdChanged)
        contract_id.currentTextChanged.connect(self.onManualSignalContractIdChanged)
        calendar.clicked.connect(self.onManualSignalCalendarClicked)

        add_order.clicked.connect(self.onAddOrderClicked)

        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.btType = None
        subWindow.setWidget(manual_create_order)
        self.mdi_area.addSubWindow(subWindow)

        manual_create_order.show()

    def onDeleteOrder(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget)
        item = order_tree.currentItem()
        index = order_tree.indexOfTopLevelItem(item)
        order_tree.takeTopLevelItem(index)

    def onOrderTreeRightClicked(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget)
        delete_order = self.manual_create_order.findChild(QAction, "delete_order")
        if order_tree.currentColumn() > 0:
            menu = QMenu(order_tree)
            menu.addAction(delete_order)
            menu.popup(QtGui.QCursor.pos())

    def onOrderTreeClicked(self, item, column):

        send_date_text = item.text(0)

        underlying_id_text = item.text(1)
        contract_id_text = item.text(2)
        position_effect_text = item.text(3)
        side_text = item.text(4)
        order_type_text = item.text(5)
        volume = item.text(6)

        self.manual_create_order.findChild(QDateEdit, "send_date").setDate(QtCore.QDate.fromString(send_date_text, "yyyy-MM-dd 00:00:00"))
        self.manual_create_order.findChild(QComboBox, "order_type").setCurrentText(order_type_text)
        self.manual_create_order.findChild(QComboBox, "underlying_id").setCurrentText(underlying_id_text)
        if contract_id_text:
            contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
            ids = getattr(contract_id, "ids")
            contract_id.setCurrentIndex(ids.index(contract_id_text))
        self.manual_create_order.findChild(QComboBox, "position_effect").setCurrentText(position_effect_text)
        self.manual_create_order.findChild(QComboBox, "side").setCurrentText(side_text)
        self.manual_create_order.findChild(QSpinBox, "volume").setValue(int(volume))

    def onAddOrderClicked(self):

        send_date = self.manual_create_order.findChild(QDateEdit, "send_date")
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
        position_effect = self.manual_create_order.findChild(QComboBox, "position_effect")
        side = self.manual_create_order.findChild(QComboBox, "side")
        volume = self.manual_create_order.findChild(QSpinBox, "volume")

        order_tree = self.manual_create_order.findChild(QTreeWidget)

        item = QTreeWidgetItem(order_tree)
        item.setText(0, send_date.dateTime().toString("yyyy-MM-dd 00:00:00"))
        item.setText(1, underlying_id.currentText())
        if order_type.currentIndex() == 0:
            if hasattr(contract_id, "ids"):
                ids = getattr(contract_id, "ids")
                contract_symbol_index = contract_id.currentIndex()
                item.setText(2, ids[contract_symbol_index])
        item.setText(3, position_effect.currentText())
        item.setText(4, side.currentText())
        item.setText(5, order_type.currentText())
        item.setText(6, str(volume.value()))

    def onManualSignalOrderTypeChanged(self, text):
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        underlying_id.clear()
        if text == "期权合约":
            underlying_ids = []
            for index in range(self.option_list.rowCount()):
                underlying_ids.append(self.option_list.item(index, 1).text())
            underlying_id.addItems(underlying_ids)
            self.manual_create_order.findChild(QComboBox, "contract_id").setEnabled(True)
        elif text == "期权标的":
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            table = "option/contract"
            data = sql.read(table, where="maturity_date>='%s' AND listed_date <= '%s' " % (date, date))
            ids = [id for id, group in data.groupby(["underlying_order_book_id"])]
            # underlying_ids = []
            # for index in range(self.option_list.rowCount()):
            #     underlying_ids.append(self.option_list.item(index, 1).text())
            self.manual_create_order.findChild(QComboBox, "underlying_id").addItems(ids)
            self.manual_create_order.findChild(QComboBox, "contract_id").setEnabled(False)

    def onManualSignalContractIdChanged(self, text):
        contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
        if not hasattr(contract_id, "ids"):
            return
        ids = getattr(contract_id, "ids")
        if ids == []:
            return
        index = contract_id.currentIndex()
        text = ids[index]
        date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
        table = "option/contracts/%s" % text
        data = sql.read(table, where="date='%s'" % date)
        close_price = data.close
        self.manual_create_order.findChild(QDoubleSpinBox, "close_price").setValue(close_price)

    def onManualSignalUnderlyingIdChanged(self, text):
        if not text:
            return
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        if order_type.currentIndex() == 0:
            contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            contract_id.clear()
            table = "option/contract"
            data = sql.read(table, where="underlying_symbol='%s' AND maturity_date>='%s' AND listed_date <= '%s' " % (text, date, date))
            ids = list(data.order_book_id)
            symbols = list(data.symbol)
            contract_id.addItems(symbols)
            setattr(contract_id, "ids", ids)
        else:
            table = "option/underlyings/%s" % text
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            data = sql.read(table, where="date='%s'" % date)
            close_price = data.close
            self.manual_create_order.findChild(QDoubleSpinBox, "close_price").setValue(close_price)

    def onManualSignalCalendarClicked(self, date):

        date_str = date.toString("yyyy-MM-dd 00:00:00")
        table = "option/underlyings/510050.XSHG"
        tick = sql.read(table, where="date='%s'" % date_str)
        if tick.empty:
            self.messageBox("不是交易日")
            return
        self.manual_create_order.findChild(QDateEdit, "send_date").setDate(date)
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        text = order_type.currentText()
        self.onManualSignalOrderTypeChanged(text)


    def onActionFunction(self):

        current_window = self.mdi_area.currentSubWindow()
        if current_window is None:
            self.messageBox("请先打开数据")
            return
        self.data = getattr(current_window, "btData")
        hidden_columns = getattr(current_window, "hidden_columns")
        data = self.data
        loader = QUiLoader()
        function_ui = loader.load('function_dialog.ui', parentWidget=self.window)
        function_ui.setWindowTitle("函数计算")
        function_tab = function_ui.findChild(QTabWidget, "function_tab")
        input = function_ui.findChild(QLineEdit, "column_name")
        button_box = function_ui.findChild(QDialogButtonBox, "buttonBox")

        input.textEdited.connect(lambda: self.onFunctionInput(function_ui))
        button_box.accepted.connect(lambda: self.onFunctionAccept(function_ui, data))
        button_box.rejected.connect(self.onFunctionReject)

        "lambda event: self.onTableViewColumnDoubleClicked(event, None)"

        function_tab.currentChanged.connect(lambda event: self.onLoadFunctionDialogTab(event, function_ui, data, hidden_columns))
        #self.function_tab.currentChanged.connect(self.onLoadFunctionDialogTab)
        button_box.setEnabled(False)
        self.onLoadFunctionDialogTab(0, function_ui, data, hidden_columns)
        function_ui.show()

    def onLoadFunctionDialogTab(self, index, function_ui, data, hidden_columns):
        if index == 0:
            self.cal_list1 = function_ui.findChild(QListWidget, "cal_list1")
            self.cal_list2 = function_ui.findChild(QListWidget, "cal_list2")
            self.function_box = function_ui.findChild(QComboBox, "function_box")
            self.list_items = [i for i in list(data.columns) if i not in hidden_columns]
            self.cal_list1.clear()
            self.cal_list2.clear()
            for item in self.list_items:
                self.cal_list1.addItem(item)
            for item in self.list_items:
                self.cal_list2.addItem(item)
            self.function_box.currentIndexChanged.connect(self.onFunctionCalculateBox)
        elif index == 1:
            self.rel_list1 = function_ui.findChild(QListWidget, "rel_list1")
            self.rel_list2 = function_ui.findChild(QListWidget, "rel_list2")
            self.function_box = function_ui.findChild(QComboBox, "rel_box")
            self.list_items = [i for i in list(data.columns) if i not in hidden_columns]
            self.rel_list1.clear()
            self.rel_list2.clear()
            for item in self.list_items:
                self.rel_list1.addItem(item)
            for item in self.list_items:
                self.rel_list2.addItem(item)
            self.function_box.currentIndexChanged.connect(self.onFunctionCalculateBox)
        elif index == 2:
            self.search_tec_function = function_ui.findChild(QLineEdit, "search_input")
            self.tec_tree = function_ui.findChild(QTreeWidget, "tec_tree")
            talib_groups = talib.get_function_groups()

            for key in talib_groups.keys():
                node = QTreeWidgetItem(self.tec_tree)
                node.setText(0, key)
                for value in talib_groups[key]:
                    sub_node = QTreeWidgetItem(node)
                    sub_node.setText(0, value)

            self.tec_tree.itemClicked.connect(lambda event1, event2: self.onFunctionTecTree(event1, event2, function_ui))
            #self.search_tec_function.textEdited.connect(self.onFunctionInput)

    def onTecFunctionSearched(self):
        text = self.search_tec_function.text().strip()

    def onFunctionTecTree(self, item, column, function_ui):
        group_box = function_ui.findChild(QGroupBox, "parameter_box")
        labels = group_box.findChildren(QLabel)
        spin_boxs = group_box.findChildren(QSpinBox)
        for label in labels:
            label.close()
        for spin_box in spin_boxs:
            spin_box.close()
        text = item.text(column)

        if text in talib.get_function_groups().keys():
            return
        indicator = abstract.Function(text.lower())
        params_dict = indicator.get_parameters()
        keys = params_dict.keys()
        locator = 20
        num = 0
        paras_locators = [locator + i * 30 for i in range(len(keys))]
        for key in keys:
            p = paras_locators[num]
            value = params_dict[key]
            label = QLabel(group_box)
            label.setText(key)
            label.setGeometry(10, p, 100, 20)
            spin_box = QSpinBox(group_box)
            spin_box.setGeometry(100, p, 50, 20)
            spin_box.setObjectName(text)
            spin_box.setWhatsThis(key)
            spin_box.setValue(value)
            label.show()
            spin_box.show()
            num += 1

    def onFunctionInput(self, function_ui):
        input = function_ui.findChild(QLineEdit, "column_name")
        button_box = function_ui.findChild(QDialogButtonBox, "buttonBox")
        if input.text().strip():
            button_box.setEnabled(True)
        else:
            button_box.setEnabled(False)

    def onFunctionCalculateBox(self, index):
        self.cal_list2.clear()
        if index <= 4:
            for item in self.list_items:
                self.cal_list2.addItem(item)

    def onFunctionAccept(self, function_ui, data):
        df = []
        function_tab = function_ui.findChild(QTabWidget, "function_tab")
        input = function_ui.findChild(QLineEdit, "column_name")
        column_name = input.text()
        current_tab_index = function_tab.currentIndex()

        text = self.function_box.currentText()
        if current_tab_index == 0:
            list1_row_text = self.cal_list1.currentItem().text()
            list2_row_text = self.cal_list2.currentItem().text()
            col1 = data.loc[:, list1_row_text]
            col2 = data.loc[:, list2_row_text]
            if text == u"求和":
                df = col1 + col2
            elif text == u"求差":
                df = col1 - col2
            elif text == u"求积":
                df = col1 * col2
            elif text == u"求商":
                df = col1 / col2
            elif text == u"求幂":
                df = np.power(col1, col2)
            elif text == u"正弦":
                df = np.sin(col2)
            elif text == u"余弦":
                df = np.cos(col2)
            elif text == u"正切":
                df = np.tan(col2)
            elif text == u"反正弦":
                df = np.arcsin(col2)
            elif text == u"反余弦":
                df = np.arccos(col2)
            elif text == u"反正切":
                df = np.arctan(col2)
            elif text == u"指数":
                df = np.exp(col2)
            elif text == u"开平方":
                df = np.sqrt(col2)
            data[column_name] = df
        elif current_tab_index == 1:
            list1_row_text = self.cal_list1.currentItem().text()
            list2_row_text = self.cal_list2.currentItem().text()
            col1 = data.loc[:, list1_row_text]
            col2 = data.loc[:, list2_row_text]
            if text == u"上穿":
                try:
                    relation_signal = np.where((col1 > col2) & (col1.shift() < col2.shift()), 1, 0)
                except:
                    self.messageBox(u"当前数据不支持上穿")
                    return False
            elif text == u"下穿":
                try:
                    relation_signal = np.where((col1 < col2) & (col1.shift() > col2.shift()), 1, 0)
                except:
                    self.messageBox(u"当前数据不支持下穿")
                    return False
            elif text == u"大于":
                relation_signal = np.where((col1 > col2), 1, 0)
            elif text == u"大于或等于":
                relation_signal = np.where((col1 >= col2), 1, 0)
            elif text == u"小于":
                relation_signal = np.where((col1 < col2), 1, 0)
            elif text == u"小于或等于":
                relation_signal = np.where((col1 <= col2), 1, 0)
            elif text == u"等于":
                relation_signal = np.where((col1 == col2), 1, 0)
            elif text == u"或" :
                relation_signal = np.where((col1 | col2), 1, 0)
            elif text == u"且":
                relation_signal = np.where((col1 & col2), 1, 0)
            elif text == u"非":
                relation_signal = np.where((col2 ^ 1), 1, 0)
            else:
                relation_signal = 0
            data[column_name] = relation_signal
        elif current_tab_index == 2:
            function_name = self.tec_tree.currentItem().text(0)

            if function_name in talib.get_function_groups().keys():
                #self.messageBox("请选择正确的函数后再试")
                return
            tech_indicator = talib.abstract.Function(function_name.lower())
            output_names = tech_indicator.output_names
            group_box = function_ui.findChild(QGroupBox, "parameter_box")
            spin_boxs = group_box.findChildren(QSpinBox)

            data_arrays = {"close": data.get("close", []),
                           "open": data.get("open", []),
                           "high": data.get("high", []),
                           "low": data.get("low", []),
                           "volume": data.get("volume", [])}
            tech_indicator.set_input_arrays(data_arrays)

            parameters = {}

            for spin_box in spin_boxs:

                name = spin_box.objectName()
                if name == function_name:
                    param_key = spin_box.whatsThis()
                    param_value = spin_box.value()
                    parameters.update({param_key:param_value})
            tech_indicator.set_parameters(parameters)
            data_frame = tech_indicator.run()
            if len(output_names) == 1:
                data[column_name] = data_frame
            else:
                for i in range(len(output_names)):
                    output_name = output_names[i]
                    data[output_name] = data_frame[i]

        self.__display_table(data)

    def onFunctionReject(self):
        delattr(self, "cal_list1")
        delattr(self, "cal_list2")
        delattr(self, "list_items")
        delattr(self, "data")
        delattr(self, "function_box")
        delattr(self, "button_box")

    def onSignalAccept(self):

        open_signal_text = self.open_signal_box.currentText()
        open_list1_row_number = self.open_signal_list1.currentRow()
        open_list2_row_number = self.open_signal_list2.currentRow()
        if open_list1_row_number >= 0 and open_list2_row_number >= 0:
            open_col1 = self.data.loc[:, self.data.columns[open_list1_row_number]]
            open_col2 = self.data.loc[:, self.data.columns[open_list2_row_number]]
            open_signal = self.__calculate_signal(open_signal_text, open_col1, open_col2, 1)
        else:
            open_signal = 0

        close_signal_text = self.close_signal_box.currentText()
        close_list1_row_number = self.close_signal_list1.currentRow()
        close_list2_row_number = self.close_signal_list2.currentRow()
        if close_list1_row_number >= 0 and close_list2_row_number >= 0:
            close_col1 = self.data.loc[:, self.data.columns[close_list1_row_number]]
            close_col2 = self.data.loc[:, self.data.columns[close_list2_row_number]]
            close_signal = self.__calculate_signal(close_signal_text, close_col1, close_col2, -1)
        else:
            close_signal = 0
        signal = open_signal|close_signal
        if "signal" in self.data.columns:
            signal = self.data["signal"]|signal

        for i in range(len(signal)-1, -1, -1):
            n = signal[i]
            if n == 1:
                signal[i] = 0
                break
            elif n == -1:
                break

        self.data["signal"] = signal
        self.__display_table(self.data)
        return

    def onSignalReject(self):
        return

    def onActionIndicator(self):
        print(2222222222)

    def onTableViewColumnClicked(self, index, table_view):
        # up = self.window.findChild(QAction, "action_up")
        # down = self.window.findChild(QAction, "action_down")
        roll = self.window.findChild(QAction, "action_roll")
        delete = self.window.findChild(QAction, "action_delete_column")

        menu = QMenu(table_view)
        menu.addAction(roll)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        return

    def onTableViewRowDoubleClicked(self, index):
        childSubWindow = getattr(self.mdi_area.currentSubWindow(), "childSubWindow")
        if not childSubWindow:
            return
        data = getattr(self.mdi_area.currentSubWindow(), "btData")
        id = getattr(self.mdi_area.currentSubWindow(), "btId")
        title = childSubWindow.get("title")
        type = childSubWindow.get("type")
        tableName = childSubWindow.get("table_name")
        where = childSubWindow.get("where")
        select = childSubWindow.get("select", "*")
        hidden_columns = childSubWindow.get("hidden_columns")
        index_column = childSubWindow.get("index_column")
        csw = childSubWindow.get("childSubWindow")
        has_column_name = re.search("%(\S*)%", tableName)
        if has_column_name:
            column_name = has_column_name.group(1)
            column_value = data.iloc[index,:]
            column_value = column_value[column_name]
            tableName = re.sub("%\S*%", column_value, column_value)
        if type == "option_underlying_table":
            self._get_option_underlying_data(column_value, column_value)
        elif type == "option_contract_table":
            self._get_option_contract_by_date(id, tableName)
        elif type == "future_contract_table":
            self._get_future_contract_data(column_value, column_value)

        return

    def onTableViewColumnDoubleClicked(self, index, evt):
        currentSubWindow = self.mdi_area.currentSubWindow()
        tableView = currentSubWindow.findChild(QTableView)
        selectedColumns = [selection.column() for selection in tableView.selectionModel().selectedColumns()]
        btData = getattr(currentSubWindow, "btData")
        selectedData = btData.iloc[:, selectedColumns]
        self._show_plot_sub_window(selectedData)
        # # plt.figure()
        # try:
        #     ax = selectedData.plot(title="走势图")
        #     labels = ax.get_xticklabels() + ax.legend().texts + [ax.title]
        #     for label in labels:
        #         label.set_fontproperties(font)
        #     plt.show()
        # except Exception as err:
        #     self.messageBox("{0}".format(err))
        # loader = QUiLoader()
        # loader.registerCustomWidget(bt_plot.Pic)
        # circle = loader.load('pic_show.ui')
        # circle.show()
        return

    def onTableViewCellDoubleClicked(self, index):
        return

    def onOptionListDoubleClicked(self):
        row = self.option_list.currentRow()
        name = self.option_list.item(row, 0).text()
        id = self.option_list.item(row, 1).text()
        type = self.option_list.item(row, 2).text()
        if type == "指数":
            self._get_option_underlying_data(name, id)
        elif type == "期货":
            self._get_option_contract(name, id)

    def onFutureListDoubleClicked(self):
        row = self.future_list.currentRow()
        name = self.future_list.item(row, 0).text()
        id = self.future_list.item(row, 1).text()
        self._get_future_contract(name, id)

    def initBacktestAccountTable(self, widget, filename):
        file_name = os.path.normpath(   os.path.join(ROOT, "accounts", "%s.bt" % filename))
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.config["account"] = data
            table_widget = widget
            table_widget.setRowCount(len(data.keys())-1)
            i = 0
            for key in data.keys():
                if key == "name":
                    continue
                value = data[key]
                key_item = QTableWidgetItem(key)
                value_item = QTableWidgetItem(str(value))
                table_widget.setItem(i, 0, key_item)
                table_widget.setItem(i, 1, value_item)
                i += 1

    def onBacktestRunAccountChanged2(self, value):
        file_name = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % value))
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.config["account"] = data
            self.tc = tradeCenter.TradeCenter(data)

    def onBackTestRunAccountChanged(self, value):
        file_name = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % value))
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.config["account"] = data
            table_widget = self.mdi_area.currentSubWindow().findChild(QTableWidget)
            table_widget.setRowCount(len(data.keys())-1)
            i = 0
            for key in data.keys():
                if key == "name":
                    continue
                value = data[key]
                key_item = QTableWidgetItem(key)
                value_item = QTableWidgetItem(str(value))
                table_widget.setItem(i, 0, key_item)
                table_widget.setItem(i, 1, value_item)
                i += 1
            # item = QTableWidgetItem(username)
            # item = (username)

    def messageBox(self, messgae):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("提示")
        msgBox.setText(messgae)
        msgBox.exec_()

    def _set_tool_box_items(self, text, widget):
        return

    def _get_option_underlying_data(self, name, id):
        table = "option/underlyings/%s" % id
        childSubWindow = {
            "title": "%s的当日合约",
            "type": "option_contract_table",
            "table_name": "%date%",
            "where":"",
            "select": id,
            "hidden_columns": [],
            "index_column": [],
            "childSubWindow": {},
        }
        hidden_columns = ['total_turnover',
                          'limit_up',
                          'limit_down',
                          'settlement',
                          'prev_settlement',
                          'discount_rate',
                          'acc_net_value',
                          'unit_net_value',
                          'date',
                          'open_interest'
                          ]
        if id == "510050.XSHG":
            where = "date > '2015-02-08 00:00:00'"
        else:
            where = None
        if where:
            data = sql.read(table, where=where)
        else:
            data = sql.read(table)
        self._show_table_sub_window(name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    index_column='date',
                                    childSubWindow=childSubWindow,
                                    type="option_underlying"
                                    )

    def _get_future_contract(self, name, id):
        table = "future/contract"
        data = sql.read(table, where="underlying_symbol='%s' AND symbol LIKE '%%主力连续'" % id)
        hidden_columns = [
            'index',
            'contract_multiplier',
            'de_listed_date',
            'exchange',
            'listed_date',
            'margin_rate',
            'market_tplus',
            'maturity_date',
            'order_book_id',
            'round_lot',
            'trading_hours',
            'underlying_order_book_id',
                          ]
        data.dropna(axis=0, how='any', inplace=True)
        #data.drop_duplicates("underlying_order_book_id", inplace=True)
        data.index = [i for i in range(int(len(data.index)))]
        self._show_table_sub_window(name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    childSubWindow={
                                        "title": id,
                                        "type": "future_contract_table",
                                        "table_name": "future/contracts/%order_book_id%",
                                        "hidden_columns": ['total_turnover',
                                                           'limit_up',
                                                           'limit_down',
                                                           'settlement',
                                                           'prev_settlement',
                                                           'discount_rate',
                                                           'acc_net_value',
                                                           'unit_net_value',
                                                           'date',
                                                           'open_interest'],
                                        "index_column": "date",
                                    })
        return

    def _get_option_contract(self, name, id):
        table = "option/contract"
        data = sql.read(table, where="underlying_symbol='%s'" % id)
        hidden_columns = ['index',
                          'contract_multiplier',
                          'de_listed_date',
                          'exchange',
                          'exercise_type',
                          'listed_date',
                          'market_tplus',
                          'maturity_date',
                          'option_type',
                          'order_book_id',
                          'round_lot',
                          'strike_price',
                          'symbol',
                          'trading_hours'
                          ]
        data.dropna(axis=0, how='any', inplace=True)
        data.drop_duplicates("underlying_order_book_id", inplace=True)
        data.index = [i for i in range(int(len(data.index)))]
        self._show_table_sub_window(name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    childSubWindow={
                                        "title":id,
                                        "type":"option_underlying_table",
                                        "table_name": "option/underlyings/%underlying_order_book_id%",
                                        "hidden_columns": ['total_turnover',
                                                           'limit_up',
                                                           'limit_down',
                                                           'settlement',
                                                           'prev_settlement',
                                                           'discount_rate',
                                                           'acc_net_value',
                                                           'unit_net_value',
                                                           'date',
                                                           'open_interest'],
                                        "index_column":"date",
                                    })

    def _get_option_contract_by_date(self, underlying_symbol, date):
        showData = pd.DataFrame()
        data = sql.read("option/contract", where="maturity_date>='%s' AND listed_date <= '%s' AND underlying_order_book_id='%s'" % (date, date, underlying_symbol))
        for index, row in data.iterrows():
            order_book_id = row.order_book_id
            symbol = row.symbol
            table = "option/contracts/%s" % order_book_id
            if sql.is_table(table):
                dataRow = sql.read(table, where="date='%s'" % date)
                dataRow["symbol"] = symbol
                showData = showData.append(dataRow, ignore_index=True, sort=True)
        self._show_table_sub_window("标的%s在%s日的期权全部合约" % (underlying_symbol, date), showData, index_column="symbol", hidden_columns=["symbol"], id=1)

    def _get_future_contract_data(self, name, id):
        table = "future/contracts/%s" % id
        childSubWindow = {
            "title": "%s的当日合约",
            "type": "future_contract_data_table",
            "table_name": "%date%",
            "where": "",
            "select": id,
            "hidden_columns": [],
            "index_column": [],
            "childSubWindow": {},
        }
        hidden_columns = ['total_turnover',
                          'limit_up',
                          'limit_down',
                          'settlement',
                          'prev_settlement',
                          'discount_rate',
                          'acc_net_value',
                          'unit_net_value',
                          'date',
                          'open_interest'
                          ]
        data = sql.read(table)
        self._show_table_sub_window(name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    index_column='date',
                                    childSubWindow=childSubWindow,
                                    type="option_underlying"
                                    )

    def _show_list_sub_window(self, title, data):
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        listView = QListWidget()
        listView.setWindowTitle(title)
        listView.addItems(data)
        subWindow = QMdiSubWindow()
        subWindow.btData = data
        subWindow.setWidget(listView)
        self.mdi_area.addSubWindow(subWindow)
        subWindow.show()

    def _show_backtest_sub_window(self, title, data, id=0, type=0):
        subWindow = QMdiSubWindow()
        setattr(subWindow, "btType", type)
        setattr(subWindow, "btId", id)
        setattr(subWindow, "btData", data)
        setattr(subWindow, "btFilePath", None)

        loader = QUiLoader()
        backtest = loader.load('backtest_run.ui', parentWidget=self.window)
        backtest.setWindowTitle(title)
        result_tree = backtest.findChild(QTreeWidget)
        result_tree.itemDoubleClicked.connect(self.onResultTreeDoubleClicked)

        select_account = backtest.findChild(QComboBox, "account")
        account_folder = os.path.normpath(os.path.join(ROOT, "accounts"))
        account_files = [os.path.splitext(i)[0] for i in os.listdir(account_folder) if
                         os.path.splitext(i)[-1] == ".bt"]
        select_account.addItems(account_files)
        select_account.currentTextChanged.connect(self.onBacktestRunAccountChanged2)
        select_account.setCurrentIndex(0)
        file_name = os.path.normpath(os.path.join(ROOT, "accounts", "%s.bt" % account_files[0]))
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.config["account"] = data
            self.tc = tradeCenter.TradeCenter(data)

        start_button = backtest.findChild(QPushButton)
        start_button.clicked.connect(self.onBacktestRun)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWidget(backtest)
        self.mdi_area.addSubWindow(subWindow)
        subWindow.show()
        self.backtest = backtest

        # if account:
        #     subWindow.show()
        #     self.backtest = backtest
        #     self.tc = tradeCenter.TradeCenter(account)
        # else:
        #     self.messageBox("请先设置测试账户后再打开")

    def _show_table_sub_window(self, title, data, id=0, hidden_columns=None, index_column=None, childSubWindow={}, type=1):
        """

        :param title: Window title
        :param data: Table show data
        :param hidden_columns: Columns to be hidden
        :param index_column: which column is index column
        :param childSubWindow: When double click each row, which child table should be opened
                Sample:  {
                            "title":"",
                            "type": "table",
                            "table_name": "option/underlyings/%underlying_order_book_id%",
                            "where:"",
                            "select":"",
                            "hidden_columns":[],
                            "index_column":[],
                            "childSubWindow":{},
                        }

        :return:
        """
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        if index_column:
            data.index = list(data[index_column])
            data.index.name = index_column
        subWindow = QMdiSubWindow()
        setattr(subWindow, "btData", data)
        setattr(subWindow, "btId", id)
        setattr(subWindow, "btType", type)
        setattr(subWindow, "btFilePath", None)
        setattr(subWindow, "childSubWindow", childSubWindow)
        setattr(subWindow, "hidden_columns", hidden_columns)

        tableView = QTableView()
        #双击列的信号
        tableView.horizontalHeader().sectionDoubleClicked.connect(lambda event: self.onTableViewColumnDoubleClicked(event, None))
        #双击行的信号
        tableView.verticalHeader().sectionDoubleClicked.connect(self.onTableViewRowDoubleClicked)
        #双击cell的信号
        tableView.doubleClicked.connect(self.onTableViewCellDoubleClicked)

        #右键列
        headers = tableView.horizontalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(lambda event: self.onTableViewColumnClicked(event, tableView))
        headers.setSelectionMode(QAbstractItemView.SingleSelection)

        cornerButton = tableView.findChild(QAbstractButton)
        cornerButton.customContextMenuRequested.connect(self.onCornerButtonRightClicked)

        tableView.setWindowTitle(title)

        proxyModel = QtCore.QSortFilterProxyModel(subWindow)
        mode = pandas_mode.PandasModel(data)
        proxyModel.setSourceModel(mode)
        tableView.setModel(proxyModel)

        self._hide_columns(tableView, data, hidden_columns)

        systemMenu = subWindow.systemMenu()
        last_action = systemMenu.actions()[-1]
        display_setting = self.window.findChild(QAction, "display_action")
        systemMenu.insertAction(last_action, display_setting)

        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWidget(tableView)
        self.mdi_area.addSubWindow(subWindow)

        subWindow.show()

    def _hide_columns(self, table_view, data, hidden_columns):
        columns_list = list(data.columns)
        if hidden_columns:
            for i in range(len(columns_list)):
                name = columns_list[i]
                if name in hidden_columns:
                    table_view.setColumnHidden(i, True)

    def _show_plot_sub_window(self, data_frame):
        if data_frame.empty:
            return
        loader = QUiLoader()
        subwindow = self.loadUI("plot.ui")
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

        self.mdi_area.addSubWindow(subwindow)
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

    def __display_table(self, data, currentSubWindow=None):
        if currentSubWindow is None:
            currentSubWindow = self.mdi_area.currentSubWindow()
        tableView = currentSubWindow.findChild(QTableView)
        tableView.clearSpans()
        mode = pandas_mode.PandasModel(data)
        tableView.setModel(mode)
        columns_list = list(data.columns)
        hidden_columns = getattr(currentSubWindow, "hidden_columns")
        for i in columns_list:
            index = columns_list.index(i)
            if i in hidden_columns:
                tableView.setColumnHidden(index, True)
            else:
                tableView.setColumnHidden(index, False)

    def __calculate_signal(self, text, col1, col2, signal_number):
        relation_signal = 0
        if text == u"上穿":
            try:
                relation_signal = np.where((col1 > col2) & (col1.shift() < col2.shift()), signal_number, 0)
            except:
                self.messageBox(u"当前数据不支持上穿")
                return False
        elif text == u"下穿":
            try:
                relation_signal = np.where((col1 < col2) & (col1.shift() > col2.shift()), signal_number, 0)
            except:
                self.messageBox(u"当前数据不支持下穿")
                return False
        elif text == u"大于":
            relation_signal = np.where((col1 > col2), signal_number, 0)
        elif text == u"大于或等于":
            relation_signal = np.where((col1 >= col2), signal_number, 0)
        elif text == u"小于":
            relation_signal = np.where((col1 < col2), signal_number, 0)
        elif text == u"小于或等于":
            relation_signal = np.where((col1 <= col2), signal_number, 0)
        elif text == u"等于":
            relation_signal = np.where((col1 == col2), signal_number, 0)
        elif text == u"或":
            relation_signal = np.where((col1 | col2), signal_number, 0)
        elif text == u"且":
            relation_signal = np.where((col1 & col2), signal_number, 0)
        elif text == u"非":
            relation_signal = np.where((col2 ^ 1), signal_number, 0)
        return relation_signal

    def _get_max_drawdown(self, array):
        drawdowns = []
        max_so_far = array[0]
        for i in range(len(array)):
            if array[i] > max_so_far:
                drawdown = 0
                drawdowns.append(drawdown)
                max_so_far = array[i]
            else:
                drawdown = max_so_far - array[i]
                drawdowns.append(drawdown)
        return max(drawdowns)

    def _get_performance_level(self, indicator):
        index = 0
        if indicator < 0:
            return u"没有等级，还需努力哦"
        elif indicator<=1:
            index = 0
        elif 1<indicator<=3:
            index = 1
        elif 3<indicator<=6:
            index = 2
        elif 6<indicator<=9:
            index = 3
        elif 9<indicator<=13:
            index = 4
        elif 13<indicator<=17:
            index = 5
        elif 17<indicator<=20:
            index = 6
        elif 20<indicator<=30:
            index = 7
        elif 30<indicator<=40:
            index = 8
        elif 40<indicator<=50:
            index = 9
        elif indicator>50:
            index = 10
        return setting.PERFORMANCE_LEVEL[index]

if __name__ == '__main__':

    app = QApplication(sys.argv)
    form = BT('main.ui')
    sys.exit(app.exec_())