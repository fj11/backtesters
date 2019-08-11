# encoding: utf-8
import sys
from io import StringIO
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTextEdit, QPushButton
from PySide2.QtCore import Qt
import pyperclip
import contextlib
import pandas as pd

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class CodingWidget():

    def __init__(self, parent, parent_widget):
        self.parent = parent
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        python_editor = loader.load('coding.ui', parentWidget=parent_widget)

        self.code_string = python_editor.findChild(QTextEdit, "code_string")

        self.result_display = python_editor.findChild(QTextEdit, "result_display")

        python_editor.findChild(QPushButton, "run").clicked.connect(lambda :self.onRunButton())
        python_editor.findChild(QPushButton, "cancel").clicked.connect(lambda: self.onCancelButton())

        subWindow.setWidget(python_editor)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

    def onRunButton(self):

        self.result_display.clear()
        self.code_string.selectAll()
        self.code_string.copy()
        string = pyperclip.paste()
        with stdoutIO() as s:
            try:
                string = """
# encoding: utf-8
%s
%s
%s""" % ("from talib.abstract import *", "import numpy as np\n", string)
                exec(string,  self.init_env())
                output = s.getvalue()
                self.result_display.setText(str(output))
            except Exception as e:
                self.result_display.setText(str(e))
            return

    def onCancelButton(self):
        return

    def init_env(self):

        local_parameters = {
            "read_data": self.get_data,
            "add_signal":self.add_signal

        }
        return local_parameters

    def get_data(self, name):

        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle() == name][0]
        if hasattr(sub_window, "btData"):
            return getattr(sub_window, "btData")
        else:
            return pd.DataFrame()

    def add_signal(self, name, data):
        sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle() == name][0]
        if hasattr(sub_window, "btData"):
            df = getattr(sub_window, "btData")
            df["signal"] = data
            self.parent.display_table(df, sub_window)
            return True
        else:
            return False

