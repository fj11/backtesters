

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QApplication, QMdiArea, QTreeWidgetItem, \
    QMessageBox, QMdiSubWindow, QTableView, QToolBox, QFrame, QListView, \
    QTableWidget, QListWidget, QAction, QComboBox, QDialogButtonBox, QLineEdit, \
    QTabWidget, QTreeWidget, QSpinBox, QLabel, QGroupBox, QPushButton, QFileDialog,\
    QMenu, QInputDialog, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, \
    QToolBar, QCalendarWidget, QWidget, QAbstractButton, QAbstractItemView, QSlider
from PySide2.QtCore import Qt
from PySide2 import QtGui

from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from src import sql

font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=14)

class ManualSignal():

    def __init__(self, parent, parent_widget, mdi_area):
        self.parent = parent
        loader = QUiLoader()
        manual_create_order = loader.load('msignal_dialog.ui', parentWidget=parent_widget)
        manual_create_order.setWindowTitle("手动下单")
        self.manual_create_order = manual_create_order

        order_type = manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = manual_create_order.findChild(QComboBox, "contract_id")
        add_order = manual_create_order.findChild(QPushButton, "add_order")
        calendar = manual_create_order.findChild(QCalendarWidget)
        order_tree = manual_create_order.findChild(QTreeWidget)
        order_tree.setContextMenuPolicy(Qt.CustomContextMenu)

        self.manual_create_order.findChild(QAction, "delete_order").triggered.connect(self.onDeleteOrder)
        order_tree.itemClicked.connect(self.onOrderTreeClicked)
        order_tree.customContextMenuRequested.connect(self.onOrderTreeRightClicked)
        order_type.currentTextChanged.connect(self.onOrderTypeChanged)
        underlying_id.currentTextChanged.connect(self.onUnderlyingIdChanged)
        contract_id.currentTextChanged.connect(self.onContractIdChanged)
        calendar.clicked.connect(lambda event: self.onCalendarClicked(event, manual_create_order))
        add_order.clicked.connect(self.onAddOrderClicked)

        order_type.setCurrentIndex(1)
        manual_create_order.setAttribute(Qt.WA_DeleteOnClose)
        #manual_create_order.btType = None
        mdi_area.addSubWindow(manual_create_order)
        manual_create_order.show()

    def onDeleteOrder(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget)
        item = order_tree.currentItem()
        index = order_tree.indexOfTopLevelItem(item)
        order_tree.takeTopLevelItem(index)

    def onOrderTreeRightClicked(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget)
        delete_order = self.manual_create_order.findChild(QAction, "delete_order")
        if order_tree.currentColumn() > 0:
            menu = QMenu(order_tree)
            menu.addAction(delete_order)
            menu.popup(QtGui.QCursor.pos())

    def onOrderTreeClicked(self, item, column):

        send_date_text = item.text(0)

        underlying_id_text = item.text(1)
        contract_id_text = item.text(2)
        position_effect_text = item.text(3)
        side_text = item.text(4)
        order_type_text = item.text(5)
        volume = item.text(6)

        self.manual_create_order.findChild(QDateEdit, "send_date").setDate(QtCore.QDate.fromString(send_date_text, "yyyy-MM-dd 00:00:00"))
        self.manual_create_order.findChild(QComboBox, "order_type").setCurrentText(order_type_text)
        self.manual_create_order.findChild(QComboBox, "underlying_id").setCurrentText(underlying_id_text)
        if contract_id_text:
            contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
            ids = getattr(contract_id, "ids")
            contract_id.setCurrentIndex(ids.index(contract_id_text))
        self.manual_create_order.findChild(QComboBox, "position_effect").setCurrentText(position_effect_text)
        self.manual_create_order.findChild(QComboBox, "side").setCurrentText(side_text)
        self.manual_create_order.findChild(QSpinBox, "volume").setValue(int(volume))

    def onAddOrderClicked(self):

        send_date = self.manual_create_order.findChild(QDateEdit, "send_date")
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
        position_effect = self.manual_create_order.findChild(QComboBox, "position_effect")
        side = self.manual_create_order.findChild(QComboBox, "side")
        volume = self.manual_create_order.findChild(QSpinBox, "volume")

        order_tree = self.manual_create_order.findChild(QTreeWidget)

        item = QTreeWidgetItem(order_tree)
        item.setText(0, send_date.dateTime().toString("yyyy-MM-dd 00:00:00"))
        item.setText(1, underlying_id.currentText())
        if order_type.currentIndex() == 0:
            if hasattr(contract_id, "ids"):
                ids = getattr(contract_id, "ids")
                contract_symbol_index = contract_id.currentIndex()
                item.setText(2, ids[contract_symbol_index])
        item.setText(3, position_effect.currentText())
        item.setText(4, side.currentText())
        item.setText(5, order_type.currentText())
        item.setText(6, str(volume.value()))

    def onOrderTypeChanged(self, text):
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        underlying_id.clear()
        if text == "期权合约":
            underlying_ids = []
            for index in range(self.parent.option_list.rowCount()):
                underlying_ids.append(self.parent.option_list.item(index, 1).text())
            underlying_id.addItems(underlying_ids)
            self.manual_create_order.findChild(QComboBox, "contract_id").setEnabled(True)
        elif text == "期权标的":
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            table = "option/contract"
            data = sql.read(table, where="maturity_date>='%s' AND listed_date <= '%s' " % (date, date))
            ids = [id for id, group in data.groupby(["underlying_order_book_id"])]
            # underlying_ids = []
            # for index in range(self.option_list.rowCount()):
            #     underlying_ids.append(self.option_list.item(index, 1).text())
            self.manual_create_order.findChild(QComboBox, "underlying_id").addItems(ids)
            self.manual_create_order.findChild(QComboBox, "contract_id").setEnabled(False)

    def onContractIdChanged(self, text):
        contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
        if not hasattr(contract_id, "ids"):
            return
        ids = getattr(contract_id, "ids")
        if ids == []:
            return
        index = contract_id.currentIndex()
        text = ids[index]
        date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
        table = "option/contracts/%s" % text
        data = sql.read(table, where="date='%s'" % date)
        close_price = data.close
        self.manual_create_order.findChild(QDoubleSpinBox, "close_price").setValue(close_price)

    def onUnderlyingIdChanged(self, text):
        if not text:
            return
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        if order_type.currentIndex() == 0:
            contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            contract_id.clear()
            table = "option/contract"
            data = sql.read(table, where="underlying_symbol='%s' AND maturity_date>='%s' AND listed_date <= '%s' " % (text, date, date))
            ids = list(data.order_book_id)
            symbols = list(data.symbol)
            contract_id.addItems(symbols)
            setattr(contract_id, "ids", ids)
        else:
            table = "option/underlyings/%s" % text
            date = self.manual_create_order.findChild(QDateEdit, "send_date").dateTime().toString("yyyy-MM-dd 00:00:00")
            data = sql.read(table, where="date='%s'" % date)
            close_price = data.close
            self.manual_create_order.findChild(QDoubleSpinBox, "close_price").setValue(close_price)

    def onCalendarClicked(self, date, manual_create_order):
        date_str = date.toString("yyyy-MM-dd 00:00:00")
        table = "option/underlyings/510050.XSHG"
        tick = sql.read(table, where="date='%s'" % date_str)
        if tick.empty:
            self.parent.messageBox("不是交易日")
            return
        self.manual_create_order.findChild(QDateEdit, "send_date").setDate(date)
        order_type = manual_create_order.findChild(QComboBox, "order_type")
        text = order_type.currentText()
        self.onOrderTypeChanged(text)

