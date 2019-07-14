# encoding: utf-8

import pandas as pd

from PySide2.QtWidgets import QTreeWidgetItem,\
    QAction, QComboBox, QLineEdit, \
    QTreeWidget, QSpinBox,\
    QMenu, QDoubleSpinBox, QGroupBox, QVBoxLayout, QInputDialog
from PySide2.QtCore import Qt
from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader

from libs.windows.grid_view import GridView
from src import setting

class SemiAutoSignal():
    def __init__(self, widget, main_widget, config, delete_backtest_tree_item, add_option_underlying,
                                  add_option_group, add_option_contract, no_support):
        self.parent = main_widget

        self.config = config
        self.mdi_area = self.parent.mdi_area
        self.root = self.parent.root
        self.group_box_widgets = []
        backtest = widget
        self.backtest = backtest

        self.add_option_underlying = add_option_underlying
        self.add_option_group = add_option_group
        self.add_option_contract = add_option_contract
        self.no_support = no_support


        self.group_box = backtest.findChild(QGroupBox, "backtest_box")
        self.group_box_layout = QVBoxLayout()
        self.group_box.setLayout(self.group_box_layout)
        self.backtest_tree = backtest.findChild(QTreeWidget, "backtest_tree")
        self.backtest_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.backtest_tree.topLevelItem(0).setExpanded(True)

        add_option_underlying.triggered.connect(self.onAddOptionUnderlying)
        add_option_group.triggered.connect(self.onAddOptionGroup)
        add_option_contract.triggered.connect(self.onAddOptionContract)
        self.backtest_tree.itemDoubleClicked.connect(self.onBackTestTreeDoubleClicked)
        self.backtest_tree.customContextMenuRequested.connect(lambda event: self.onBackTestTreeRightClicked())

        delete_backtest_tree_item.triggered.connect(self.onDeleteBackTestTreeItem)

        self.loadBacktestTree()

    def loadBacktestTree(self):
        options = self.config.get("options", {})
        underlyings = options.get("underlyings", [])

        for i in range(1):
            item = self.backtest_tree.topLevelItem(i)
            item.setExpanded(True)
            for j in range(item.childCount()):
                child_item = item.child(j)
                child_item.setExpanded(True)
                whatsthis = child_item.whatsThis(0)
                if whatsthis == "option":
                    for underlying in underlyings:
                        current_item = child_item
                        node = QTreeWidgetItem(current_item)
                        node.setText(0, underlying["name"])
                        node.setCheckState(0, Qt.Unchecked)
                        node.setWhatsThis(0, "option_underlying")
                        node.setExpanded(True)

                        data = underlying.get("id", {}).get("data", pd.DataFrame())
                        if not data.empty:
                            id_dict = underlying.get("id", {})
                            name = id_dict["list"][id_dict["value"]]
                            childSubWindow = {
                                "title": "%s的当日合约",
                                "type": "option_contract_table",
                                "table_name": "%date%",
                                "where": "",
                                "select": id,
                                "hidden_columns": [],
                                "index_column": [],
                                "childSubWindow": {},
                            }
                            hidden_columns = ['total_turnover',
                                              'limit_up',
                                              'limit_down',
                                              'settlement',
                                              'prev_settlement',
                                              'discount_rate',
                                              'acc_net_value',
                                              'unit_net_value',
                                              'date',
                                              'open_interest',
                                              'iopv',
                                              'num_trades'
                                              ]

                            GridView(self.parent, name, data, id=name,
                                                   hidden_columns=hidden_columns,
                                                   index_column='date',
                                                   childSubWindow=childSubWindow,
                                                   type="option_underlying")
                        current_item = node

                        groups = underlying.get("groups", [])
                        for group in groups:
                            node = QTreeWidgetItem(current_item)
                            node.setText(0, group["name"])
                            node.setCheckState(0, Qt.Unchecked)
                            node.setIcon(0, QtGui.QIcon("../icon/group.png"))
                            node.setWhatsThis(0, "option_group")
                            node.setExpanded(True)
                            current_item = node
                            contracts = group.get("contracts")
                            for contract in contracts:
                                node = QTreeWidgetItem(current_item)
                                node.setText(0, contract["name"])
                                node.setCheckState(0, Qt.Unchecked)
                                node.setWhatsThis(0, "option_contract")
                                node.setExpanded(True)
                                current_item = node

    def onBackTestTreeDoubleClicked(self, item, column):
        self.setting_show(item, column)

    def onBackTestTreeRightClicked(self):
        menu = QMenu(self.backtest_tree)
        if self.backtest_tree.currentItem().whatsThis(0) == "option":
            #
            menu.addAction(self.add_option_underlying)
        else:
            whats_this = self.backtest_tree.currentItem().whatsThis(0)
            if whats_this == "option_underlying":
                menu.addAction(self.add_option_group)
                # menu.addAction(self.add_option_contract)
                menu.addAction(self.delete_backtest_tree_item)
            elif whats_this == "option_group":
                menu.addAction(self.add_option_contract)
                menu.addAction(self.delete_backtest_tree_item)
            elif whats_this == "option_contract":
                menu.addAction(self.delete_backtest_tree_item)
            else:
                menu.addAction(self.no_support)
        menu.popup(QtGui.QCursor.pos())

    def onDeleteBackTestTreeItem(self):
        current_item = self.backtest_tree.currentItem()
        parent_item = current_item.parent()
        grand_parent_item = parent_item.parent()
        whats_this = current_item.whatsThis(0)
        parent_whats_this = parent_item.whatsThis(0)
        parent_item_text = parent_item.text(0)
        current_item_text = current_item.text(0)

        index = parent_item.indexOfChild(current_item)
        if whats_this == "option_group":
            for underlying in self.config["options"]["underlyings"]:
                if underlying.get("name") == parent_item_text:
                    groups = underlying.get("groups")
                    for group in groups:
                        if group.get("name") == current_item_text:
                            groups.remove(group)
        elif whats_this == "option_contract":
            #两种情况需要处理
            if parent_whats_this == "option_underlying":
                for underlying in self.config["options"]["underlyings"]:
                    if underlying.get("name") == parent_item_text:
                        contracts = underlying.get("contracts")
                        for contract in contracts:
                            if contract.get("name") == current_item_text:
                                contracts.remove(contract)
            elif parent_whats_this == "option_group":
                for underlying in self.config["options"]["underlyings"]:
                    if underlying.get("name") == grand_parent_item.text(0):
                        groups = underlying.get("groups")
                        for group in groups:
                            if group.get("name") == parent_item_text:
                                contracts = group.get("contracts")
                                for contract in contracts:
                                    if contract.get("name") == current_item_text:
                                        contracts.remove(contract)
        elif whats_this == "option_underlying":
            underlyings = self.config["options"]["underlyings"]
            for underlying in underlyings:
                if underlying.get("name") == current_item_text:
                    underlyings.remove(underlying)
        parent_item.takeChild(index)
        return

    def setting_show(self, item, column):

        while self.group_box_widgets:
            for i in self.group_box_widgets:
                i.hide()
                self.group_box_layout.removeWidget(i)
                self.group_box_widgets.remove(i)

        self.current_node = {}
        text = item.text(column)
        whats_this = item.whatsThis(column)
        if whats_this == "option":
            bt_type = "backtest_option"
            title = "期权设置"
            load_file = "backtest_option.ui"
            current_node = self.config["options"]
            self.current_node = current_node
        elif whats_this == "option_underlying":
            title = "标的 %s 的设置" % text
            load_file = "backtest_option_underlying.ui"
            bt_type = "backtest_option_underlying"
            current_node = [i for i in self.config["options"]["underlyings"] if i["name"] == text][0]
            self.current_node = current_node
        elif whats_this == "option_group":
            title = "期权组 %s 的设置" % text
            load_file = "backtest_option_group.ui"
            bt_type = "backtest_option_group"
            parent_item = item.parent()
            parent_item_text = parent_item.text(0)
            underlying_node = [i for i in self.config["options"]["underlyings"] if i["name"] == parent_item_text][0]
            current_node = [i for i in underlying_node["groups"] if i["name"] == text][0]
            self.current_node = current_node
        elif whats_this == "option_contract":
            title = "期权合约 %s 的设置" % text
            load_file = "backtest_option_contract.ui"
            bt_type = "backtest_option_contract"
            parent_item = item.parent()
            parent_item_text = parent_item.text(0)
            parent_item_whats_this = parent_item.whatsThis(column)
            if parent_item_whats_this == "option_group":
                grand_parent_item = parent_item.parent()
                grand_parent_item_text = grand_parent_item.text(0)
                underlying_node = \
                [i for i in self.config["options"]["underlyings"] if i["name"] == grand_parent_item_text][0]
                group_node = [i for i in underlying_node["groups"] if i["name"] == parent_item_text][0]
                current_node = [i for i in group_node["contracts"] if i["name"] == text][0]
                self.current_node = current_node
            elif parent_item_whats_this == "option_underlying":
                underlying_node = [i for i in self.config["options"]["underlyings"] if i["name"] == parent_item_text][0]
                current_node = [i for i in underlying_node["contracts"] if i["name"] == text][0]
                self.current_node = current_node
        # elif whats_this == "strategy":
        #     title = "策略基本设置"
        #     load_file = "strategy.ui"
        #     bt_type = "backtest_strategy"
        else:
            return

        loader = QUiLoader()
        setting_widget = loader.load(load_file)

        self.group_box.setTitle(title)
        self.group_box_layout.addWidget(setting_widget)
        self.group_box_widgets.append(setting_widget)

        # 连接各组件信号和展示数据
        if whats_this == "option":
            ratio = setting_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(self.current_node["ratio"]["value"])
            ratio.valueChanged.connect(lambda event: self.onRatioChanged(event))
        elif whats_this == "option_underlying":
            ratio = setting_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(self.current_node["ratio"]["value"])
            setting_widget.findChild(QSpinBox, "ratio").valueChanged.connect(lambda event: self.onRatioChanged(event))

            underlying_list = setting_widget.findChild(QComboBox, "underlying_list")
            underlying_list.addItems(self.current_node["id"]["list"])
            underlying_list.currentIndexChanged.connect(lambda event: self.onUnderlyingListChanged(event))
            # underlying_list.setCurrentIndex(0)
            signal_list = setting_widget.findChild(QComboBox, "signal_list")
            # signal_list.setCurrentIndex(current_node["signal"]["value"])
            ids = self.current_node["id"]["list"]
            if ids == []:
                self.parent.messageBox("没有数据")
                return
            _sub_window = self.parent.getSubWindowByAttribute("btId", ids[0])
            if _sub_window is None:
                self.parent.messageBox("没有找到标的")
                return

            underlying_list.setCurrentIndex(self.current_node["id"]["value"])

            columns = _sub_window.btData.columns
            signal_column = [i for i in columns if i.startswith("signal")]
            self.current_node["signal"]["list"] = signal_column
            signal_list.addItems(signal_column)
            signal_list.setCurrentIndex(self.current_node["signal"]["value"])
            signal_list.currentIndexChanged.connect(lambda event: self.onSignalChanged(event))

            side = setting_widget.findChild(QComboBox, "side")
            side.setCurrentIndex(self.current_node["option_side"]["value"])
            side.currentIndexChanged.connect(lambda event: self.onOptionSideChanged(event))

            volume = setting_widget.findChild(QSpinBox, "volume")
            volume.setValue(self.current_node["volume"]["value"])
            volume.valueChanged.connect(lambda event: self.onVolumeChanged(event))

        elif whats_this == "option_group":

            ratio = setting_widget.findChild(QSpinBox, "ratio")
            ratio.setValue(self.current_node["ratio"]["value"])
            setting_widget.findChild(QSpinBox, "ratio").valueChanged.connect(lambda event: self.onRatioChanged(event))

        elif whats_this == "option_contract":
            contract_type = setting_widget.findChild(QComboBox, "contract_type")
            contract_type.setCurrentIndex(self.current_node["option_type"]["value"])
            contract_type.currentIndexChanged.connect(lambda event: self.onOptionContractTypeChanged(event))

            option_side = setting_widget.findChild(QComboBox, "option_side")
            option_side.setCurrentIndex(self.current_node["option_side"]["value"])
            option_side.currentIndexChanged.connect(lambda event: self.onOptionSideChanged(event))

            close_strategy = setting_widget.findChild(QComboBox, "close_strategy")
            close_strategy.setCurrentIndex(self.current_node["close_method"]["value"])
            close_strategy.currentIndexChanged.connect(lambda event: self.onCloseMethodChanged(event))

            change_feq = setting_widget.findChild(QComboBox, "change_feq")
            change_feq.setCurrentIndex(self.current_node["change_feq"]["value"])
            change_feq.currentIndexChanged.connect(lambda event: self.onChangeFeqChanged(event))

            move_condition = setting_widget.findChild(QComboBox, "move_condition")
            move_condition.setCurrentIndex(self.current_node["change_condition"]["value"])
            move_condition.currentIndexChanged.connect(lambda event: self.onChangeConditionChanged(event))

            interval = setting_widget.findChild(QComboBox, "interval")
            interval.setCurrentIndex(self.current_node["month_interval"]["value"])
            interval.currentIndexChanged.connect(lambda event: self.onMonthIntervalChanged(event))

            strike_interval = setting_widget.findChild(QComboBox, "strike_interval")
            strike_interval.setCurrentIndex(self.current_node["strike_interval"]["value"])
            strike_interval.currentIndexChanged.connect(lambda event: self.onStrikeIntervalChanged(event))

            smart_match = setting_widget.findChild(QComboBox, "smart_match")
            smart_match.setCurrentIndex(self.current_node["smart_selection"]["value"])
            smart_match.currentIndexChanged.connect(lambda event: self.onSmartSelectionChanged(event))

            volume = setting_widget.findChild(QSpinBox, "volume")
            volume.setValue(self.current_node["volume"]["value"])
            volume.valueChanged.connect(lambda event: self.onVolumeChanged(event))

            deposit_ratio = setting_widget.findChild(QDoubleSpinBox, "deposit_ratio")
            deposit_ratio.setValue(self.current_node["deposit_coefficient"]["value"])
            deposit_ratio.valueChanged.connect(lambda event: self.onDepositCoefficient(event))

            delta = setting_widget.findChild(QDoubleSpinBox, "delta")
            delta.setValue(self.current_node["delta"]["value"])
            delta.valueChanged.connect(lambda event: self.onDeltaChanged(event))

            gamma = setting_widget.findChild(QDoubleSpinBox, "gamma")
            gamma.setValue(self.current_node["gamma"]["value"])
            gamma.valueChanged.connect(lambda event: self.onGammaChanged(event))

            theta = setting_widget.findChild(QDoubleSpinBox, "theta")
            theta.setValue(self.current_node["theta"]["value"])
            theta.valueChanged.connect(lambda event: self.onThetaChanged(event))

            vega = setting_widget.findChild(QDoubleSpinBox, "vega")
            vega.setValue(self.current_node["vega"]["value"])
            vega.valueChanged.connect(lambda event: self.onVegaChanged(event))

            rho = setting_widget.findChild(QDoubleSpinBox, "rho")
            rho.setValue(self.current_node["rho"]["value"])
            rho.valueChanged.connect(lambda event: self.onRhoChanged(event))

            ivix = setting_widget.findChild(QDoubleSpinBox, "ivix")
            ivix.setValue(self.current_node["ivix"]["value"])
            ivix.valueChanged.connect(lambda event: self.onIvixChanged(event))

        # elif whats_this == "strategy":
        #     account_folder = os.path.normpath(os.path.join(ROOT, "accounts"))
        #     account_files = [os.path.splitext(i)[0] for i in os.listdir(account_folder) if
        #                      os.path.splitext(i)[-1] == ".bt"]
        #     account_list = sub_window_widget.findChild(QComboBox, "account")
        #     account_list.addItems(account_files)
        #     account_list.currentTextChanged.connect(lambda event:self.onBackTestRunAccountChanged(event))
        #
        #     open_type_list = sub_window_widget.findChild(QComboBox, "open_type")
        #     open_type_list.currentIndexChanged.connect(lambda event: self.onBackTestOpenTypeChanged(event))
        #
        #     table_view = sub_window_widget.findChild(QTableWidget)
        #     self.initBacktestAccountTable(table_view, account_files[0])


    def onOptionContractTypeChanged(self, index):
        current_node = self.current_node
        current_node["option_type"]["value"] = index

    def onOptionSideChanged(self, index):
        current_node = self.current_node
        current_node["option_side"]["value"] = index

    def onCloseMethodChanged(self, index):
        current_node = self.current_node
        current_node["close_method"]["value"] = index

    def onChangeFeqChanged(self, index):
        current_node = self.current_node
        current_node["change_feq"]["value"] = index

    def onChangeConditionChanged(self, index):
        current_node = self.current_node
        current_node["change_condition"]["value"] = index

    def onMonthIntervalChanged(self, index):
        current_node = self.current_node
        current_node["month_interval"]["value"] = index

    def onStrikeIntervalChanged(self, index):
        current_node = self.current_node
        current_node["strike_interval"]["value"] = index

    def onSmartSelectionChanged(self, index):
        current_node = self.current_node
        current_node["smart_selection"]["value"] = index

    def onDepositCoefficient(self, value):
        current_node = self.current_node
        current_node["deposit_coefficient"]["value"] = value

    def onDeltaChanged(self, value):
        current_node = self.current_node
        current_node["delta"]["value"] = value

    def onGammaChanged(self, value):
        current_node = self.current_node
        current_node["gamma"]["value"] = value

    def onThetaChanged(self, value):
        current_node = self.current_node
        current_node["theta"]["value"] = value

    def onVegaChanged(self, value):
        current_node = self.current_node
        current_node["vega"]["value"] = value

    def onRhoChanged(self, value):
        current_node = self.current_node
        current_node["rho"]["value"] = value

    def onIvixChanged(self, value):
        current_node = self.current_node
        current_node["ivix"]["value"] = value

    def onRatioChanged(self, value):
        current_node = self.current_node
        current_node["ratio"]["value"] = value

    def onUnderlyingListChanged(self, index):
        current_node = self.current_node
        current_node["id"]["value"] = index
        text = current_node["id"]["list"][index]
        signal_list = self.mdi_area.currentSubWindow().findChild(QComboBox, "signal_list")
        signal_list.clear()
        sub_window = self.parent.getSubWindowByAttribute("btId", text)
        data = sub_window.btData
        signal_list.addItems([i for i in data.columns if i.startswith("signal")])

    def onVolumeChanged(self, value):
        current_node = self.current_node
        current_node["volume"]["value"] = value

    def onSignalChanged(self, index):
        current_node = self.current_node
        current_node["signal"]["value"] = index

    def onAddOptionUnderlying(self):

        text, ok = QInputDialog.getText(self.backtest, "请输入期权标的名称","名称", QLineEdit.Normal)
        if ok and text:
            node = QTreeWidgetItem(self.backtest_tree.currentItem())
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_underlying")
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            ids = [i.btId for i in self.mdi_area.subWindowList() if hasattr(i, "btType") and i.btType in ["option_underlying", "excel", "csv"]]
            group_dict = {
                "name": text,
                "enable": 0,
                "ratio": {
                    "type": "int",
                    "value": 0,
                },
                "id": {
                    "type": "list",
                    "value": 0,
                    "list": ids,
                    "data": getattr(self.parent.getSubWindowByAttribute("btId", ids[0]), "btData")
                },
                "signal": {
                    "type": "list",
                    "value": 0,
                    "list": []
                },
                "option_side": {
                    "type": "list",
                    "value": 0,
                    "list": [u"买入"]
                },
                "volume": {
                    "type": "int",
                    "value": 0,
                },
                "groups": [],
                "contracts":[],
            }
            self.config["options"]["underlyings"].append(group_dict)

    def onAddOptionGroup(self):
        text, ok = QInputDialog.getText(self.backtest, "请输入期权组名称", "名称", QLineEdit.Normal)
        current_item = self.backtest_tree.currentItem()
        # parent_item = current_item.parent()
        current_item_text = current_item.text(0)
        # parent_item_text = parent_item.text(0)
        if ok and text:
            node = QTreeWidgetItem(current_item)
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_group")
            node.setIcon(0, QtGui.QIcon("../icon/group.png"))
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            group_dict = {
                "name": text,
                "enable": 1,
                "contracts": [],
                "signal": {
                    "type": "list",
                    "value": 0,
                    "list": []
                },
                "ratio": {
                    "type": "float",
                    "value": 0,
                },
            }
            for underlying in self.config["options"]["underlyings"]:
                if underlying.get("name") == current_item_text:
                    underlying["groups"].append(group_dict)

    def onAddOptionContract(self):
        text, ok = QInputDialog.getText(self.backtest, "请输入期权合约名称", "名称", QLineEdit.Normal)
        current_item = self.backtest_tree.currentItem()
        current_item_whats_this = current_item.whatsThis(0)
        current_item_text = current_item.text(0)
        parent_item = current_item.parent()
        parent_whats_this = parent_item.whatsThis(0)
        parent_item_text = parent_item.text(0)
        if ok and text:
            node = QTreeWidgetItem(current_item)
            node.setText(0, text)
            node.setCheckState(0, Qt.Unchecked)
            node.setWhatsThis(0, "option_contract")
            node.setIcon(0, QtGui.QIcon("../icon/contract.png"))
            self.backtest_tree.expandItem(self.backtest_tree.currentItem())
            filter_dict = {
                "name": text,
                "enable": 1,
                "open_status": False,
                "ids":[],
                "option_type": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_TYPE,
                },
                "option_side": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_SIDE,
                },
                "close_method": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CLOSE_METHOD,
                },
                "change_feq": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CHANGE_FEQ,
                },
                "change_condition": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_CHANGE_CONDITION,
                },
                "month_interval": {
                    "type": "list",
                    "value": 0,
                    "list": [setting.OPTION_INTERVAL[i] for i in range(len(setting.OPTION_INTERVAL)) if i != 2],
                },
                "strike_interval": {
                    "type": "list",
                    "value": 0,
                    "list": setting.OPTION_STRIKE_INTERVAL,
                },
                "smart_selection": {
                    "type": "list",
                    "value": 1,
                    "list": setting.OPTION_SMART_SELECTION,
                },
                "type": "option",
                "volume": {
                    "type": "int",
                    "value": 0
                },
                "deposit_coefficient": {
                    "type": "int",
                    "value": 1,
                },
                "delta": {
                    "type": "int",
                    "value": 0,
                },
                "gamma": {
                    "type": "int",
                    "value": 0,
                },
                "theta": {
                    "type": "int",
                    "value": 0,
                },
                "vega": {
                    "type": "int",
                    "value": 0,
                },
                "rho": {
                    "type": "int",
                    "value": 0,
                },
                "ivix": {
                    "type": "float",
                    "value": 0
                }
            }
            for underlying in self.config["options"]["underlyings"]:
                underlying_name = underlying.get("name")
                if current_item_whats_this == "option_group":
                    if underlying_name == parent_item_text:
                        groups = underlying.get("groups")
                        for group in groups:
                            if group.get("name") ==  current_item_text:
                                group["contracts"].append(filter_dict)
                elif current_item_whats_this == "option_underlying":
                    if underlying_name == current_item_text:
                        underlying.get("contracts").append(filter_dict)