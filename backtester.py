
import os, sys
from PySide2.QtWidgets import QApplication

os.chdir("ui")
os.environ["QT_API"] = "PySide2"
from pyside2_libs import BT

if __name__ == '__main__':

    app = QApplication(sys.argv)
    form = BT('main.ui')
    sys.exit(app.exec_())