
import datetime

OPEN_TYPE = [u"固定数量", u"固定金额", u"资金比例"]
CLOSE_TYPE = [u"全部平仓", u"分批平仓"]
OPTION_FILTER = [u"期权类型", u"数量", u"开仓方向", u"平仓策略",
                 u"移仓频率", u"移仓条件", u"到期时间", u"行权价", u"智能匹配", u"保证金系数",
                 u"Delta", u"Gamma", u"Theta", u"Vega"]
ACTION = [u"关闭", u"打开"]
SIDE = [u"买入开仓", u"卖出开仓"]
TYPE = [u"比例", u"数量"]
OPTION_TYPE = [u"认购期权", u"认沽期权"]
OPTION_SIDE = [u"买入开仓", u"卖出开仓"]
OPTION_CLOSE_METHOD = [u"交易信号平仓", u"到期日平仓"]
OPTION_CHANGE_CONDITION = [u"收盘价", u"开盘价"]
OPTION_CHANGE_FEQ = [u"到期日", u"1天", u"2天", u"3天"]
OPTION_INTERVAL = [u"当月", u"下月", u"下季", u"隔季"]
OPTION_STRIKE_INTERVAL = [u"", u"低1个价位", u"低2个价位", u"低3个价位",
                        u"低4个价位", u"低5个价位",u"低6个价位",
                        u"低7个价位", u"低8个价位",u"低9个价位",u"平值",
                        u"高1个价位", u"高2个价位", u"高3个价位",
                        u"高4个价位", u"高5个价位", u"高6个价位",
                        u"高7个价位", u"高8个价位", u"高9个价位"]
OPTION_SMART_SELECTION = [u"否", u"是"]
PERFORMANCE_LEVEL = [u"斗之气凝聚", u"斗者", u"斗师",
                        u"大斗师", u"斗灵", u"斗王",
                        u"斗皇", u"斗宗", u"斗尊",
                     u"斗圣", u"斗帝"]
STRATEGY_EXTENSION = "*.bt"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

ACCOUNT = {
    "investment":{
                "type": "int",
                "value": 500000
            },
            "commission_rate":{
                "type": "float",
                "value": 0.001
            },
            "option_commission_rate":{
                "type": "float",
                "value": 12.3
            },
            "profit_ratio":{
                "type":"float",
                "value": 0.04
            },
            "slide_point":{
                "type": "int",
                "value": 1
            },
            "currency":{
                "type": "list",
                "value": "RMB"
            },
            "stop_profit":{
                "type":"float",
                "value":0
            },
            "stop_loss":{
                "type":"float",
                "value":0
            },
    "position":{

    }
}

SETTINGS = {
        "manual_order":[],

        "open_type":{
            "value":0,
            "type":list,
            "list":OPEN_TYPE
        },
        "close_type":{
            "value":0,
            "type":list,
            "list":CLOSE_TYPE
        },
        "options":{
            "enable": 0,
            "ratio":{
                "type": "float",
                "value": 0,
            },
            "underlyings":[],
        },
        "stock":{
            "enable": 0,
            "ratio":{
                "type": "float",
                "value": 0
            },
            "pool":{
                "type": "list",
                "value": [],
            },
            "groups":{},
        },
        "report":{},

                        }

#订单状态
OrderStatus_New = 1                        #已报
OrderStatus_PartiallyFilled = 2            #部成
OrderStatus_Filled = 3                     #已成
OrderStatus_DoneForDay = 4                 #
OrderStatus_Canceled = 5                   #已撤
OrderStatus_PendingCancel = 6              #待撤
OrderStatus_Stopped = 7                    #停止
OrderStatus_Rejected = 8                   #已拒绝
OrderStatus_Suspended = 9                  #挂起
OrderStatus_PendingNew = 10                #待报
OrderStatus_Calculated = 11                #计算
OrderStatus_Expired = 12                   #已过期
OrderStatus_AcceptedForBidding = 13        #接受竞价
OrderStatus_PendingReplace = 14             #待修改

#订单拒绝原因
OrderRejectReason_UnknownReason = 1                #未知原因
OrderRejectReason_RiskRuleCheckFailed = 2          #不符合风控规则
OrderRejectReason_NoEnoughCash = 3                 #资金不足
OrderRejectReason_NoEnoughPosition = 4             #仓位不足
OrderRejectReason_IllegalStrategyID = 5            #非法策略ID
OrderRejectReason_IllegalSymbol = 6                #非法交易标的
OrderRejectReason_IllegalVolume = 7                #非法委托量
OrderRejectReason_IllegalPrice = 8                 #非法委托价
OrderRejectReason_NoMatchedTradingChannel = 9      #没有匹配的交易通道
OrderRejectReason_AccountForbidTrading = 10        #交易账号被禁止交易
OrderRejectReason_TradingChannelNotConnected = 11  #交易通道未连接
OrderRejectReason_StrategyForbidTrading = 12       #策略不允许交易
OrderRejectReason_NotInTradingSession = 13          #非交易时段
CancelOrderRejectReason_OrderFinalized = 101        #订单已是最终状态
CancelOrderRejectReason_UnknownOrder = 102          #未知订单
CancelOrderRejectReason_BrokerOption = 103          #柜台拒绝
CancelOrderRejectReason_AlreadyInPendingCancel = 104        #重复撤单

