
import os, pickle
from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QTreeWidgetItem, \
    QListWidget, QComboBox, QDialogButtonBox, QLineEdit, \
    QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox, QPushButton,\
    QDoubleSpinBox, QTextEdit

from . import columns_display, filter_display
from src import setting

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
        filter_display.FilterDisplay(filter_widget, columns)

        button_box = widget.findChild(QDialogButtonBox, "buttonBox")
        button_box.accepted.connect(lambda : self.onGridDisplayAccept())
        button_box.rejected.connect(lambda : self.onGridDisplayReject())

        widget.show()

        self.widget = widget
        self.sub_window = sub_window

    def onGridDisplayAccept(self):

        hide_list = self.widget.findChild(QListWidget, "hide_list")
        items_text = [hide_list.item(i).text() for i in range(hide_list.count())]
        setattr(self.sub_window, "hidden_columns", items_text)
        data = getattr(self.sub_window, "btData")
        self.parent.display_table(data, self.sub_window)
        return

    def onGridDisplayReject(self):
        return

