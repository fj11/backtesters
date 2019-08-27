# encoding: utf-8
import sys
from io import StringIO
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTextEdit, QPushButton, QToolButton, QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import Qt
import contextlib
import pandas as pd
import numpy as np
import talib
import code
from src import functions, database, stock_item

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class CodingWidget():

    def __init__(self, parent, parent_widget, data=None, text='', file_path=None):

        self.db = database.DataBase("stock")
        self.db.encryption("123qwe!#QWE")
        self.parent = parent
        subWindow = QMdiSubWindow()
        self.sub_window = subWindow
        self.parent_widget = parent_widget
        loader = QUiLoader()
        python_editor = loader.load('coding.ui', parentWidget=parent_widget)

        self.code_string = python_editor.findChild(QTextEdit, "code_string")

        self.result_display = python_editor.findChild(QTextEdit, "result_display")

        python_editor.findChild(QToolButton).clicked.connect(lambda:self.onClickedFunctionButton())
        python_editor.findChild(QPushButton, "run").clicked.connect(lambda :self.onRunButton())
        python_editor.findChild(QPushButton, "cancel").clicked.connect(lambda: self.onCancelButton())

        self.code_string.textChanged.connect(lambda :self.onCodeChanged())
        if data:
            self.code_string.setPlainText(data)

        self.python_editor = python_editor

        setattr(subWindow, "subWindowType", 2)
        setattr(subWindow, "btData", '')
        setattr(subWindow, "btFilePath", file_path)
        subWindow.setWindowTitle(u"程序 - %s" % text)
        subWindow.setWidget(python_editor)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

    def onCodeChanged(self):
        setattr(self.sub_window, "btData", self.code_string.toPlainText())

    def onRunButton(self):

        self.result_display.clear()
        string = self.code_string.toPlainText()
        output = ""
        with stdoutIO() as s:
            try:
                string = """
# encoding: utf-8
%s
%s
%s
%s
%s""" % ("import talib", "from talib.abstract import *", "import numpy as np", "import pandas as pd\n", string)
                c = code.compile_command(string, "<stdin>", "exec")
                exec(c,  self.init_env())
            except Exception as e:
                print(str(e))
            output = s.getvalue()
        self.result_display.setText(output)

    def onCancelButton(self):
        return

    def init_env(self):

        local_parameters = {
            "read_data": self.get_data,
            "add_signal_to_sheet": self.add_signal_to_sheet,
            "cross_up": self.cross_up,
            "cross_down": self.cross_down,
            "greater_than": self.greater_than,
            "greater_than_or_equal_to": self.greater_than_or_equal_to,
            "less_than": self.less_than,
            "less_than_or_equal_to": self.less_than_or_equal_to,
            "equal_to": self.equal_to,
            "get_stock_ids": self.get_stocks,
            "get_stock": self.get_stock,
            "has_stock": self.has_stock,
        }
        return local_parameters

    def get_data(self, name):
        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle() == name][0]
        if hasattr(sub_window, "btData"):
            return getattr(sub_window, "btData")
        else:
            return pd.DataFrame()

    def add_signal_to_sheet(self, name, data):
        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle() == name][0]
        if hasattr(sub_window, "btData"):
            df = getattr(sub_window, "btData")
            df["signal"] = data
            self.parent.display_table(df, sub_window)
            return True
        else:
            return False

    def cross_up(self, l1, l2):
        return np.where((l1 > l2) & (l1.shift() < l2.shift()), 1, 0)

    def cross_down(self, l1, l2):
        return np.where((l1 < l2) & (l1.shift() > l2.shift()), 1, 0)

    def greater_than(self, l1, l2):
        return np.where((l1 > l2), 1, 0)

    def greater_than_or_equal_to(self, l1, l2):
        return np.where((l1 >= l2), 1, 0)

    def less_than(self, l1, l2):
        return np.where((l1 < l2), 1, 0)

    def less_than_or_equal_to(self, l1, l2):
        return np.where((l1 <= l2), 1, 0)

    def equal_to(self, l1, l2):
        return np.where((l1 == l2), 1, 0)

    def get_stocks(self):
        return [i.split("_", 1)[-1] for i in self.db.list_tables()]

    def get_stock(self, id, select="*", where=""):
        return stock_item.StockItem(self.parent, id, self.db, select=select, where=where)

    def has_stock(self, id, freqency="daily"):
        table = "%s_%s" % (freqency, id)
        return self.db.is_table(table)

    def onClickedFunctionButton(self):
        loader = QUiLoader()
        function_ui = loader.load('function_description.ui', parentWidget=self.python_editor)
        function_ui.setWindowTitle("函数说明")
        function_ui.show()

        self.tree = function_ui.findChild(QTreeWidget)
        self.demo = function_ui.findChild(QTextEdit)

        talib_groups = talib.get_function_groups()

        for key in talib_groups.keys():
            node = QTreeWidgetItem(self.tree)
            node.setText(0, key)
            for value in talib_groups[key]:
                sub_node = QTreeWidgetItem(node)
                sub_node.setText(0, value)
        names = functions.functions_name
        for key in names.keys():
            node = QTreeWidgetItem(self.tree)
            node.setText(0, key)
            for name in names[key].keys():
                sub_node = QTreeWidgetItem(node)
                sub_node.setText(0, name)
        self.tree.itemClicked.connect(
            lambda event1, event2: self.onFunctionTreeItemClicked(event1, event2))
        self.tree.itemDoubleClicked.connect(
            lambda event1, event2: self.onFunctionTreeItemDoubleClicked(event1, event2))
        return

    def onFunctionTreeItemClicked(self, item, column):

        text = item.text(column)
        name = ""
        self.demo.clear()
        if text in talib.get_functions():
            indicator = talib.abstract.Function(text.lower())
            info = indicator.info
            name = info.get("display_name", "")
        if text in functions.functions_name["自定义函数"].keys():
            name = functions.functions_name["自定义函数"][text]["demo_code"]
        self.demo.setText(name)
        return

    def onFunctionTreeItemDoubleClicked(self, item, column):
        text = item.text(column)
        function_name = ""
        name = "%s()"
        if text in talib.get_functions():
            function_name = text
        if text in functions.functions_name["自定义函数"].keys():
            function_name = text
        if function_name:
            self.code_string.append(name % function_name)
        return