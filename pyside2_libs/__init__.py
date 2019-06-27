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
    QSlider
from PySide2.QtCore import QObject, Qt

from src import sql, pandas_mode, setting
from. import dialogs
from pyside2_libs.windows import trading_center, grid_view

ROOT = os.path.normpath(os.path.join(os.curdir, ".."))

sql.encryption("123qwe!@#QWE")

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

        self.action_function = self.window.findChild(QAction, "actionfunction")
        self.action_signal = self.window.findChild(QAction, "action_signal")
        self.action_about = self.window.findChild(QAction, "actionabout")
        self.action_account = self.window.findChild(QAction, "actionacounts")
        self.action_backtest = self.window.findChild(QAction, "actionstart_backtest")
        self.action_open_file = self.window.findChild(QAction, "actionopen")
        self.action_save_file = self.window.findChild(QAction, "actionsave")
        self.action_save_as_flie = self.window.findChild(QAction, "actionsave_as")
        self.action_new_file = self.window.findChild(QAction, "actionnew")

        self.filter = self.window.findChild(QAction, "action_filter")


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
        self.action_about.triggered.connect(self.about)
        self.action_account.triggered.connect(self.onAccounts)
        self.action_backtest.triggered.connect(self.onBacktest)
        self.action_new_file.triggered.connect(self.onNewFile)
        self.action_open_file.triggered.connect(self.onOpenFile)
        self.action_save_file.triggered.connect(self.onSaveAs)
        self.action_save_as_flie.triggered.connect(self.onSaveAs)

        self.filter.triggered.connect(self.onFilter)
        self.mdi_area.subWindowActivated.connect(self.onSubWindowActivated)

        self.window.findChild(QAction, "display_action").triggered.connect(self.onDisplay)
        self.window.findChild(QAction, "action_roll").triggered.connect(self.onRoll)
        self.window.findChild(QAction, "action_delete_column").triggered.connect(self.onDeleteColumn)
        self.window.findChild(QAction, "action_registration").triggered.connect(self.registration)
        self.window.findChild(QAction, "actionupdate").triggered.connect(self.update)

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

    def update(self):
        #TODO
        return
        # subWindows.RQData(self, self.window, self.mdi_area)

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

    def onNewFile(self):
        return

    def onOpenFile(self):
        fileName = QFileDialog.getOpenFileName(self.window, "Open BackTest File", "../", "BackTest Files (*.csv *.xls *.xlsx *.bt)")[0]
        file_name, extension = os.path.splitext(fileName)
        if extension == ".csv":
            data = pd.read_csv(fileName)
            grid_view.GridView(self, file_name, data, id=file_name,
                                type="csv")
        elif extension == ".xls" or  extension == ".xlsx":
            data = pd.read_excel(fileName)
            grid_view.GridView(self, file_name, data, id=file_name,
                                type="csv")
        elif extension == ".bt":
            pkl_file = open(fileName, 'rb')
            data = pickle.load(pkl_file)
            trading_center.TradeCenterWidget(self, self.window, data)

    def onSave(self, type, data, file_path):

        if type == 0:
            writer = pd.ExcelWriter('%s' % file_path)
            data.to_excel(writer, 'BackTest')
            writer.save()
        elif type == 1:
            with open("%s "% file_path, "wb") as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    def onSaveAs(self):
        currentSubWindow = self.mdi_area.currentSubWindow()
        if currentSubWindow is None:
            return
        if hasattr(currentSubWindow, "subWindowType"):
            type = getattr(currentSubWindow, "subWindowType")
        else:
            type = 10
        fileName = getattr(currentSubWindow, "btFilePath")

        if fileName is None or fileName == "":
            if type == 0:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../",
                                                       "BackTest Files (*.xlsx)")[0]
                if fileName:
                    data = getattr(currentSubWindow, "btData")
                    hidden_columns = getattr(currentSubWindow, "hidden_columns")
                    data = data.drop(hidden_columns, axis=1, errors="ignore")
                    self.onSave(type, data, fileName)
            elif type == 1:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../",
                                                       "BackTest Files (*.bt)")[0]
                if fileName:
                    data = getattr(currentSubWindow, "btData")
                    self.onSave(type, data, fileName)
            setattr(currentSubWindow, "btFilePath", fileName)

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

        trading_center.TradeCenterWidget(self, self.window)

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
            grid_view.GridView(self, name, data, id=id,
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
            grid_view.GridView(self, name, data, id=id,
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
            grid_view.GridView(self, name, data, id=id,
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
            grid_view.GridView(self, "标的%s在%s日的期权全部合约" % (underlying_symbol, date), showData, index_column="symbol", hidden_columns=["symbol"], id=1)

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
            grid_view.GridView(self, name, data, id=id,
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