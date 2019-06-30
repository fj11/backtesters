# encoding: utf-8

from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import \
    QListWidget, QComboBox, QDialogButtonBox
import numpy as np

class Signals():

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
                self.parent.messageBox(u"当前数据不支持上穿")
                return False
        elif text == u"下穿":
            try:
                relation_signal = np.where((col1 < col2) & (col1.shift() > col2.shift()), signal_number, 0)
            except:
                self.parent.messageBox(u"当前数据不支持下穿")
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