#订单方向
OrderSide_Bid = 1  ## 多方向
OrderSide_Ask = 2  ## 空方向

#订单类型
OrderType_LMT = 0,       ## 限价委托(limit)
OrderType_BOC = 1,       ## 对方最优价格(best of counterparty)
OrderType_BOP = 2,       ## 己方最优价格(best of party)
OrderType_B5TC = 3,      ## 最优五档剩余撤销(best 5 then cancel)
OrderType_B5TL = 4,      ## 最优五档剩余转限价(best 5 then limit)
OrderType_IOC = 5,       ## 即时成交剩余撤销(immediately or cancel)
OrderType_FOK = 6,       ## 即时全额成交或撤销(fill or kill)
OrderType_AON = 7,       ## 全额成交或不成交(all or none)
OrderType_MTL = 8,       ## 市价剩余转限价(market then limit)
OrderType_EXE = 9        ## 期权行权(option execute)
#订单执行回报类型
ExecType_New = 1                ## 交易所已接受订单
ExecType_DoneForDay = 4
ExecType_Canceled = 5           ## 已撤
ExecType_PendingCancel = 6      ## 待撤
ExecType_Stopped = 7            ## 已停
ExecType_Rejected = 8           ## 已拒绝
ExecType_Suspended = 9          ## 暂停
ExecType_PendingNew = 10        ## 待接受
ExecType_Calculated = 11        ## 已折算
ExecType_Expired = 12           ## 过期
ExecType_Restated = 13          ## 重置
ExecType_PendingReplace = 14    ## 待修改
ExecType_Trade = 15             ## 交易
ExecType_TradeCorrect = 16      ## 交易更正
ExecType_TradeCancel = 17       ## 交易取消
ExecType_OrderStatus = 18       ## 更新订单状态
ExecType_CancelRejected = 19    ## 撤单被拒绝

#开平仓类型
PositionEffect_Open = 1             ## 开仓
PositionEffect_Close = 2            ## 平仓
PositionEffect_CloseToday = 3       ## 平今仓
PositionEffect_CloseYesterday = 4   ## 平昨仓

#委托订单
class Order(object):

    def __init__(self):
        self.strategy_id = ''                 ## 策略ID
        self.account_id = ''                  ## 交易账号

        # self.cl_ord_id = ''                   ## 客户端订单ID
        # self.order_id = ''                    ## 柜台订单ID
        # self.ex_ord_id = ''                   ## 交易所订单ID

        # self.exchange = ''                    ## 交易所代码
        self.sec_id = ''                      ## 证券ID

        self.position_effect = 0              ## 开平标志
        self.side = 0                         ## 买卖方向
        self.order_type = 0                   ## 订单类型
        self.order_src = 0                    ## 订单来源
        self.status = 0                       ## 订单状
        self.ord_rej_reason = 0               ## 订单拒绝原因
        self.ord_rej_reason_detail = ''       ## 订单拒绝原因描述

        self.price = 0.0                      ## 委托价
        self.stop_price = 0.0                 ## 止损价
        self.volume = 0.0                     ## 委托量
        self.filled_volume = 0.0              ## 已成交量
        self.filled_vwap = 0.0                ## 已成交均价
        self.filled_amount = 0.0              ## 已成交额

        self.sending_time = 0.0               ## 委托下单时间
        # self.transact_time = 0.0              ## 最新一次成交时间

        # self.expiration_date = None            ##过期时间
        self.deposit_coefficient = 1.0
        self.change_feq = None
        self.short_name = ""
        self.close_method = 0
        self.var_sec_id = ""
        self.var_price = 0
        self.contract_type = 0
        self.expiration_date = ""
        self.strike_price = 0
        self.exercise_type = ""             #美式期权/欧式期权

#委托执行回报
class ExecRpt(object):

    def __init__(self):
        self.strategy_id = ''                 ## 策略ID

        self.cl_ord_id = ''                   ## 客户端订单ID
        self.order_id = ''                    ## 交易所订单ID
        self.exec_id = ''                     ## 订单执行回报ID

        self.exchange = ''                    ## 交易所代码
        self.sec_id = ''                      ## 证券ID

        self.position_effect = 0              ## 开平标志
        self.side = 0                         ## 买卖方向
        self.ord_rej_reason = 0               ## 订单拒绝原因
        self.ord_rej_reason_detail = ''       ## 订单拒绝原因描述
        self.exec_type = 0                    ## 订单执行回报类型

        self.price = 0.0                      ## 成交价
        self.volume = 0.0                     ## 成交量
        self.amount = 0.0                     ## 成交额

        self.transact_time = 0.0              ## 交易时间

