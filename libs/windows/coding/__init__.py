# encoding: utf-8

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow
from PySide2.QtCore import Qt

class CodingWidget():

    def __init__(self, parent, parent_widget):
        self.parent = parent
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        python_editor = loader.load('coding.ui', parentWidget=parent_widget)

        subWindow.setWidget(python_editor)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()
