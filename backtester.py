
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

################ 不可以删除 ##################
from PySide2.QtXml import QDomNode
############################################

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QMdiArea, QTreeWidgetItem, \
    QMessageBox, QMdiSubWindow, QTableView, QToolBox,\
    QTableWidget, QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
    QTreeWidget, QSpinBox, QPushButton, QFileDialog,\
    QMenu, QInputDialog, QDoubleSpinBox, QTableWidgetItem, \
    QAbstractButton, QAbstractItemView, QSlider
from PySide2.QtCore import QFile, QObject, Qt
from PySide2 import QtGui
os.environ["QT_API"] = "pyqt5"

from src import sql, pandas_mode, setting, dialogs, subWindows

os.chdir("ui")
ROOT = os.path.normpath(os.path.join(os.curdir, ".."))

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

        self.root = ROOT
        self.tc = None
        self.orders = {}
        self.positions = {}
        self.cashs = {}
        self.label_text = {}
        self.option_filter_dict = {}

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
        self.filter.triggered.connect(self.onFilter)
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

            open_type_list = sub_window_widget.findChild(QComboBox, "open_type")
            open_type_list.currentIndexChanged.connect(self.onBackTestOpenTypeChanged)

            table_view = sub_window_widget.findChild(QTableWidget)
            self.initBacktestAccountTable(table_view, account_files[0])

        subWindow.show()

    def onBackTestOpenTypeChanged(self, value):
        self.config["open_type"]["value"] = value
        return

    def _active_backtest_widget(self, bt_type, text):

        for i in self.mdi_area.subWindowList():
            if hasattr(i, "btType") and i.btType==bt_type and i.windowTitle() == text:
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
                    "list": [i.btId for i in self.mdi_area.subWindowList() if hasattr(i, "btType") and i.btType in ["option_underlying", "excel", "csv"]]
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

        subWindows.BackTest(self, self.window)
        #self._show_backtest_sub_window("开始回测", None, id=0)

    def __getSubWindowByAttribute(self, key, value):
        for i in self.mdi_area.subWindowList():
            if hasattr(i, key) and getattr(i, key) == value:
                return i
        return None

    def onAccounts(self):
        dialogs.Accounts(self, self.window)

    def onActionSignal(self):
        current_window = self.mdi_area.currentSubWindow()
        if current_window is None:
            self.messageBox("请先打开数据")
            return
        dialogs.Signal(self, self.window, current_window)

    def onActionMSignal(self):

        subWindows.ManualSignal(self, self.window, self.mdi_area)

    def onActionFunction(self):

        current_window = self.mdi_area.currentSubWindow()
        if current_window is None:
            self.messageBox("请先打开数据")
            return
        dialogs.Function(self, self.window, current_window)
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
        subWindows.Plot(selectedData, self.window, self.mdi_area)
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

    def display_table(self, data, currentSubWindow=None):
        self.__display_table(data, currentSubWindow)

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



if __name__ == '__main__':

    app = QApplication(sys.argv)
    form = BT('main.ui')
    sys.exit(app.exec_())