#资金
class Cash(object):

    def __init__(self):
        # self.strategy_id = ''           ## 策略ID
        # self.account_id = ''            ## 账户id
        self.currency = "rmb"               ## 币种
        self.income = 0.0
        self.cost = 0.0
        self.nav = 0.0                  ## 资金余额
        self.fpnl = 0.0                 ## 浮动收益
        self.pnl = 0.0                  ## 净收益
        # self.profit_ratio = 0.0         ## 收益率
        self.frozen = 0.0               ## 持仓冻结金额
        # self.order_frozen = 0.0         ## 挂单冻结金额
        self.available = 0.0            ## 可用资金

        self.cum_inout = 0.0            ## 累计出入金
        # self.cum_trade = 0.0            ## 累计交易额
        self.cum_pnl = 0.0              ## 累计收益
        self.cum_commission = 0.0       ## 累计手续费
        self.date = None

        # self.last_trade = 0.0           ## 最新一笔交易额
        # self.last_pnl = 0.0             ## 最新一笔交易收益
        # self.last_commission = 0.0      ## 最新一笔交易手续费
        # self.last_inout = 0.0           ## 最新一次出入金
        # self.change_reason = 0          ## 变动原因

        # self.transact_time = 0.0        ## 交易时间

#持仓
class Position(object):

    def __init__(self):
        # self.strategy_id = ''           ## 策略ID
        self.account_id = ''            ## 账户id
        # self.exchange = ''              ## 交易所代码
        self.sec_id = ''                ## 证券ID
        self.side = 0                   ## 买卖方向
        self.volume = 0.0               ## 持仓量
        # self.volume_today = 0.0         ## 今仓量
        self.amount = 0.0               ## 持仓额
        self.vwap = 0.0                 ## 持仓均价

        self.price = 0.0                ## 当前行情价格
        self.fpnl = 0.0                 ## 持仓浮动盈亏
        self.pnl = 0.0
        self.income = 0.0
        self.cost = 0.0                 ## 持仓成本
        self.cum_cost = 0.0
        # self.order_frozen = 0.0         ## 挂单冻结仓位
        # self.available = 0.0            ## 可平仓位
        # self.order_frozen_today = 0.0   ## 挂单冻结今仓
        self.available = 0.0
        self.available_today = 0.0      ## 可平今仓
        # self.last_price = 0.0           ## 上一笔成交价
        # self.last_volume = 0.0          ## 上一笔成交量
        self.init_time = None            ## 初始建仓时间
        self.transact_time = None        ## 上一仓位变更时间
        self.close_time = None           ##平仓时间

        self.date = None
        self.deposit = 0
        self.commission = 0
        self.deposit_cost = 0
        self.deposit_coefficient = 0
        self.status = u"正常"
        self.slide_cost = 0
        self.short_name = ""

#绩效
class Performance(object):

    def __init__(self):
        # self.strategy_id = ''                       ## 策略ID
        # self.account_id = ''                        ## 账号ID
        self._max_nav = 0.0
        self.nav = 0.0                              ## 净值(cum_inout + cum_pnl + fpnl - cum_commission)
        self.pnl = 0.0                              ## 净收益(nav-cum_inout)
        self.profit_ratio = 0.0                     ## 收益率(pnl/cum_inout)

        self.sharp_ratio = 0.0                      ## 夏普比率
        self.risk_ratio = 0.0                       ## 风险比率
        self.trade_count = 0                        ## 交易次数
        self.win_count = 0                          ## 盈利次数
        self.lose_count = 0                         ## 亏损次数
        self.win_ratio = 0.0                        ## 胜率
        self.max_profit = 0.0                       ## 最大收益
        self.min_profit = 0.0                 ## 最小收益
        self.max_loss = 0.0                         ##
        self.min_loss = 0.0              ##
        self.max_single_trade_profit = 0.0          ## 最大单次交易收益
        self.min_single_trade_profit = 0.0          ## 最小单次交易收益
        self.daily_max_single_trade_profit = 0.0    ## 今日最大单次交易收益
        self.daily_min_single_trade_profit = 0.0    ## 今日最小单次交易收益
        self.max_position_value = 0.0               ## 最大持仓市值或权益
        self.min_position_value = 0.0               ## 最小持仓市值或权益
        self.max_drawdown = 0.0                     ## 最大回撤
        self._max_drawdown = 0.0
        self.daily_pnl = 0.0                        ## 今日收益
        self.daily_return = 0.0                     ## 今日收益率
        self.annual_return = 0.0                    ## 年化收益率

        self.transact_time = 0.0                    ## 指标计算时间
        self.total_win = 0.0                        ##总盈利
        self.total_loss = 0.0                       ##总亏损
        self.average_win = 0.0                      ##平均盈利
        self.average_loss = 0.0                     ##平均亏损
        self.win_loss = 0.0                         ##盈亏比