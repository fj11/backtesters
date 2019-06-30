# encoding: utf-8

import os, pickle

from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import \
    QListWidget, QDialogButtonBox, QLineEdit, \
    QSpinBox, QPushButton, QDoubleSpinBox

from src import setting

class Accounts():

    def __init__(self, parent, parent_widget):

        self.parent = parent
        self.root = self.parent.root
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