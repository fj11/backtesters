# encoding: utf-8

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import \
    QMdiSubWindow, QTabWidget
from PySide2.QtCore import Qt

from .manual_update_tab import ManualSignal
from .auto_update_tab import AutoUpdate

class DataCenterWidget():

    def __init__(self, parent, parent_widget):
        self.parent = parent
        self.parent_widget = parent_widget

        has_sub_window = [i for i in self.parent.mdi_area.subWindowList() if i.windowTitle() == u"数据下载"]
        if has_sub_window:
            return
        subWindow = QMdiSubWindow()
        loader = QUiLoader()
        data_center = loader.load('data_update.ui', parentWidget=parent_widget)

        tab_widgets = data_center.findChild(QTabWidget)
        ManualSignal(tab_widgets.widget(0), subWindow, parent.root)
        AutoUpdate(tab_widgets.widget(1), parent.root, parent.config)
        #
        subWindow.setWindowTitle(u"数据下载")
        subWindow.setWidget(data_center)
        parent.mdi_area.addSubWindow(subWindow)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.show()



