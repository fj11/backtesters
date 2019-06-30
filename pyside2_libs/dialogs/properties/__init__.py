# encoding: utf-8

from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import \
    QListWidget, QDialogButtonBox,\
    QTabWidget, QTreeWidget

from . import columns_display, filter_display

import copy

class Properties():

    def __init__(self, parent):

        self.parent = parent
        self.main_window = parent.window
        self.mdi_area = parent.mdi_area

        sub_window = parent.mdi_area.currentSubWindow()
        data = getattr(sub_window, "btData")
        columns = list(data.columns)
        hidden_columns = getattr(sub_window, "hidden_columns")

        loader = QUiLoader()
        widget = loader.load("grid_display.ui", parentWidget=self.main_window)
        widget.setWindowTitle("显示设置")

        tab_widget = widget.findChild(QTabWidget)
        columns_display_widget = tab_widget.widget(0)
        filter_widget = tab_widget.widget(1)

        columns_display.ColumnsDisplay(columns_display_widget, parent, columns, hidden_columns)

        if hasattr(sub_window, "filter_condition"):
            filter_condition = getattr(sub_window, "filter_condition")
        else:
            filter_condition = []
        filter_display.FilterDisplay(filter_widget, columns, filter_condition)

        button_box = widget.findChild(QDialogButtonBox, "buttonBox")
        button_box.accepted.connect(lambda : self.onGridDisplayAccept())
        button_box.rejected.connect(lambda : self.onGridDisplayReject())

        widget.show()

        self.widget = widget
        self.sub_window = sub_window

    def onGridDisplayAccept(self):

        hide_list = self.widget.findChild(QListWidget, "hide_list")
        items_text = [hide_list.item(i).text() for i in range(hide_list.count())]
        hidden_coumns = getattr(self.sub_window, "hidden_columns")
        data = copy.deepcopy(getattr(self.sub_window, "btData"))
        if not hidden_coumns == items_text:
            setattr(self.sub_window, "hidden_columns", items_text)

        filter_tree = self.widget.findChild(QTreeWidget)
        setattr(self.sub_window, "filter_condition", [])
        for i in range(filter_tree.topLevelItemCount()):
            item = filter_tree.topLevelItem(i)
            columns_list = filter_tree.itemWidget(item, 0)
            condition_list = filter_tree.itemWidget(item, 1)
            value_line = filter_tree.itemWidget(item, 2)
            value = value_line.text().strip()
            if value:
                columns_value = columns_list.currentText()
                condition_value = condition_list.currentText()
                if columns_value != "date":
                    value = float(value)
                if condition_value == "大于":
                    data = data[data[columns_value] > value]
                elif condition_value == "大于且等于":
                    data = data[data[columns_value] >= value]
                elif condition_value == "小于":
                    data = data[data[columns_value] < value]
                elif condition_value == "小于且等于":
                    data = data[data[columns_value] <= value]
                elif condition_value == "等于":
                    data = data[data[columns_value] == value]
                elif condition_value == "包含于":
                    data = data[data[columns_value].contains(value)]
                condition = [columns_value, condition_value, value]
                filter_condition = getattr(self.sub_window, "filter_condition")
                filter_condition.append(condition)
        self.parent.display_table(data, self.sub_window)

    def onGridDisplayReject(self):
        return

