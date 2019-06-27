# encoding: utf-8

from PySide2 import QtCore
from PySide2.QtWidgets import QTreeWidgetItem, \
    QAction, QComboBox, \
    QTreeWidget, QSpinBox, QPushButton,\
    QMenu, QDoubleSpinBox, QDateEdit, \
    QCalendarWidget
from PySide2.QtCore import Qt
from PySide2 import QtGui

from src import sql

class ManualSignal():

    def __init__(self, widget, main_widget, config):
        self.config = config

        self.main_widget = main_widget
        manual_create_order = widget
        manual_create_order.setWindowTitle("手动下单")
        self.manual_create_order = manual_create_order

        order_type = manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = manual_create_order.findChild(QComboBox, "contract_id")
        add_order = manual_create_order.findChild(QPushButton, "add_order")
        calendar = manual_create_order.findChild(QCalendarWidget)
        order_tree = manual_create_order.findChild(QTreeWidget, "mtree")
        order_tree.setContextMenuPolicy(Qt.CustomContextMenu)

        self.manual_create_order.findChild(QAction, "delete_order").triggered.connect(lambda event:self.onDeleteOrder())
        order_tree.itemClicked.connect(lambda event:self.onOrderTreeClicked(event))
        order_tree.customContextMenuRequested.connect(lambda event:self.onOrderTreeRightClicked())
        order_type.currentTextChanged.connect(lambda event:self.onOrderTypeChanged(event))
        underlying_id.currentTextChanged.connect(lambda event:self.onUnderlyingIdChanged(event))

        contract_id.currentTextChanged.connect(lambda event: self.onContractIdChanged(event))

        calendar.clicked.connect(lambda event: self.onCalendarClicked(event, manual_create_order))
        add_order.clicked.connect(lambda :self.onAddOrderClicked())

        order_type.setCurrentIndex(1)
        orders = self.config.get("manual_order")
        if orders:
            self.loadOrderTree(orders)

    def loadOrderTree(self, orders):
        for order in orders:
            order_type = order.get("order_type")
            send_date = order.get("send_date")
            underlying_id = order.get("underlying_id")
            contract_id = order.get("contract_id")
            position_effect = order.get("position_effect")
            side = order.get("side")
            volume = order.get("volume")
            order_tree = self.manual_create_order.findChild(QTreeWidget, "mtree")
            item = QTreeWidgetItem(order_tree)
            item.setText(0, send_date)
            item.setText(1, underlying_id)
            item.setText(2, contract_id)
            item.setText(3, position_effect)
            item.setText(4, side)
            item.setText(5, order_type)
            item.setText(6, str(volume))

    def onDeleteOrder(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget, "mtree")
        item = order_tree.currentItem()
        index = order_tree.indexOfTopLevelItem(item)
        order_tree.takeTopLevelItem(index)
        self.config["manual_order"].pop(index)

    def onOrderTreeRightClicked(self):
        order_tree = self.manual_create_order.findChild(QTreeWidget, "mtree")
        delete_order = self.manual_create_order.findChild(QAction, "delete_order")
        if order_tree.currentColumn() >= 0:
            menu = QMenu(order_tree)
            menu.addAction(delete_order)
            menu.popup(QtGui.QCursor.pos())

    def onOrderTreeClicked(self, item):

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
        self.manual_create_order.findChild(QSpinBox, "mvolume").setValue(int(volume))

    def onAddOrderClicked(self):

        send_date = self.manual_create_order.findChild(QDateEdit, "send_date")
        order_type = self.manual_create_order.findChild(QComboBox, "order_type")
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        contract_id = self.manual_create_order.findChild(QComboBox, "contract_id")
        position_effect = self.manual_create_order.findChild(QComboBox, "position_effect")
        side = self.manual_create_order.findChild(QComboBox, "side")
        volume = self.manual_create_order.findChild(QSpinBox, "mvolume")

        order_tree = self.manual_create_order.findChild(QTreeWidget, "mtree")

        item = QTreeWidgetItem(order_tree)

        send_date_text = send_date.dateTime().toString("yyyy-MM-dd 00:00:00")
        underlying_id_text = underlying_id.currentText()
        order_type_text = order_type.currentText()
        side_text = side.currentText()
        volume_text = volume.value()
        position_effect_text = position_effect.currentText()

        order = {
            "order_type": order_type_text,
            "send_date": send_date_text,
            "underlying_id": underlying_id_text,
            "position_effect": position_effect_text,
            "side": side_text,
            "volume": volume_text
        }

        item.setText(0, send_date_text)
        item.setText(1, underlying_id_text)
        if order_type_text == "期权合约":
            if hasattr(contract_id, "ids"):
                ids = getattr(contract_id, "ids")
                contract_symbol_index = contract_id.currentIndex()
                contract_symbol_text = ids[contract_symbol_index]
                item.setText(2, contract_symbol_text)
                order.update(
                    {"contract_id": contract_symbol_text    }
                )

        item.setText(3, position_effect_text)
        item.setText(4, side_text)
        item.setText(5, order_type_text)
        item.setText(6, str(volume_text))

        self.config["manual_order"].append(order)

    def onOrderTypeChanged(self, text):
        underlying_id = self.manual_create_order.findChild(QComboBox, "underlying_id")
        underlying_id.clear()
        if text == "期权合约":
            underlying_ids = []
            for index in range(self.main_widget.option_list.rowCount()):
                underlying_ids.append(self.main_widget.option_list.item(index, 1).text())
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
        if data.empty:
            return
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
            self.main_widget.messageBox("不是交易日")
            return
        self.manual_create_order.findChild(QDateEdit, "send_date").setDate(date)
        order_type = manual_create_order.findChild(QComboBox, "order_type")
        text = order_type.currentText()
        self.onOrderTypeChanged(text)