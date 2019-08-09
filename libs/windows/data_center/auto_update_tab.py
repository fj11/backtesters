# encoding: utf-8

from PySide2.QtWidgets import \
    QRadioButton
import os

class AutoUpdate():

    def __init__(self, widget, root, config):

        self.root = root
        self.config = config

        self.update_config = self.config.getroot().findall("./data/update")[0]
        self.fre_value = int(self.update_config.get("freqency"))

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

        daily_update.clicked.connect(lambda event: self.checked(1))
        weekly_update.clicked.connect(lambda event: self.checked(2))
        monthly_update.clicked.connect(lambda event: self.checked(3))
        startup_update.clicked.connect(lambda event: self.checked(4))

        pass

    def checked(self, type):

        update_config = self.update_config
        if int(type) != int(self.fre_value):
            update_config.set("freqency", str(type))

            self.config.write(os.path.normpath(os.path.join(self.root, "backtesters")))
        pass