class Plot():

    def __init__(self, data_frame, parent_widget, mdi_area):
        if data_frame.empty:
            return
        self.subplot = False
        self.label_text = {}
        loader = QUiLoader()
        subwindow = loader.load("plot.ui", parentWidget=parent_widget)
        subwindow.setWindowTitle("图形展示")

        pwidget = subwindow.findChild(QWidget)

        canvas = FigureCanvas(Figure())
        canvas.figure.add_subplot(111)
        canvas.axes = canvas.figure.add_subplot(111)

        canvas.mpl_connect('motion_notify_event', lambda event: self.onPlotMotion(event, canvas))
        canvas.mpl_connect('key_press_event', self.onPlotPress)

        cols = list(data_frame.columns)
        index = list(data_frame.index)
        index_name = data_frame.index.name
        for i in range(0, len(index)):
            self.label_text[i] = []
            for j in range(0, len(cols)):
                col_data = float(data_frame.iloc[i, j])
                self.label_text[i].append(canvas.axes.annotate("%s:%s\n%s:%s" %
                                                             (index_name, index[i], cols[j], col_data), (i, col_data),
                                                             bbox=dict(boxstyle="round", fc="w", ec="k"), visible=False,
                                                             size=0.3 * 36))
                # self.label_text[i, col_data] = self.axes.annotate("%s: %s" % (cols[j], col_data), (i, col_data), visible=False)
        axes = data_frame.plot(ax=canvas.axes, legend=True, subplots=self.subplot)
        # self.axes.legend(loc="best")
        # x_label = to_unicode(index_name)
        # x_label = index_name
        axes.set_xlabel(index_name)
        axes.grid(True)
        axes.tick_params(axis='x', labelsize=7)
        toolbar = NavigationToolbar2QT(canvas, pwidget)
        toolbar.update()
        l = QtWidgets.QVBoxLayout(pwidget)
        l.addWidget(toolbar)
        l.addWidget(canvas)
        subwindow.setAttribute(Qt.WA_DeleteOnClose)

        mdi_area.addSubWindow(subwindow)
        subwindow.show()

    def onPlotMotion(self, evt, canvas):
        for texts in self.label_text.values():
            for text in texts:
                if text.get_visible():
                    text.set_visible(False)
        if evt.inaxes:
            mycursor = QtGui.QCursor()
            canvas.setCursor(mycursor)
            #self.canvas.setCursor(mycursor)
            xpos = int(evt.xdata)
            annotations = self.label_text.get(xpos, [])
            for annotation in annotations:
                if not annotation.get_visible():             # is entered
                    annotation.set_visible(True)
            canvas.axes.figure.canvas.draw()

    def onPlotPress(self, evt):
        return