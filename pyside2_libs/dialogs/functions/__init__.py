# encoding: utf-8

from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QTreeWidgetItem, \
    QListWidget, QComboBox, QDialogButtonBox, QLineEdit, \
    QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox

import talib
from talib import abstract
import numpy as np

class Functions():

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
                    self.parent.messageBox(u"当前数据不支持上穿")
                    return False
            elif text == u"下穿":
                try:
                    relation_signal = np.where((col1 < col2) & (col1.shift() > col2.shift()), 1, 0)
                except:
                    self.parent.messageBox(u"当前数据不支持下穿")
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