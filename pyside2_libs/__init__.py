# encoding: utf-8

import os
import uuid
import pickle

import pandas as pd

################ 不可以删除 ##################
from PySide2.QtXml import QDomNode
############################################

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMdiArea, QTreeWidgetItem, \
    QMessageBox, QTableView, QToolBox,\
    QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
    QTreeWidget, QSpinBox, QPushButton, QFileDialog,\
    QMenu, QInputDialog, QSlider
from PySide2.QtCore import QObject, Qt
from PySide2 import QtGui

from src import sql, pandas_mode, setting
from. import dialogs, subWindows

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
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        self.window.setWindowTitle("回测者")
        #self.window.setWindowIcon("")

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
        self.mdi_area.subWindowActivated.connect(self.onSubWindowActivated)

        self.window.findChild(QAction, "display_action").triggered.connect(self.onDisplay)
        self.window.findChild(QAction, "action_roll").triggered.connect(self.onRoll)
        self.window.findChild(QAction, "action_delete_column").triggered.connect(self.onDeleteColumn)
        self.window.findChild(QAction, "action_registration").triggered.connect(self.registration)
        self.window.findChild(QAction, "actionupdate").triggered.connect(self.update)

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

    def onSubWindowActivated(self, subWindow):
        if hasattr(subWindow, "btData") and hasattr(subWindow, "btFilePath"):
            self.action_save_file.setEnabled(True)
            self.action_save_as_flie.setEnabled(True)
        else:
            self.action_save_file.setEnabled(False)
            self.action_save_as_flie.setEnabled(False)

    def onSubWindowClosed(self):
        self.mdi_area.activatePreviousSubWindow()
        return

    def onBackTestTreeDoubleClicked(self, item, column):
        subWindows.StrategySetting(self, self.window, item, column)

    def active_backtest_widget(self, bt_type, text):
        return self._active_backtest_widget(bt_type, text)

    def _active_backtest_widget(self, bt_type, text):
        for i in self.mdi_area.subWindowList():
            if hasattr(i, "btType") and i.btType==bt_type and i.windowTitle() == text:
                self.mdi_area.setActiveSubWindow(i)
                return True



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

    def update(self):
        subWindows.RQData(self, self.window, self.mdi_area)

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

    def registration(self):
        dialog = self.loadUI("registration.ui", parentWidget=self.window)
        dialog.setWindowTitle("产品注册")
        line_edit = dialog.findChild(QLineEdit, "lineEdit")
        copy_button = dialog.findChild(QPushButton, "pushButton")
        uuid = get_uuid()
        line_edit.setText(uuid)
        line_edit.setReadOnly(True)
        copy_button.clicked.connect(lambda: self.registration_copy_button_clicked(line_edit))

        dialog.show()

    def registration_copy_button_clicked(self, line_edit):
        line_edit.selectAll()
        line_edit.copy()

    def onBacktest(self):

        subWindows.BackTest(self, self.window)

    def getSubWindowByAttribute(self, key, value):
        return self.__getSubWindowByAttribute(key, value)

    def __getSubWindowByAttribute(self, key, value):
        for i in self.mdi_area.subWindowList():
            if hasattr(i, key) and getattr(i, key) == value:
                return i
        return None

    def onAccounts(self):
        dialogs.Accounts(self, self.window)

    def onActionSignal(self):
        current_window = self.mdi_area.currentSubWindow()
        if current_window is None or not hasattr(current_window, "btData"):
            self.messageBox("请先打开数据")
            return
        dialogs.Signal(self, self.window, current_window)

    def onActionMSignal(self):
        subWindows.ManualSignal(self, self.window, self.mdi_area)

    def onActionFunction(self):

        current_window = self.mdi_area.currentSubWindow()
        if current_window is None or not hasattr(current_window, "btData"):
            self.messageBox("请先打开数据")
            return
        dialogs.Function(self, self.window, current_window)
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

    def messageBox(self, messgae):
        msgBox = QMessageBox(parent=self.window)
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
                          'open_interest',
                          'iopv',
                          'num_trades'
                          ]
        if id == "510050.XSHG":
            where = "date > '2015-02-08 00:00:00'"
        else:
            where = None
        if where:
            data = sql.read(table, where=where)
        else:
            data = sql.read(table)
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        else:
            subWindows.GridView(self, name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    index_column='date',
                                    childSubWindow=childSubWindow,
                                    type="option_underlying")

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
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        else:
            subWindows.GridView(self, name, data, id=id,
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
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        else:
            subWindows.GridView(self, name, data, id=id,
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
        if showData.empty:
            self.messageBox("数据库中没有该数据")
            return
        else:
            subWindows.GridView(self, "标的%s在%s日的期权全部合约" % (underlying_symbol, date), showData, index_column="symbol", hidden_columns=["symbol"], id=1)

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
        if data.empty:
            self.messageBox("数据库中没有该数据")
            return
        else:
            subWindows.GridView(self, name, data, id=id,
                                    hidden_columns=hidden_columns,
                                    index_column='date',
                                    childSubWindow=childSubWindow,
                                    type="option_underlying")

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