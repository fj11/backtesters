# encoding: utf-8

from PySide2.QtWidgets import QListWidget, QPushButton

class ColumnsDisplay():

    def __init__(self, widget, parent, columns, hidden_columns):

        self.parent = parent

        hide_button = widget.findChild(QPushButton, "hide")
        show_button = widget.findChild(QPushButton, "show")

        show_list = widget.findChild(QListWidget, "show_list")
        hide_list = widget.findChild(QListWidget, "hide_list")

        show_columns = [i for i in columns if i not in hidden_columns]

        hide_list.addItems(hidden_columns)
        show_list.addItems(show_columns)

        hide_button.clicked.connect(lambda: self.onHideButtonClicked(show_list, hide_list))
        show_button.clicked.connect(lambda: self.onShowButtonClicked(show_list, hide_list))
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


