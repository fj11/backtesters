# encoding: utf-8
import sys
from io import StringIO
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTextEdit, QPushButton
from PySide2.QtCore import Qt
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

    def __init__(self, parent, parent_widget, data=None):
        self.parent = parent
        subWindow = QMdiSubWindow()
        self.sub_window = subWindow
        loader = QUiLoader()
        python_editor = loader.load('coding.ui', parentWidget=parent_widget)

        self.code_string = python_editor.findChild(QTextEdit, "code_string")

        self.result_display = python_editor.findChild(QTextEdit, "result_display")

        python_editor.findChild(QPushButton, "run").clicked.connect(lambda :self.onRunButton())
        python_editor.findChild(QPushButton, "cancel").clicked.connect(lambda: self.onCancelButton())

        self.code_string.textChanged.connect(lambda :self.onCodeChanged())
        if data:
            self.code_string.setPlainText(data)

        setattr(subWindow, "subWindowType", 2)
        setattr(subWindow, "btData", '')
        setattr(subWindow, "btFilePath", None)
        subWindow.setWindowTitle(u"程序")
        subWindow.setWidget(python_editor)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()

    def onCodeChanged(self):
        setattr(self.sub_window, "btData", self.code_string.toPlainText())

    def onRunButton(self):

        self.result_display.clear()
        string = self.code_string.toPlainText()
        with stdoutIO() as s:
            try:
                string = """
# encoding: utf-8
%s
%s
%s
%s""" % ("from talib.abstract import *", "import numpy as np", "import pandas as pd\n", string)
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

