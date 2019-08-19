# encoding: utf-8

import os
import uuid
import pickle
import pandas as pd

################ 不可以删除 ##################
from PySide2.QtXml import QDomNode
############################################
import xml.etree.ElementTree as ET
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMdiArea, \
    QMessageBox, QTableView, QToolBox,\
    QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
    QSpinBox, QPushButton, QFileDialog,\
    QSlider, QInputDialog
from PySide2.QtCore import QObject, Qt

from src import sql, pandas_mode, setting
from. import dialogs
from libs.windows import trading_center, grid_view, data_center, coding, pool
from libs.dialogs import properties, functions, signals, accounts

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

        self.config = ET.parse(os.path.normpath(os.path.join(self.root, 'backtester.cfg')))

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
        self.action_open_file.triggered.connect(self.onOpenFile)
        self.action_save_file.triggered.connect(self.onSaveAs)
        self.action_save_as_flie.triggered.connect(self.onSaveAs)

        self.mdi_area.subWindowActivated.connect(self.onSubWindowActivated)

        self.window.findChild(QAction, "display_action").triggered.connect(self.onDisplay)
        self.window.findChild(QAction, "action_roll").triggered.connect(self.onRoll)
        self.window.findChild(QAction, "action_delete_column").triggered.connect(self.onDeleteColumn)
        self.window.findChild(QAction, "action_registration").triggered.connect(self.registration)
        self.window.findChild(QAction, "actionupdate").triggered.connect(self.update)
        self.window.findChild(QAction, "actioncode").triggered.connect(self.code)
        self.window.findChild(QAction, "actiontable").triggered.connect(self.code)
        self.window.findChild(QAction, "actiontrategy").triggered.connect(self.onBacktest)
        self.window.findChild(QAction, "actionpool").triggered.connect(self.pool)

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
        data_center.DataCenterWidget(self, self.window)
        return

    def code(self):
        text, ok = QInputDialog.getText(self.window, u'输入', '请输入文件名称')
        if ok:
            if text:
                coding.CodingWidget(self, self.window, text=text)
            else:
                self.messageBox("请输入文件名")

    def pool(self):
        text, ok = QInputDialog.getText(self.window, u'输入', '请输入文件名称')
        if ok:
            if text:
                pool.PoolWidget(self, self.window, text=text)
            else:
                self.messageBox("请输入文件名")

    def onDisplay(self):

        properties.Properties(self)

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
        fileName = QFileDialog.getOpenFileName(self.window, "Open BackTest File", "../", "BackTest Files (*.csv *.xls *.xlsx *.bt *.py)")[0]
        file_name, extension = os.path.splitext(fileName)
        file_name = os.path.basename(file_name)
        if extension == ".csv":
            data = pd.read_csv(fileName)
            grid_view.GridView(self, file_name, data, id=file_name,
                                type="csv", file_path=fileName)
        elif extension == ".xls" or  extension == ".xlsx":
            data = pd.read_excel(fileName)
            grid_view.GridView(self, file_name, data, id=file_name,
                                type="xlsx", file_path=fileName)
        elif extension == ".bt":
            pkl_file = open(fileName, 'rb')
            data = pickle.load(pkl_file)
            trading_center.TradeCenterWidget(self, self.window, data, text=file_name, file_path=fileName)
        elif extension == ".py":
            with open(fileName, "r", encoding="utf8") as f:
                data = f.read()
                coding.CodingWidget(self, self.window, data, text=file_name, file_path=fileName)

    def onSave(self, type, data, file_path):

        if type == 0:
            writer = pd.ExcelWriter('%s' % file_path)
            data.to_excel(writer, 'BackTest')
            writer.save()
        elif type == 1:
            with open("%s "% file_path, "wb") as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        elif type == 2:
            with open("%s" % file_path, "w") as f:
                f.write(data)

    def onSaveAs(self):
        currentSubWindow = self.mdi_area.currentSubWindow()
        if currentSubWindow is None:
            return
        if hasattr(currentSubWindow, "subWindowType"):
            type = getattr(currentSubWindow, "subWindowType")
        else:
            type = 10
        fileName = getattr(currentSubWindow, "btFilePath")
        default_file_name = currentSubWindow.windowTitle()
        default_file_name = default_file_name.split("-", 1)[-1]

        if fileName is None or fileName == "":
            if type == 0:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../%s.xlsx" % default_file_name,
                                                       "BackTest Files (*.xlsx)")[0]
                if fileName:
                    data = getattr(currentSubWindow, "btData")
                    hidden_columns = getattr(currentSubWindow, "hidden_columns")
                    data = data.drop(hidden_columns, axis=1, errors="ignore")
                    self.onSave(type, data, fileName)
            elif type == 1:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../%s.bt" % default_file_name,
                                                       "BackTest Files (*.bt)")[0]
                if fileName:
                    data = getattr(currentSubWindow, "btData")
                    self.onSave(type, data, fileName)
            elif type == 2:
                fileName = QFileDialog.getSaveFileName(self.window, "Save BackTest File", "../%s.py" % default_file_name,
                                                       "BackTest Files (*.py)")[0]
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
        text, ok = QInputDialog.getText(self.window, u'输入', '请输入文件名称')
        if ok:
            if text:
                trading_center.TradeCenterWidget(self, self.window, text=text)
            else:
                self.messageBox(u"请输入文件名")

    def getSubWindowByAttribute(self, key, value):
        return self.__getSubWindowByAttribute(key, value)

    def __getSubWindowByAttribute(self, key, value):
        for i in self.mdi_area.subWindowList():
            if hasattr(i, key) and getattr(i, key) == value:
                return i
        return None

    def onAccounts(self):
        accounts.Accounts(self, self.window)

    def onActionSignal(self):
        current_window = self.mdi_area.currentSubWindow()
        if current_window is None or not hasattr(current_window, "btData"):
            self.messageBox("请先打开数据")
            return
        signals.Signals(self, self.window, current_window)

    def onActionFunction(self):

        current_window = self.mdi_area.currentSubWindow()
        if current_window is None or not hasattr(current_window, "btData"):
            self.messageBox("请先打开数据")
            return
        functions.Functions(self, self.window, current_window)
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
                          'trading_hours',
                          'underlying_order_book_id'
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
                                    index_column="underlying_order_book_id",
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