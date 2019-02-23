
import os, sys
from PySide2.QtWidgets import QApplication, QSplashScreen
from PySide2.QtGui import QPixmap

os.chdir("ui")
os.environ["QT_API"] = "PySide2"
from pyside2_libs import BT

if __name__ == '__main__':

    app = QApplication(sys.argv)

    pixmap = QPixmap('../images/boot.jpg')

    splash = QSplashScreen(pixmap)
    splash.show()

    app.processEvents()

    main = BT('main.ui')
    main.window.show()
    splash.finish(main.window)

    sys.exit(app.exec_())