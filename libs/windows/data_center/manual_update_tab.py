# encoding: utf-8

from PySide2.QtWidgets import \
    QPushButton, QTextEdit, QProgressBar
from .signals import Signals
from .stock import Stock

class ManualSignal():

    def __init__(self, widget, subWindow, root):
        self.update_button = widget.findChild(QPushButton, "update_button")
        self.log_output = widget.findChild(QTextEdit, "log_output")
        self.progress_bar = widget.findChild(QProgressBar, "progressBar")

        self.update_button.clicked.connect(lambda: self.onUpdateButton())

        self.signals = Signals(self.log_output, self.progress_bar)
        self.stock = Stock(root, self)

        subWindow.destroyed.connect(self.stop_update)

    def onUpdateButton(self):
        self.progress_bar.reset()
        self.log_output.clear()
        self.update_button.setEnabled(False)

        self.stock.set_enable(True)
        self.stock.finished.connect(self.updated)
        self.stock.start()

    def updated(self):
        try:
            self.update_button.setEnabled(True)
        except:
            return

    def stop_update(self):
        self.stock.set_enable(False)
        if self.stock.local_sql: self.stock.local_sql.close()
        # self.stock.remote_sql.close()
