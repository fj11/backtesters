# encoding: utf-8

from PySide2.QtWidgets import \
    QRadioButton, QGroupBox
import os

class AutoUpdate():

    def __init__(self, widget, root, config):

        self.root = root
        self.config = config

        self.update_config = self.config.getroot().findall("./data/update")[0]
        self.fre_value = int(self.update_config.get("freqency"))
        self.enabled = int(self.update_config.get("enabled"))

        self.group_box = widget.findChild(QGroupBox)

        daily_update = widget.findChild(QRadioButton, "daily")
        weekly_update = widget.findChild(QRadioButton, "weekly")
        monthly_update = widget.findChild(QRadioButton, "monthly")
        startup_update = widget.findChild(QRadioButton, "startup")

        if self.fre_value == 1:
            daily_update.setChecked(True)
        elif self.fre_value == 2:
            weekly_update.setChecked(True)
        elif self.fre_value == 3:
            monthly_update.setChecked(True)
        elif self.fre_value == 4:
            startup_update.setChecked(True)

        if self.enabled:
            self.group_box.setChecked(True)
        else:
            self.group_box.setChecked(False)

        self.group_box.clicked.connect(lambda event: self.enable_checked(event))
        daily_update.clicked.connect(lambda event: self.fre_checked(1))
        weekly_update.clicked.connect(lambda event: self.fre_checked(2))
        monthly_update.clicked.connect(lambda event: self.fre_checked(3))
        startup_update.clicked.connect(lambda event: self.fre_checked(4))


    def fre_checked(self, type):
        update_config = self.update_config
        if int(type) != int(self.fre_value):
            update_config.set("freqency", str(type))
            self.config.write(os.path.normpath(os.path.join(self.root, "backtester.cfg")))

    def enable_checked(self, checked):
        if self.enabled ^ checked:
            if checked:
                self.update_config.set("enabled", "1")
            else:
                self.update_config.set("enabled", "0")
            self.config.write(os.path.normpath(os.path.join(self.root, "backtester.cfg")))

