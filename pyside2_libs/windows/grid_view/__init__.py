# encoding: utf-8

import os, re

from PySide2 import QtCore
from PySide2.QtWidgets import \
    QMdiSubWindow, QTableView, QAction, \
    QMenu, \
    QAbstractButton, QAbstractItemView
from PySide2.QtCore import Qt
from PySide2 import QtGui

# Make sure that we are using QT5
# matplotlib.use('Qt5Agg')
# os.environ["QT_API"] = "PySide2"
from matplotlib.font_manager import FontProperties

from src import pandas_mode

from pyside2_libs.windows.plot import Plot

font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14)

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

class GridView():

    def __init__(self, parent, title, data, id=0, hidden_columns=[], index_column=None, childSubWindow={}, type=1):
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
        self.parent = parent
        self.window = parent.window
        self.mdi_area = parent.mdi_area
        if index_column:
            data.index = list(data[index_column])
            data.index.name = index_column
        subWindow = QMdiSubWindow()
        setattr(subWindow, "subWindowType", 0)
        setattr(subWindow, "btData", data)
        setattr(subWindow, "btId", id)
        setattr(subWindow, "btType", type)
        setattr(subWindow, "btFilePath", None)
        setattr(subWindow, "childSubWindow", childSubWindow)
        setattr(subWindow, "hidden_columns", hidden_columns)

        tableView = QTableView()

        # 双击列的信号
        tableView.horizontalHeader().sectionDoubleClicked.connect(
            lambda event: self.onTableViewColumnDoubleClicked(event, None))
        # 双击行的信号
        tableView.verticalHeader().sectionDoubleClicked.connect(self.onTableViewRowDoubleClicked)
        # 双击cell的信号
        tableView.doubleClicked.connect(self.onTableViewCellDoubleClicked)

        # 右键列
        headers = tableView.horizontalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(lambda event: self.onTableViewColumnClicked(event, tableView))
        headers.setSelectionMode(QAbstractItemView.SingleSelection)

        cornerButton = tableView.findChild(QAbstractButton)
        cornerButton.customContextMenuRequested.connect(self.onCornerButtonRightClicked)

        tableView.setWindowTitle(title)
        tableView.setWindowIcon(QtGui.QIcon("../icon/sheet.png"))

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

    def onTableViewColumnDoubleClicked(self, index, evt):
        currentSubWindow = self.mdi_area.currentSubWindow()
        tableView = currentSubWindow.findChild(QTableView)
        selectedColumns = [selection.column() for selection in tableView.selectionModel().selectedColumns()]
        btData = getattr(currentSubWindow, "btData")
        selectedData = btData.iloc[:, selectedColumns]
        Plot(selectedData, self.window, self.mdi_area)
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
            self.parent._get_option_underlying_data(column_value, column_value)
        elif type == "option_contract_table":
            self.parent._get_option_contract_by_date(id, tableName)
        elif type == "future_contract_table":
            self.parent._get_future_contract_data(column_value, column_value)

        return

    def onTableViewCellDoubleClicked(self, index):
        # print(index.row(), index.column(), index.data())
        # data = getattr(self.mdi_area.currentSubWindow(), "btData")
        # print(data)
        return

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

    def onCornerButtonRightClicked(self):
        print(1111)