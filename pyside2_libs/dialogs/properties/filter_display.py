# encoding: utf-8

from PySide2.QtWidgets import QTreeWidget, QPushButton, QComboBox, QLineEdit, QTreeWidgetItem

class FilterDisplay():

    def __init__(self, widget, columns):

        self.columns = columns

        add_button = widget.findChild(QPushButton, "add_filter")
        delete_button = widget.findChild(QPushButton, "delete_filter")

        self.filter_tree = widget.findChild(QTreeWidget)

        add_button.clicked.connect(lambda: self.onAddButton())
        delete_button.clicked.connect(lambda: self.onDeleteButton())
        return

    def onAddButton(self):

        value_list = QComboBox()
        value_list.addItems(self.columns)

        condition_list = QComboBox()
        condition_list.addItems(["大于", "大于且等于", "小于", "小于且等于", "等于", "包含于"])

        line_edit = QLineEdit()
        # line_edit.textChanged.connect(lambda: self.onFilterTreeCellEntered(filter_tree, table))

        filterItem = QTreeWidgetItem()
        self.filter_tree.addTopLevelItem(filterItem)

        self.filter_tree.setItemWidget(filterItem, 0, value_list)
        self.filter_tree.setItemWidget(filterItem, 1, condition_list)
        self.filter_tree.setItemWidget(filterItem, 2, line_edit)
        return

    def onDeleteButton(self):
        current_item = self.filter_tree.currentItem()
        current_index = self.filter_tree.indexOfTopLevelItem(current_item)
        self.filter_tree.takeTopLevelItem(current_index)
        return
