
import os, pickle

from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QTreeWidgetItem, \
    QListWidget, QComboBox, QDialogButtonBox, QLineEdit, \
    QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox, QPushButton,\
    QDoubleSpinBox, QTextEdit

import talib
from talib import abstract
import numpy as np

from src import setting

class Function():

    def __init__(self, parent, parent_widget, current_window):
        self.parent = parent
        loader = QUiLoader()
        function_ui = loader.load('function_dialog.ui', parentWidget=parent_widget)
        function_ui.setWindowTitle("函数计算")
        data = getattr(current_window, "btData")
        hidden_columns = getattr(current_window, "hidden_columns")
        function_tab = function_ui.findChild(QTabWidget, "function_tab")
        input = function_ui.findChild(QLineEdit, "column_name")
        button_box = function_ui.findChild(QDialogButtonBox, "buttonBox")

        input.textEdited.connect(lambda: self.onFunctionInput(function_ui))
        button_box.accepted.connect(lambda: self.onFunctionAccept(function_ui, data))
        # button_box.rejected.connect(self.onFunctionReject)

        "lambda event: self.onTableViewColumnDoubleClicked(event, None)"

        function_tab.currentChanged.connect(
            lambda event: self.onLoadFunctionDialogTab(event, function_ui, data, hidden_columns))
        # self.function_tab.currentChanged.connect(self.onLoadFunctionDialogTab)
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

            self.tec_tree.itemClicked.connect(
                lambda event1, event2: self.onFunctionTecTree(event1, event2, function_ui, data, hidden_columns))
            self.search_tec_function.textEdited.connect(lambda event: self.onTecFunctionSearched(function_ui))

    def onTecFunctionSearched(self, function_ui):

        text = self.search_tec_function.text().strip().lower()
        self.tec_tree.clear()
        self.tec_tree = function_ui.findChild(QTreeWidget, "tec_tree")
        if text != "":
            talib_functions = talib.get_functions()
            for i in talib_functions:
                if text in i.lower():
                    node = QTreeWidgetItem(self.tec_tree)
                    node.setText(0, i)
        else:
            talib_groups = talib.get_function_groups()
            for key in talib_groups.keys():
                node = QTreeWidgetItem(self.tec_tree)
                node.setText(0, key)
                for value in talib_groups[key]:
                    sub_node = QTreeWidgetItem(node)
                    sub_node.setText(0, value)

    def onFunctionTecTree(self, item, column, function_ui, data, hidden_columns):
        group_box = function_ui.findChild(QGroupBox, "parameter_box")
        display_name_box = function_ui.findChild(QLineEdit, "display_name")
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
        info = indicator.info
        display_name = info.get("display_name", "")
        display_name_box.setText(display_name)

        params_dict = indicator.get_parameters()
        keys = list(params_dict.keys())
        keys.insert(0, u"Column")
        locator = 20
        num = 0
        paras_locators = [locator + i * 30 for i in range(len(keys))]
        for key in keys:
            p = paras_locators[num]
            label = QLabel(group_box)
            label.setText(key)
            label.setGeometry(10, p, 100, 20)
            if key == "Column":
                combo_box = QComboBox(group_box)
                combo_box.setGeometry(100, p, 100, 20)
                combo_box.setObjectName(key)
                combo_box.setWhatsThis(key)
                columns = [i for i in list(data.columns) if i not in hidden_columns]
                combo_box.addItems(columns)
                if "close" in columns:
                    combo_box.setCurrentText("close")
                combo_box.show()
            else:
                spin_box = QSpinBox(group_box)
                spin_box.setGeometry(100, p, 50, 20)
                spin_box.setObjectName(text)
                spin_box.setWhatsThis(key)
                value = params_dict[key]
                spin_box.setValue(value)
                spin_box.show()
            label.show()

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
            elif text == u"或":
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
                # self.messageBox("请选择正确的函数后再试")
                return
            tech_indicator = talib.abstract.Function(function_name.lower())
            output_names = tech_indicator.output_names
            group_box = function_ui.findChild(QGroupBox, "parameter_box")
            spin_boxs = group_box.findChildren(QSpinBox)
            combo_boxs = group_box.findChildren(QComboBox)

            selected_column_name = "close"
            for combo_box in combo_boxs:
                name = combo_box.objectName()
                if name == "Column":
                    selected_column_name = combo_box.currentText()
            data_arrays = {"close": data.get(selected_column_name, []),
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
                    parameters.update({param_key: param_value})
            tech_indicator.set_parameters(parameters)
            data_frame = tech_indicator.run()
            if len(output_names) == 1:
                data[column_name] = data_frame
            else:
                for i in range(len(output_names)):
                    output_name = output_names[i]
                    data[output_name] = data_frame[i]

        self.parent.display_table(data)


class Signal():

    def __init__(self, parent, parent_widget, current_window):

        self.parent = parent

        data = getattr(current_window, "btData")
        hidden_columns = getattr(current_window, "hidden_columns")
        loader = QUiLoader()
        signal = loader.load('signal_dialog.ui', parentWidget=parent_widget)
        signal.setWindowTitle("函数信号")

        button_box = signal.findChild(QDialogButtonBox, "buttonBox")

        open_signal_box = signal.findChild(QComboBox, "openbox")
        open_signal_list1 = signal.findChild(QListWidget, "open_list1")
        open_signal_list2 = signal.findChild(QListWidget, "open_list2")

        close_signal_box = signal.findChild(QComboBox, "closebox")
        close_signal_list1 = signal.findChild(QListWidget, "close_list1")
        close_signal_list2 = signal.findChild(QListWidget, "close_list2")

        button_box.accepted.connect(lambda: self.onSignalAccept(data, signal))
        button_box.rejected.connect(self.onSignalReject)

        list_items = [i for i in list(data.columns) if i not in hidden_columns]
        for item in list_items:
            open_signal_list1.addItem(item)
            close_signal_list1.addItem(item)
            open_signal_list2.addItem(item)
            close_signal_list2.addItem(item)

        signal.show()

    def onSignalAccept(self, data, signal):

        open_signal_box = signal.findChild(QComboBox, "openbox")
        open_signal_list1 = signal.findChild(QListWidget, "open_list1")
        open_signal_list2 = signal.findChild(QListWidget, "open_list2")

        close_signal_box = signal.findChild(QComboBox, "closebox")
        close_signal_list1 = signal.findChild(QListWidget, "close_list1")
        close_signal_list2 = signal.findChild(QListWidget, "close_list2")

        open_signal_text = open_signal_box.currentText()
        open_list1_row_number = open_signal_list1.currentRow()
        open_list2_row_number = open_signal_list2.currentRow()
        if open_list1_row_number >= 0 and open_list2_row_number >= 0:
            open_list1_text = open_signal_list1.currentItem().text()
            open_list2_text = open_signal_list2.currentItem().text()
            open_col1 = data.loc[:, open_list1_text]
            open_col2 = data.loc[:, open_list2_text]
            open_signal = self.__calculate_signal(open_signal_text, open_col1, open_col2, 1)
        else:
            open_signal = 0

        close_signal_text = close_signal_box.currentText()
        close_list1_row_number = close_signal_list1.currentRow()
        close_list2_row_number = close_signal_list2.currentRow()

        if close_list1_row_number >= 0 and close_list2_row_number >= 0:
            close_list1_text = open_signal_list1.currentItem().text()
            close_list2_text = open_signal_list2.currentItem().text()
            close_col1 = data.loc[:, close_list1_text]
            close_col2 = data.loc[:, close_list2_text]
            close_signal = self.__calculate_signal(close_signal_text, close_col1, close_col2, -1)
        else:
            close_signal = 0
        signal = open_signal|close_signal
        if "signal" in data.columns:
            signal = data["signal"]|signal

        for i in range(len(signal)-1, -1, -1):
            n = signal[i]
            if n == 1:
                signal[i] = 0
                break
            elif n == -1:
                break

        data["signal"] = signal
        self.parent.display_table(data)
        return

    def onSignalReject(self):
        return

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

class Accounts():

    def __init__(self, parent, parent_widget):

        self.root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        self.parent = parent
        loader = QUiLoader()
        self.account_management = loader.load('account_management.ui', parentWidget=parent_widget)
        self.account_management.setWindowTitle("账户")

        self.account_list = self.account_management.findChild(QListWidget)
        self.add_account_button = self.account_management.findChild(QPushButton, "add_account")
        self.delete_account_button = self.account_management.findChild(QPushButton, "delete_account")

        self.add_account_button.clicked.connect(lambda :self.onNewAccount(self.account_management))
        self.delete_account_button.clicked.connect(self.onDeleteAccount)
        self.account_list.itemClicked.connect(self.onAccountListClicked)
        account_folder = os.path.normpath(os.path.join(self.root, "accounts"))
        files = [f for f in os.listdir(account_folder) if
                 os.path.isfile(os.path.normpath(os.path.join(account_folder, f))) and f.endswith("bt")]
        for f in files:
            name, extension = os.path.splitext(f)
            self.account_list.addItem(name)
        self.account_management.show()

    def onAccountListClicked(self, item):
        name = item.text()
        account_folder = os.path.normpath(os.path.join(self.root, "accounts", "%s.bt" % name))
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

    def onNewAccount(self, parent):
        loader = QUiLoader()
        self.create_account = loader.load('create_account.ui', parentWidget=parent)
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
            account_folder = os.path.normpath(os.path.join(self.root, "accounts", "%s.bt" % name))
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
        account_folder = os.path.normpath(os.path.join(self.root, "accounts", "%s.bt" % name))
        with open(account_folder, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(info, f, pickle.HIGHEST_PROTOCOL)
        return

    def onCreateAccountReject(self):
        return