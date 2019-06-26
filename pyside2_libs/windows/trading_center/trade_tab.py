# encoding: utf-8

import os, pickle, re

import pandas as pd
import numpy as np

from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QTreeWidgetItem, \
    QMdiSubWindow, QTableView, \
    QTableWidget, QAction, QComboBox, QLineEdit, \
    QTreeWidget, QSpinBox, QPushButton,\
    QMenu, QDoubleSpinBox, QTableWidgetItem, QDateEdit, QProgressBar, \
    QCalendarWidget, QWidget, QAbstractButton, QAbstractItemView, QCheckBox, QTextEdit
from PySide2.QtCore import Qt
from PySide2 import QtGui

from pyside2_libs.windows.grid_view import GridView
from src import sql, tradeCenter, setting

class BackTest():
    def __init__(self, widget, main_widget):
        self.parent = main_widget

        self.config = main_widget.config
        self.mdi_area = self.parent.mdi_area
        self.root = self.parent.root

        self.tc = None

        backtest = widget

        result_tree = backtest.findChild(QTreeWidget)
        result_tree.itemDoubleClicked.connect(self.onResultTreeDoubleClicked)

        select_account = backtest.findChild(QComboBox, "account")
        account_folder = os.path.normpath(os.path.join(self.root, "accounts"))
        account_files = [os.path.splitext(i)[0] for i in os.listdir(account_folder) if
                         os.path.splitext(i)[-1] == ".bt"]
        select_account.addItems(account_files)
        select_account.currentTextChanged.connect(self.onBacktestRunAccountChanged2)
        select_account.setCurrentIndex(0)

        open_type_list = backtest.findChild(QComboBox, "open_type")
        open_type_list.currentIndexChanged.connect(lambda event: self.onOpenTypeChanged(event))

        start_button = backtest.findChild(QPushButton)
        start_button.clicked.connect(lambda event:self.onBacktestRun())
        self.backtest = backtest

    def onResultTreeDoubleClicked(self, item, column):
        text = item.text(column)
        whats_this = item.whatsThis(column)
        if text == "资产":
            data = pd.DataFrame(self.cashs)
            data.index = data.date
            GridView(self.parent, "资产详情", data)
        if whats_this == "position":
            id = item.parent().text(column)
            data = self.positions[id][text]
            data = pd.DataFrame(data)
            GridView(self.parent, "%s 的仓位详情" % id, data, hidden_columns=["account_id", "short_name"])
        elif whats_this == "order":
            id = item.parent().text(column)
            data = self.orders[id][text][0]
            loader = QUiLoader()
            order_status = loader.load('order_status.ui', parentWidget=self.parent_widget)
            order_status.setWindowTitle("订单状态")
            sec_id = order_status.findChild(QLineEdit, "sec_id")
            sec_id.setText(data[0].sec_id)

            order_type = order_status.findChild(QLineEdit, "order_type")
            order_type.setText(str(data[0].order_type))

            position_effect = order_status.findChild(QLineEdit, "position_effect")
            position_effect.setText(str(data[0].position_effect))

            side = order_status.findChild(QLineEdit, "side")
            side.setText(str(data[0].side))

            sending_time = order_status.findChild(QDateEdit, "sending_time")
            sending_time.setDate(QtCore.QDate.fromString(data[0].sending_time, "yyyy-MM-dd 00:00:00"))

            transact_time = order_status.findChild(QDateEdit, "transact_time")
            transact_time.setDate(QtCore.QDate.fromString(data[1].transact_time, "yyyy-MM-dd 00:00:00"))

            price = order_status.findChild(QDoubleSpinBox, "price")
            price.setValue(data[0].price)

            res_price = order_status.findChild(QDoubleSpinBox, "res_price")
            res_price.setValue(data[1].price)

            amount = order_status.findChild(QDoubleSpinBox, "amount")
            amount.setValue(data[1].amount)

            res_volume = order_status.findChild(QSpinBox, "res_volume")
            res_volume.setValue(abs(data[1].volume))

            volume = order_status.findChild(QSpinBox, "volume")
            volume.setValue(abs(data[0].volume))

            status = order_status.findChild(QLineEdit, "status")
            status.setText(str(data[1].ord_rej_reason))

            reason = order_status.findChild(QLineEdit, "reason")
            reason.setText(data[1].ord_rej_reason_detail)

            subWindow = QMdiSubWindow()
            subWindow.setAttribute(Qt.WA_DeleteOnClose)
            subWindow.setWidget(order_status)
            self.mdi_area.addSubWindow(subWindow)

            order_status.show()

    def onOpenTypeChanged(self, value):
        self.config["open_type"]["value"] = value

    def onBacktestRunAccountChanged2(self, value):
        # file_name = os.path.normpath(os.path.join(self.root, "accounts", "%s.bt" % value))
        # with open(file_name, "rb") as f:
        #     data = pickle.load(f)
        #     self.config["account"] = data
        #     self.tc = tradeCenter.TradeCenter(data)
        pass

    def onBacktestRun(self):

        self.beforeRun()
        start_date = self.backtest.findChild(QDateEdit, "start_date").date()
        end_date = self.backtest.findChild(QDateEdit, "end_date").date()
        current_date = start_date
        process_bar = self.backtest.findChild(QProgressBar)
        if start_date >= end_date:
            self.parent.messageBox("开始时间必须小于结束时间")
            return
        days = start_date.daysTo(end_date)
        process_bar.reset()
        process_bar. setRange(0, days)
        count = 1
        while end_date > current_date:
            current_date = current_date.addDays(1)
            current_date_str = current_date.toString("yyyy-MM-dd 00:00:00")
            process_bar.setValue(count)
            table = "option/underlyings/510050.XSHG"
            tick = sql.read(table, where="date='%s'" % current_date_str)
            if tick.empty:
                # 当前日期不是交易日，跳过
                count += 1
                continue
            # 先处理手动订单
            self.__handleManualOrder(current_date_str)
            # 在处理自动订单
            option = self.config["options"]
            if option["enable"] == 1 or option["enable"] == 0:
                underlyings = option["underlyings"]
                for underlying in underlyings:
                    id = underlying["id"]["list"][underlying["id"]["value"]]
                    sub_window = self.parent.getSubWindowByAttribute("btId", id)
                    data = sub_window.btData
                    row = data[data.date == current_date_str]
                    row = row.T.squeeze()
                    if row.empty:
                        continue
                    if underlying["signal"]["list"] == []:
                        self.parent.messageBox("标的%s没有绑定的信号" % id)
                        return
                    underlying_signal_column = underlying["signal"]["list"][underlying["signal"]["value"]]
                    underlying_signal = int(row[underlying_signal_column])
                    self.__handleOptionUnderlyingTick(id, row, underlying_signal, underlying)
                    groups = underlying["groups"]
                    if groups:
                        table = "option/contract"
                        contract_dataframe = sql.read(table, where="underlying_order_book_id='%s'" % id)
                        for group in groups:
                            group_contract = group["contracts"]
                            for contract in group_contract:
                                self.__handleOptionContractTick(id, row, underlying_signal, contract_dataframe, contract, option_underlying_setting=underlying,
                                                                option_group_setting=group)
            self.updateMarket()
            self.updatePosition(current_date_str)
            self.updateCash(current_date_str)
            self.updatePerformance()
            count += 1
        self.afterRun()
        return

    def beforeRun(self):

        self.orders = {}
        self.positions = {}
        self.cashs = {}
        self.label_text = {}
        self.option_filter_dict = {}

        account_name = self.backtest.findChild(QComboBox, "account").currentText()
        file_name = os.path.normpath(os.path.join(self.root, "accounts", "%s.bt" % account_name))
        with open(file_name, "rb") as f:
            data = pickle.load(f)
            self.config["account"] = data
            self.tc = tradeCenter.TradeCenter(data)
        result_tree = self.backtest.findChild(QTreeWidget)
        result_tree.clear()

    def afterRun(self):
        result_tree = self.backtest.findChild(QTreeWidget)

        for text in ["资产", "仓位", "订单"]:
            item = QTreeWidgetItem(result_tree)
            item.setText(0, text)

        position_dataframe = pd.DataFrame()
        positions = self.positions.keys()
        position_item = result_tree.topLevelItem(1)
        for id in positions:
            id_item = QTreeWidgetItem(position_item)
            id_item.setText(0, id)
            for date in self.positions[id].keys():
                date_item = QTreeWidgetItem(id_item)
                date_item.setText(0, date)
                date_item.setWhatsThis(0, "position")
                if position_dataframe.empty:
                    position_dataframe = pd.DataFrame(self.positions[id][date])
                else:
                    position_dataframe = position_dataframe.append(pd.DataFrame(self.positions[id][date]), ignore_index=True, sort=True)

        order_item = result_tree.topLevelItem(2)
        orders = self.orders.keys()
        for order_id in orders:
            id_item = QTreeWidgetItem(order_item)
            id_item.setText(0, order_id)
            for order_date in self.orders[order_id].keys():
                date_item = QTreeWidgetItem(id_item)
                date_item.setText(0, order_date)
                date_item.setWhatsThis(0, "order")

        self.tc.performance.max_drawdown = round(self._get_max_drawdown(self.cashs["nav"]), 2)
        self.backtest.findChild(QLineEdit, "init_capital").setText(str(self.tc.performance.init_capital))
        self.backtest.findChild(QLineEdit, "profit_ratio").setText(str(self.tc.performance.profit_ratio))
        self.backtest.findChild(QLineEdit, "win_count").setText(str(self.tc.performance.win_count))
        self.backtest.findChild(QLineEdit, "lose_count").setText(str(self.tc.performance.lose_count))
        self.backtest.findChild(QLineEdit, "win_ratio").setText(str(self.tc.performance.win_ratio))
        self.backtest.findChild(QLineEdit, "average_win").setText(str(self.tc.performance.average_win))
        self.backtest.findChild(QLineEdit, "average_loss").setText(str(self.tc.performance.average_loss))
        self.backtest.findChild(QLineEdit, "max_draw_down").setText(str(self.tc.performance.max_drawdown))
        self.backtest.findChild(QLineEdit, "win_loss").setText(str(self.tc.performance.win_loss))
        self.backtest.findChild(QLineEdit, "final_capital").setText(str(self.tc.performance.final_capital))
        # self.backtest.findChild(QLineEdit, "performance_indicator").setText(str(performance_indicator))

        self.tc = None

    def updateMarket(self):
        self.tc.cash.fpnl = 0
        self.tc.cash.nav = self.tc.cash.available

    def updateCash(self, date):
        self.tc.cash.date = date
        for i in self.tc.cash.__dict__.keys():
            if i.startswith("_"):
                continue
            key = self.cashs.get(i, None)
            if key:self.cashs[i].append(self.tc.cash.__dict__[i])
            else:self.cashs[i] = [self.tc.cash.__dict__[i]]

    def updatePosition(self, date):
        for id in self.tc.optionUnderlyingPosition.copy():
            position = self.tc.optionUnderlyingPosition[id]
            table = "option/underlyings/%s" % id
            tick = sql.read(table, select="close", where="date='%s'" % date)
            if tick.empty:
                continue
            close = tick.at[0, "close"]
            self._updateOptionUnderlyingPosition(id, close, date, position)
            if position.volume == 0:
                self.tc.optionUnderlyingPosition.pop(id)
        for id in self.tc.optionContractPosition.copy():
            position = self.tc.optionContractPosition[id]
            table = "option/contracts/%s" % id
            tick = sql.read(table, select="close", where="date='%s'" % date)
            if tick.empty:
                continue
            close = tick.at[0, "close"]
            self._updateOptionContractPosition(id, close, date, position)
            if position.volume == 0:
                self.tc.optionContractPosition.pop(id)

    def _updateOptionContractPosition(self, id, close, date, position):
        position.cum_cost = position.cost + position.deposit_cost + position.commission + position.slide_cost
        position.fpnl = (close * position.volume * 10000) - (position.cum_cost)
        position.price = close
        position.date = date
        position.available_today = position.volume
        position.available = position.volume
        if position.volume == 0:
            self.tc.cash.fpnl += position.pnl
            position.fpnl = position.pnl
        else:
            self.tc.cash.fpnl += position.fpnl
            self.tc.cash.nav += (position.price * position.volume * 10000)

        positions = self.positions.get(id, {})
        _position = positions.get(position.init_time, {})
        for i in position.__dict__.keys():
            key = _position.get(i, None)
            if key:
                _position[i].append(position.__dict__[i])
            else:
                _position[i] = [position.__dict__[i]]
        if position.init_time not in positions:
            if id not in self.positions:
                self.positions[id] = {position.init_time: _position}
            else:
                self.positions[id][position.init_time] = _position

    def _updateOptionUnderlyingPosition(self, id, close, date, position):

        position.fpnl = (close * position.volume) - (position.cum_cost)
        position.price = close
        position.date = date
        position.available_today = position.volume
        position.available = position.volume
        if position.volume == 0:
            self.tc.cash.fpnl += position.pnl
            position.fpnl = position.pnl
        else:
            self.tc.cash.fpnl += position.fpnl
            self.tc.cash.nav += (position.price * position.volume)

        positions = self.positions.get(id, {})
        _position = positions.get(position.init_time, {})
        for i in position.__dict__.keys():
            key = _position.get(i, None)
            if key:
                _position[i].append(position.__dict__[i])
            else:
                _position[i] = [position.__dict__[i]]
        if position.init_time not in positions:
            if id not in self.positions:
                self.positions[id] = {position.init_time: _position}
            else:
                self.positions[id][position.init_time] = _position

    def updatePerformance(self):
        self.tc.performance.init_capital = round(self.tc.cash._nav, 2)
        self.tc.performance.final_capital = round(self.tc.cash.nav, 2)
        self.tc.performance.profit_ratio = round((self.tc.performance.final_capital - self.tc.performance.init_capital) / self.tc.performance.init_capital, 2) * 100
        win_count = self.tc.performance.win_count
        lose_count = self.tc.performance.lose_count
        if win_count > 0 or lose_count > 0:
            self.tc.performance.win_ratio = round(win_count / (win_count + lose_count), 2) * 100
            if win_count > 0:
                self.tc.performance.average_win = round(self.tc.performance.total_win / win_count, 2)
            if lose_count > 0:
                self.tc.performance.average_lose = round(self.tc.performance.total_loss / lose_count, 2)
                if self.tc.performance.average_loss:
                    self.tc.performance.win_loss = round(self.tc.performance.average_win / self.tc.performance.average_loss, 2)
        # performance_indicator = profit_ration / self.tc.performance.max_draw_down
        # performance_level = self.get_performance_level(performance_indicator)

    def select_option(self, underlying_tick, option_info, **params):
        options = pd.DataFrame()
        current_date = underlying_tick.date
        info_frame = self.select_option_by_info(underlying_tick, option_info, **params)
        if info_frame.empty:
            return options
        if len(info_frame.index) > 1:
            risk_frame = self.select_option_by_risk(underlying_tick, info_frame, **params)
        else:
            risk_frame = info_frame

        d = risk_frame
        sec_ids = list(d.order_book_id)
        for i in range(len(sec_ids)):
            sec_id = sec_ids[i]
            table = "option/contracts/%s" % sec_id
            data = sql.read(table, where="date='%s'" % current_date)
            data["order_book_id"] = sec_id
            if options.empty:
                options = data
            else:
                options.append(data, ignore_index=True)
        options = options.merge(d, on="order_book_id", how="inner", suffixes=('_',''))
        return options

    def select_option_by_info(self, underlying_tick, option_dataframe, **params):

        current_date = underlying_tick.date
        smart_selection = params["smart_selection"].get("value")
        change_condition = params["change_condition"].get("value")
        option_type = params["option_type"].get("value")
        month_interval = params["month_interval"].get("value")
        strike_interval = params["strike_interval"].get("value")
        if change_condition == 0:
            close_price = underlying_tick.close
        else:
            close_price = underlying_tick.open
        strike_interval_string = setting.OPTION_STRIKE_INTERVAL[strike_interval]
        strike_match = re.search(r"\d", strike_interval_string)
        if strike_match:
            strike_symbol_match = re.search(u"高", strike_interval_string)
            if strike_symbol_match:
                strike_interval = int(strike_match.group(0)) * 1
            else:
                strike_interval = int(strike_match.group(0)) * -1
        else:
            strike_interval = 0
        option_dataframe = option_dataframe[option_dataframe.listed_date <= current_date]
        option_dataframe = option_dataframe[option_dataframe.maturity_date > current_date]
        if option_type == 0:
            option_dataframe = option_dataframe[option_dataframe.option_type == "C"]
        elif option_type == 1:
            option_dataframe = option_dataframe[option_dataframe.option_type == "P"]
        if month_interval is not None:
            option_dataframe = option_dataframe.sort_values("maturity_date", axis=0)
            exp_date, group = list(option_dataframe.groupby("maturity_date"))[month_interval]
            option_dataframe = option_dataframe[option_dataframe.maturity_date == exp_date]
        if option_dataframe.empty:
            return pd.DataFrame()
        if strike_interval_string != "":
            option_dataframe = self.__filter_by_interval(option_dataframe, strike_interval, close_price, smart_selection)
        return option_dataframe

    def __filter_by_interval(self, data_frame, strike_interval, close_price, smart_selection):
        d = data_frame
        if strike_interval > 0:
            d = d[d.strike_price > close_price]
            if d.empty and smart_selection:
                return self.__filter_by_interval(data_frame, -1, close_price, smart_selection)
            d = d.sort_values("strike_price", axis=0)
            d.index = [i+1 for i in range(len(d.index))]
            if strike_interval > max(d.index) and smart_selection:
                strike_interval = max(d.index)
            d = d[d.index == abs(strike_interval)]
        elif strike_interval < 0:
            strike_interval = abs(strike_interval)
            d = d[d.strike_price < close_price]
            if d.empty and smart_selection:
                return self.__filter_by_interval(data_frame, 1, close_price, smart_selection)
            d = d.sort_values("strike_price", ascending=False, axis=0)
            d.index = [i+1 for i in range(len(d.index))]
            if strike_interval > max(d.index) and smart_selection:
                strike_interval = max(d.index)
            d = d[d.index == strike_interval]
        else:
            d["close_price_filter"] = np.abs(d.strike_price - float(close_price))
            d = d.sort_values(by="close_price_filter")
            d.index = [i for i in range(len(d.index))]
            d = d[d.index == 0]
        return d

    def select_option_by_risk(self, underlying_tick, option_dataframe, **params):

        optID = None
        current_date = underlying_tick.tradeDate
        delta = params["delta"].get("value")
        gamma = params["gamma"].get("value")
        rho = params["rho"].get("value")
        theta = params["theta"].get("value")
        vega = params["vega"].get("value")
        ivix = params["ivix"].get("value")
        table_name = "/option_risk"
        if not sql.is_table(table_name):
            return pd.DataFrame()
        option_risk_frame = sql.read(table_name)
        option_risk_frame = option_risk_frame[option_risk_frame.tradeDate==current_date]
        if not option_dataframe.empty:
            option_risk_frame = option_risk_frame.loc[:, ["Delta", "Gamma", "Rho", "Theta", "Vega", "optID", "ivix"]]
            option_risk_frame = pd.merge(option_risk_frame, option_dataframe, "optID")
        else:
            option_risk_frame["secID"] = option_risk_frame.ticker + ".XSHG"
        if delta:
            option_risk_frame["delta_filter"] = np.abs(option_risk_frame.Delta - float(delta))
            option_risk_frame = option_risk_frame.sort_values(by="delta_filter")
            optID = list(option_risk_frame.optID)[0]
        if gamma:
            option_risk_frame["gamma_filter"] = np.abs(option_risk_frame.Gamma - float(gamma))
            option_risk_frame = option_risk_frame.sort_values(by="gamma_filter")
            optID = list(option_risk_frame.optID)[0]
        if rho:
            option_risk_frame["rho_filter"] = np.abs(option_risk_frame.Rho - float(rho))
            option_risk_frame = option_risk_frame.sort_values(by="rho_filter")
            optID = list(option_risk_frame.optID)[0]
        if theta:
            option_risk_frame["theta_filter"] = np.abs(option_risk_frame.Theta - float(theta))
            option_risk_frame = option_risk_frame.sort_values(by="theta_filter")
            optID = list(option_risk_frame.optID)[0]
        if vega:
            option_risk_frame["vega_filter"] = np.abs(option_risk_frame.Vega - float(vega))
            option_risk_frame = option_risk_frame.sort_values(by="vega_filter")
            optID = list(option_risk_frame.optID)[0]
        if ivix:
            option_risk_frame["ivix_filter"] = np.abs(option_risk_frame.ivix - float(ivix))
            option_risk_frame = option_risk_frame.sort_values(by="ivix_filter")
            optID = list(option_risk_frame.optID)[0]
        if optID:
            option_risk_frame = option_risk_frame[option_risk_frame.optID == optID]
            return option_risk_frame
        else:
            return option_dataframe

    def __handleManualOrder(self, date):
        if not hasattr(self.parent, "manual_order_tree"):
            return
        open_type = self.config["open_type"]["value"]
        order_tree = self.parent.manual_order_tree
        count = order_tree. topLevelItemCount()
        for index in range(count):
            item = order_tree.topLevelItem(index)
            send_date_text = item.text(0)
            if send_date_text != date:
                continue
            underlying_id_text = item.text(1)
            contract_id_text = item.text(2)
            position_effect_text = item.text(3)
            side_text = item.text(4)
            order_type_text = item.text(5)
            volume = int(item.text(6))

            if order_type_text == "期权标的":
                table = "option/underlyings/%s" % underlying_id_text
                tick = sql.read(table, where="date='%s'" % date)
                tick = tick.T.squeeze()
                if position_effect_text == "开仓" and side_text == "买入":
                    if open_type == 0:
                        volume = volume
                    elif open_type == 1:
                        volume = int(volume / tick.close)
                    elif open_type == 2:
                        ratio = volume / 100
                        ratio = 1 if ratio > 1 else ratio
                        volume = int((ratio * self.tc.cash.available / tick.close))
                    self.buy_option_underlying(underlying_id_text, volume, tick)
                if position_effect_text == "平仓" and side_text == "卖出":
                    if open_type == 0:
                        volume = volume
                    else:
                        position = self.tc.optionUnderlyingPosition.get(underlying_id_text, None)
                        if position:
                            ratio = volume / 100
                            ratio = 1 if ratio > 1 else ratio
                            volume = int(position.volume * ratio)
                    self.sell_option_underlying(underlying_id_text, volume, tick)
            elif order_type_text == "期权合约":
                contracts_table = "option/contract"
                contract_table = "option/contracts/%s" % contract_id_text
                underlying_table = "option/underlyings/%s" % underlying_id_text

                contract_tick = sql.read(contract_table, where="date='%s'" % date)
                contract_tick = contract_tick.T.squeeze()

                contracts_tick = sql.read(contracts_table, where="order_book_id='%s'" % contract_id_text)
                contracts_tick = contracts_tick.T.squeeze()

                underlying_tick = sql.read(underlying_table, where="date='%s'" % date)
                underlying_tick = underlying_tick.T.squeeze()

                contract_tick = contract_tick.append(contracts_tick)
                contract_tick.change_feq = ""
                contract_setting = {
                        "close_method":{
                            "value": 0
                        },
                        "volume": {
                            "value":volume
                        },
                        "deposit_coefficient":{
                            "value": 0
                        },
                        "change_condition":{
                            "value": 0
                        }
                        }
                deposit_coefficient = contract_setting["deposit_coefficient"]["value"]
                if position_effect_text == "开仓":
                    if side_text == "买入":
                        if open_type == 0:
                            volume = int(volume)
                        elif open_type == 1:
                            volume = int((float(volume) / (contract_tick.close * 10000)))
                        elif open_type == 2:
                            volume = 1 if volume > 1 else volume
                            volume = int((volume * self.tc.cash.available / (contract_tick.close * 10000)))
                        self.buy_option_contract(underlying_tick, contract_tick, contract_setting, volume)
                    if side_text == "卖出":
                        if open_type == 0:
                            volume = int(volume)
                        elif open_type == 1:
                            _option_volume = 0
                            if contract_tick.option_type == 0:
                                while self.tc.call_option_cash_deposit(contract_tick.strike_price, underlying_tick.close,
                                                                       contract_tick.settlPrice, abs(
                                            _option_volume * 10000)) * deposit_coefficient < volume:
                                    _option_volume += 1
                            elif contract_tick.option_type == 1:
                                while self.tc.put_option_cash_deposit(contract_tick.strike_price, underlying_tick.close,
                                                                      contract_tick.settlPrice, abs(
                                            _option_volume * 10000)) * deposit_coefficient < volume:
                                    _option_volume += 1
                            volume = _option_volume - 1
                        elif open_type == 2:
                            option_ratio = float(volume) / 100
                            option_ratio = 1 if option_ratio > 1 else option_ratio
                            _option_volume = 0
                            volume = option_ratio * self.tc.cash.available
                            if contract_tick.option_type == 0:
                                while self.tc.call_option_cash_deposit(contract_tick.strike_price, underlying_tick.close,
                                                                       contract_tick.settlPrice, abs(
                                                _option_volume * 10000)) * deposit_coefficient < volume:
                                        _option_volume += 1
                            elif contract_tick.option_type == 1:
                                while self.tc.put_option_cash_deposit(contract_tick.strike_price,
                                                                      underlying_tick.close, contract_tick.settlPrice, abs(
                                                _option_volume * 10000)) * deposit_coefficient < volume:
                                        _option_volume += 1
                            volume = _option_volume - 1
                        self.short_option_contract(underlying_tick, contract_tick, contract_setting, volume)
                if position_effect_text == "平仓":
                    if open_type == 0:
                        volume = int(volume)
                    else:
                        position = self.tc.optionContractPosition.get(contract_id_text, None)
                        if position:
                            ratio = volume / 100
                            ratio = 1 if ratio > 1 else ratio
                            volume = int(ratio * position.volume)
                    if side_text == "卖出":
                        self.sell_option_contract(underlying_tick, contract_tick, contract_setting, volume)
                    elif side_text == "买入":
                        self.cover_option_contract(underlying_tick, contract_tick, contract_setting, volume)

    def __handleOptionUnderlyingTick(self, id, row, signal, underlying_config):
        open_type = self.config["open_type"]["value"]
        if signal == 1:
            #买入
            volume = underlying_config["volume"]["value"]
            if open_type == 0:
                volume = volume
            elif open_type == 1:
                volume = int(volume/row.close)
            elif open_type == 2:
                ratio = underlying_config["ratio"]["value"]/100
                ratio = ratio * (volume/100)
                volume = int((ratio * self.tc.cash.available / row.close))
            self.buy_option_underlying(id, volume, row)
        elif signal == -1:
            #卖出
            position = self.tc.optionUnderlyingPosition.get(id, None)
            if position:
                volume = position.volume
                self.sell_option_underlying(id, volume, row)

    def __handleOptionContractTick(self, id, tick, signal, option_dataframe, option_contract_setting,
                                   option_group_setting={},
                                   option_underlying_setting={},
                                   option_setting={}):
        open_type = self.config["open_type"]["value"]
        # close_type = option_contract_setting["close_type"]["value"]
        option_type = option_contract_setting["option_type"]["value"]
        close_method = option_contract_setting["close_method"]["value"]
        option_side = option_contract_setting["option_side"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        change_feq = option_contract_setting["change_feq"]["value"]
        if signal == 1:
            option_volume = option_contract_setting["volume"]["value"]
            var_price_type = change_condition
            options = self.select_option(tick, option_dataframe, **option_contract_setting)
            for j in options.index:
                option = options.loc[j]
                if not change_feq:
                    change_feq = None
                if open_type == 0:
                    option_volume = int(option_volume)
                elif open_type == 1:
                    if option_side == 0:
                        option_volume = self.tc.cal_option_contract_volume(float(option_volume), option.close)
                    elif option_side == 1:
                        _option_volume = 0
                        if option_type == 0:
                            while self.tc.call_option_cash_deposit(option.strike_price, tick.close,
                    option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                                _option_volume += 1
                        elif option_type == 1:
                            while self.tc.put_option_cash_deposit(option.strike_price, tick.close,
                    option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                                _option_volume += 1
                        option_volume = _option_volume - 1
                elif open_type == 2:
                    option_ratio = float(option_underlying_setting["ratio"]["value"])/100
                    option_ratio = option_ratio * (float(option_group_setting["ratio"]["value"])/100)
                    option_ratio = option_ratio * (float(option_volume)/100)
                    if option_side == 0:
                        option_volume = self.tc.cal_option_contract_volume(option_ratio*self.tc.cash.available, option.close)
                    elif option_side == 1:
                        _option_volume = 0
                        option_volume = option_ratio*self.tc.cash.available
                        if option_type == 0:
                            while self.tc.call_option_cash_deposit(option.strike_price, tick.close,
                    option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                                _option_volume += 1
                        elif option_type == 1:
                            while self.tc.put_option_cash_deposit(option.strike_price,
                    tick.close, option.settlPrice, abs(_option_volume*10000)) * deposit_coefficient < option_volume:
                                _option_volume += 1
                        option_volume = _option_volume - 1
                option.change_feq = change_feq
                #option_contract_setting["volume"]["value"] = option_volume
                if option_side == 0:
                    self.buy_option_contract(tick, option, option_contract_setting, option_volume)
                elif option_side == 1:
                    self.short_option_contract(tick, option, option_contract_setting, option_volume)
        elif signal == -1:
            for id in option_contract_setting["ids"]:
                position = self.tc.optionContractPosition.get(id, None)
                volume = position.volume
                if position:
                    tick_table = "option/contracts/%s" % id
                    contract_table = "option/contract"
                    contract_dataframe = sql.read(contract_table, where="order_book_id='%s'" % id)
                    option_tick = sql.read(tick_table, where="date='%s'" % tick.date)
                    option_tick["order_book_id"] = id
                    option = contract_dataframe.merge(option_tick, on="order_book_id", how="inner", suffixes=('_',''))
                    option = option.T.squeeze()
                    if option_side == 0:
                        self.sell_option_contract(tick, option, option_contract_setting, volume)
                    elif option_side == 1:
                        self.cover_option_contract(tick, option, option_contract_setting, volume)
        elif signal == 0:
            for id in option_contract_setting["ids"]:
                contract_dataframe = option_dataframe[option_dataframe["order_book_id"] == id]
                contract_dataframe = contract_dataframe.T.squeeze()
                if tick.date[:10] == contract_dataframe.maturity_date:
                    position = self.tc.optionContractPosition.get(id, None)
                    tick_table = "option/contracts/%s" % id
                    option_tick = sql.read(tick_table, where="date='%s'" % tick.date)
                    option_tick = option_tick.T.squeeze()
                    option = contract_dataframe.append(option_tick)
                    if close_method == 0:
                        # 按照交易信号平仓，需要换仓

                        volume = position.volume
                        if option_side == 0:
                            self.sell_option_contract(tick, option, option_contract_setting, volume)
                        elif option_side == 1:
                            self.cover_option_contract(tick, option, option_contract_setting, volume)

                        options = self.select_option(tick, option_dataframe, **option_contract_setting)
                        option_volume = option_contract_setting["volume"]["value"]
                        for j in options.index:
                            option = options.loc[j]
                            if not change_feq:
                                change_feq = None
                            if open_type == 0:
                                option_volume = int(option_volume)
                            elif open_type == 1:
                                if option_side == 0:
                                    option_volume = self.tc.cal_option_contract_volume(float(option_volume),
                                                                                       option.close)
                                elif option_side == 1:
                                    _option_volume = 0
                                    if option_type == 0:
                                        while self.tc.call_option_cash_deposit(option.strike_price, tick.close,
                                                                               option.settlPrice, abs(
                                                    _option_volume * 10000)) * deposit_coefficient < option_volume:
                                            _option_volume += 1
                                    elif option_type == 1:
                                        while self.tc.put_option_cash_deposit(option.strike_price, tick.close,
                                                                              option.settlPrice, abs(
                                                    _option_volume * 10000)) * deposit_coefficient < option_volume:
                                            _option_volume += 1
                                    option_volume = _option_volume - 1
                            elif open_type == 2:
                                option_ratio = float(option_underlying_setting["ratio"]["value"]) / 100
                                option_ratio = option_ratio * (float(option_group_setting["ratio"]["value"]) / 100)
                                option_ratio = option_ratio * (float(option_volume) / 100)
                                if option_side == 0:
                                    option_volume = self.tc.cal_option_contract_volume(
                                        option_ratio * self.tc.cash.available, option.close)
                                elif option_side == 1:
                                    _option_volume = 0
                                    option_volume = option_ratio * self.tc.cash.available
                                    if option_type == 0:
                                        while self.tc.call_option_cash_deposit(option.strike_price, tick.close,
                                                                               option.settlPrice, abs(
                                                    _option_volume * 10000)) * deposit_coefficient < option_volume:
                                            _option_volume += 1
                                    elif option_type == 1:
                                        while self.tc.put_option_cash_deposit(option.strike_price,
                                                                              tick.close, option.settlPrice, abs(
                                                    _option_volume * 10000)) * deposit_coefficient < option_volume:
                                            _option_volume += 1
                                    option_volume = _option_volume - 1
                            option.change_feq = change_feq
                            if option_side == 0:
                                self.buy_option_contract(tick, option, option_contract_setting, option_volume)
                            elif option_side == 1:
                                self.short_option_contract(tick, option, option_contract_setting, option_volume)
                            #TODO

                    elif close_method == 1:
                        #按到期日平仓，需要检查当前日期是否是到期日
                        #平仓
                        if option_side == 0:
                            self.sell_option_contract(tick, option, option_contract_setting)
                        elif option_side == 1:
                            self.cover_option_contract(tick, option, option_contract_setting)

    def buy_option_underlying(self, id, volume, tick):
        if volume <= 0:
            return
        order = setting.Order()
        order.sec_id = id
        order.order_type = "stock"
        order.price = tick.close
        order.volume = volume
        order.position_effect = setting.PositionEffect_Open
        order.side = setting.OrderSide_Bid
        order.sending_time = tick.date
        self.__save_order(order, self.tc.onOptionUnderlyingOrder(order))

    def sell_option_underlying(self, id, volume, tick):
        if volume <= 0:
            return
        order = setting.Order()
        order.sec_id = id
        order.order_type = "stock"
        order.price = tick.close
        order.volume = volume
        order.position_effect = setting.PositionEffect_Close
        order.side = setting.OrderSide_Ask
        order.sending_time = tick.date
        self.__save_order(order, self.tc.onOptionUnderlyingOrder(order))

    def __save_order(self, order, response):
        if order.sec_id in self.orders:
            order_id = self.orders[order.sec_id]
            if order.sending_time in order_id:
                order_id[order.sending_time].append((order, response))
            else:
                order_id[order.sending_time] = [(order, response)]
        else:
            self.orders[order.sec_id] = {
                order.sending_time: [(order, response)]
            }

    def buy_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting, volume):
        close_method = option_contract_setting["close_method"]["value"]
        #volume = option_contract_setting["volume"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.change_feq = option_contract_tick.change_feq
        order.var_price = option_underlying_tick.open if change_condition == 1 else option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * 1
        order.position_effect = setting.PositionEffect_Open
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Bid
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        order.deposit_coefficient = deposit_coefficient
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            option_contract_setting["ids"] = [order.sec_id]
        self.__save_order(order, response)

    def short_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting, volume):
        close_method = option_contract_setting["close_method"]["value"]
        #volume = option_contract_setting["volume"]["value"]
        deposit_coefficient = option_contract_setting["deposit_coefficient"]["value"]
        change_condition = option_contract_setting["change_condition"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.change_feq = option_contract_tick.change_feq
        order.var_price = option_underlying_tick.open if change_condition == 1 else option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * -1
        order.position_effect = setting.PositionEffect_Open
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Ask
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        order.deposit_coefficient = deposit_coefficient
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            if "ids" in option_contract_setting:
                option_contract_setting["ids"] = [order.sec_id]
        self.__save_order(order, response)

    def sell_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting, volume):
        close_method = option_contract_setting["close_method"]["value"]
        #volume = option_contract_setting["volume"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.var_price = option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * -1
        order.position_effect = setting.PositionEffect_Close
        order.expiration_date = option_contract_tick.maturity_date
        order.close_method = close_method
        order.side = setting.OrderSide_Ask
        order.sending_time = option_underlying_tick.date
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            if "ids" in option_contract_setting:
                option_contract_setting["ids"].remove(order.sec_id)
        self.__save_order(order, response)

    def cover_option_contract(self, option_underlying_tick, option_contract_tick, option_contract_setting, volume):
        close_method = option_contract_setting["close_method"]["value"]
        # volume = option_contract_setting["volume"]["value"]
        order = setting.Order()
        order.sec_id = option_contract_tick.order_book_id
        order.order_type = "option_contract"
        order.var_sec_id = option_contract_tick.underlying_order_book_id
        order.var_price = option_underlying_tick.close
        order.contract_type = option_contract_tick.option_type
        order.price = option_contract_tick.close
        order.strike_price = option_contract_tick.strike_price
        # order.settle_price = option_contract_tick.settlement
        order.volume = volume * 1
        order.position_effect = setting.PositionEffect_Close
        order.expiration_date = option_contract_tick.maturity_date
        order.side = setting.OrderSide_Bid
        order.close_method = close_method
        order.sending_time = option_underlying_tick.date
        response = self.tc.onOptionContractOrder(order)
        if response.ord_rej_reason == 0:
            option_contract_setting["ids"].remove(order.sec_id)
        self.__save_order(order, response)

    def short(self, volume, tick):
        pass

    def cover(self, volume, tick):
        pass

    def _get_max_drawdown(self, array):
        drawdowns = []
        max_so_far = array[0]
        for i in range(len(array)):
            if array[i] > max_so_far:
                drawdown = 0
                drawdowns.append(drawdown)
                max_so_far = array[i]
            else:
                drawdown = max_so_far - array[i]
                drawdowns.append(drawdown)
        return max(drawdowns)

    def _get_performance_level(self, indicator):
        index = 0
        if indicator < 0:
            return u"没有等级，还需努力哦"
        elif indicator<=1:
            index = 0
        elif 1<indicator<=3:
            index = 1
        elif 3<indicator<=6:
            index = 2
        elif 6<indicator<=9:
            index = 3
        elif 9<indicator<=13:
            index = 4
        elif 13<indicator<=17:
            index = 5
        elif 17<indicator<=20:
            index = 6
        elif 20<indicator<=30:
            index = 7
        elif 30<indicator<=40:
            index = 8
        elif 40<indicator<=50:
            index = 9
        elif indicator>50:
            index = 10
        return setting.PERFORMANCE_LEVEL[index]