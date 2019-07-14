# encoding: utf-8

import os, sys
from PySide2.QtWidgets import QApplication, QSplashScreen, QSystemTrayIcon, QMenu
from PySide2.QtGui import QPixmap, QIcon

os.chdir("ui")
os.environ["QT_API"] = "PySide2"
from libs import BT

class App:
    def __init__(self):
        # Create a Qt application
        self.app = QApplication(sys.argv)
        self.main = BT('main.ui')

        self.splash = QSplashScreen(QPixmap('../images/boot.jpg'))
        self.splash.show()

        menu = QMenu()
        showAction = menu.addAction("显示")
        hideAction = menu.addAction("隐藏")
        closeAction = menu.addAction("退出")

        showAction.triggered.connect(lambda event: self.show(showAction, hideAction))
        hideAction.triggered.connect(lambda event: self.hide(showAction, hideAction))
        closeAction.triggered.connect(self.exit)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("../icon/icon.ico"))
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.tray.setToolTip("")

    def run(self):
        # Enter Qt application main loop

        self.app.processEvents()

        self.main.window.show()

        self.splash.finish(self.main.window)

        sys.exit(self.app.exec_())

    def hide(self, show_action, hiden_actoin):
        hiden_actoin.setDisabled(True)
        show_action.setEnabled(True)
        self.main.window.hide()
        return

    def show(self, show_action, hiden_actoin):
        hiden_actoin.setEnabled(True)
        show_action.setDisabled(True)
        self.main.window.show()
        return

    def exit(self):
        self.main.window.close()
        return

if __name__ == '__main__':

    app = App()
    app.run()




